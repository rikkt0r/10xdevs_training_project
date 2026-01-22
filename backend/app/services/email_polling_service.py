"""
Email polling service for IMAP inbox monitoring and email routing.
"""
import logging
import hashlib
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timezone, timedelta
import aioimaplib
from email import message_from_bytes
from email.header import decode_header
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import decrypt_data, generate_unique_ticket_uuid
from app.models.email_inbox import EmailInbox
from app.models.processed_email import ProcessedEmail
from app.models.board import Board
from app.models.board_keyword import BoardKeyword
from app.models.ticket import Ticket
from app.models.standby_queue_item import StandbyQueueItem
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class EmailPollingService:
    """Service for polling IMAP inboxes and routing emails to tickets."""

    async def poll_inbox(self, inbox_id: int) -> None:
        """
        Main polling function - async job executed by APScheduler.

        This is the entry point called by the scheduler every N minutes.

        Process:
        1. Get inbox config from database
        2. Connect to IMAP
        3. Fetch unread emails
        4. For each email:
           a. Parse email
           b. Check for duplicates
           c. Route to board or standby queue
           d. Mark as processed
           e. Mark email as read on IMAP server
        5. Update last_polled_at timestamp
        6. Close IMAP connection

        Args:
            inbox_id: Inbox ID to poll
        """
        db = SessionLocal()
        imap_client = None

        try:
            # Get inbox configuration
            inbox = db.query(EmailInbox).filter(EmailInbox.id == inbox_id).first()

            if not inbox:
                logger.error(f"Inbox {inbox_id} not found")
                return

            if not inbox.is_active:
                logger.info(f"Inbox {inbox_id} is not active, skipping poll")
                return

            logger.info(f"Starting poll for inbox {inbox_id} ({inbox.name})")

            # Connect to IMAP
            try:
                imap_client = await self._connect_imap(inbox)
            except Exception as e:
                logger.error(f"Failed to connect to inbox {inbox_id}: {str(e)}")
                return

            # Fetch unread emails
            emails = await self._fetch_unread_emails(imap_client)

            if not emails:
                logger.info(f"No unread emails in inbox {inbox_id}")
            else:
                logger.info(f"Processing {len(emails)} emails from inbox {inbox_id}")

            # Process each email
            for msg_num, raw_email in emails:
                try:
                    # Parse email
                    parsed = self._parse_email(raw_email)
                    message_id = parsed['message_id']
                    sender = parsed['sender']
                    subject = parsed['subject']
                    body = parsed['body']

                    if not sender or not subject:
                        logger.warning(f"Skipping email with missing sender or subject")
                        continue

                    # Hash subject for duplicate detection
                    subject_hash = self._hash_subject(subject)

                    # Check for duplicates
                    if self._is_duplicate(db, inbox_id, sender, subject_hash):
                        logger.info(f"Skipping duplicate email from {sender}")
                        # Mark as read on server even if duplicate
                        await imap_client.store(msg_num, '+FLAGS', '\\Seen')
                        continue

                    # Route email to board or standby queue
                    ticket = await self._route_email(db, inbox, sender, subject, body)

                    # Mark as processed in database
                    self._mark_processed(db, inbox_id, message_id, sender, subject_hash)

                    # Mark as read on IMAP server
                    await imap_client.store(msg_num, '+FLAGS', '\\Seen')

                    if ticket:
                        logger.info(f"Successfully processed email into ticket {ticket.id}")
                    else:
                        logger.info(f"Email from {sender} sent to standby queue")

                except Exception as e:
                    logger.error(f"Error processing email in inbox {inbox_id}: {str(e)}")
                    # Continue processing other emails
                    continue

            # Update last_polled_at timestamp
            inbox.last_polled_at = datetime.now(timezone.utc)
            db.commit()

            logger.info(f"Completed poll for inbox {inbox_id}")

        except Exception as e:
            logger.error(f"Error polling inbox {inbox_id}: {str(e)}")
            db.rollback()
        finally:
            # Close IMAP connection
            if imap_client:
                try:
                    await imap_client.logout()
                except Exception:
                    pass

            # Close database session
            db.close()

    async def _connect_imap(self, inbox: EmailInbox) -> aioimaplib.IMAP4_SSL:
        """
        Establish IMAP connection with error handling.

        Args:
            inbox: EmailInbox instance with connection config

        Returns:
            Connected IMAP client

        Raises:
            Exception: If connection fails (logged, not propagated)
        """
        try:
            # Decrypt password
            password = decrypt_data(inbox.imap_password_encrypted)

            # Create IMAP client
            if inbox.imap_use_ssl:
                imap = aioimaplib.IMAP4_SSL(
                    host=inbox.imap_host,
                    port=inbox.imap_port
                )
            else:
                imap = aioimaplib.IMAP4(
                    host=inbox.imap_host,
                    port=inbox.imap_port
                )

            # Connect and login
            await imap.wait_hello_from_server()
            await imap.login(inbox.imap_username, password)

            logger.info(f"Connected to IMAP inbox {inbox.id} ({inbox.name})")
            return imap

        except Exception as e:
            logger.error(f"Failed to connect to IMAP inbox {inbox.id}: {str(e)}")
            raise

    async def _fetch_unread_emails(self, imap_client) -> List[Tuple[str, bytes]]:
        """
        Fetch unread emails from inbox.

        Returns:
            List of (message_id, raw_email_bytes) tuples
        """
        try:
            # Select INBOX folder
            await imap_client.select('INBOX')

            # Search for unread emails
            status, messages = await imap_client.search('UNSEEN')

            if status != 'OK':
                logger.error("Failed to search for unread emails")
                return []

            message_ids = messages[0].split()
            emails = []

            for msg_id in message_ids:
                # Fetch email
                status, data = await imap_client.fetch(msg_id, '(RFC822)')

                if status == 'OK':
                    raw_email = data[1]
                    emails.append((msg_id.decode(), raw_email))

            logger.info(f"Fetched {len(emails)} unread emails")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []

    def _parse_email(self, raw_email: bytes) -> Dict[str, str]:
        """
        Parse email to extract sender, subject, body.

        Returns:
            Dict with 'message_id', 'sender', 'subject', 'body'
        """
        try:
            msg = message_from_bytes(raw_email)

            # Extract message ID
            message_id = msg.get('Message-ID', '')

            # Extract sender
            sender = msg.get('From', '')
            # Parse email address from "Name <email@domain.com>" format
            if '<' in sender:
                sender = sender.split('<')[1].split('>')[0]

            # Extract subject
            subject = msg.get('Subject', '')
            # Decode if encoded
            decoded_subject = decode_header(subject)[0]
            if isinstance(decoded_subject[0], bytes):
                subject = decoded_subject[0].decode(
                    decoded_subject[1] or 'utf-8',
                    errors='replace'
                )
            else:
                subject = decoded_subject[0] or ''

            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()

                    # Prefer text/plain, fallback to text/html
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='replace')
                            break
                    elif content_type == "text/html" and not body:
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_body = payload.decode('utf-8', errors='replace')
                            body = self._strip_html(html_body)
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    content_type = msg.get_content_type()
                    text = payload.decode('utf-8', errors='replace')

                    if content_type == "text/html":
                        body = self._strip_html(text)
                    else:
                        body = text

            return {
                'message_id': message_id,
                'sender': sender.strip(),
                'subject': subject.strip(),
                'body': body.strip()
            }

        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return {
                'message_id': '',
                'sender': '',
                'subject': 'Failed to parse subject',
                'body': 'Failed to parse email body'
            }

    def _strip_html(self, html_content: str) -> str:
        """
        Strip HTML tags to get plain text.

        Args:
            html_content: HTML string

        Returns:
            Plain text with reasonable formatting
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())

        # Drop blank lines
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def _hash_subject(self, subject: str) -> str:
        """
        Hash subject for duplicate detection using SHA-256.

        Args:
            subject: Email subject

        Returns:
            Hex digest of SHA-256 hash
        """
        return hashlib.sha256(subject.encode('utf-8')).hexdigest()

    def _is_duplicate(self, db: Session, inbox_id: int, sender: str,
                      subject_hash: str) -> bool:
        """
        Check if email is duplicate within threshold.

        An email is a duplicate if:
        - Same inbox_id
        - Same sender_email
        - Same subject_hash (SHA-256 of subject)
        - Processed within DUPLICATE_EMAIL_THRESHOLD_MINUTES

        Args:
            db: Database session
            inbox_id: Inbox ID
            sender: Sender email
            subject_hash: SHA-256 hash of subject

        Returns:
            True if duplicate, False otherwise
        """
        threshold = datetime.now(timezone.utc) - timedelta(
            minutes=settings.DUPLICATE_EMAIL_THRESHOLD_MINUTES
        )

        existing = db.query(ProcessedEmail).filter(
            ProcessedEmail.inbox_id == inbox_id,
            ProcessedEmail.sender_email == sender,
            ProcessedEmail.subject_hash == subject_hash,
            ProcessedEmail.processed_at >= threshold
        ).first()

        if existing:
            logger.info(f"Duplicate email detected from {sender} with subject hash {subject_hash[:8]}...")
            return True

        return False

    async def _route_email(self, db: Session, inbox: EmailInbox,
                          sender: str, subject: str, body: str) -> Optional[Ticket]:
        """
        Route email to board using priority logic:
        1. Exclusive inbox assignment
        2. Keyword matching (only boards without exclusive inbox)
        3. Standby queue (no match)

        Args:
            db: Database session
            inbox: Source inbox
            sender: Email sender
            subject: Email subject
            body: Email body (plain text)

        Returns:
            Created Ticket or None if sent to standby queue
        """
        try:
            # Priority 1: Exclusive inbox assignment
            board = db.query(Board).filter(
                Board.exclusive_inbox_id == inbox.id,
                Board.is_archived == False
            ).first()

            if board:
                logger.info(f"Routing email to board {board.id} via exclusive inbox")
                ticket = await self._create_ticket(db, board, sender, subject, body, inbox)
                return ticket

            # Priority 2: Keyword matching
            # Only check boards without exclusive inbox (to avoid conflicts)
            keywords = db.query(BoardKeyword).join(Board).filter(
                Board.manager_id == inbox.manager_id,
                Board.exclusive_inbox_id == None,
                Board.is_archived == False
            ).all()

            # Case-insensitive keyword matching in subject
            subject_lower = subject.lower()
            for keyword_obj in keywords:
                if keyword_obj.keyword.lower() in subject_lower:
                    board = db.query(Board).filter(Board.id == keyword_obj.board_id).first()
                    if board:
                        logger.info(f"Routing email to board {board.id} via keyword '{keyword_obj.keyword}'")
                        ticket = await self._create_ticket(db, board, sender, subject, body, inbox)
                        return ticket

            # Priority 3: No match - send to standby queue
            logger.info(f"No board match for email from {sender}, sending to standby queue")
            self._create_standby_queue_item(
                db=db,
                manager_id=inbox.manager_id,
                sender=sender,
                subject=subject,
                body=body,
                failure_reason='no_keyword_match'
            )
            return None

        except Exception as e:
            logger.error(f"Error routing email: {str(e)}")
            # On routing error, send to standby queue
            self._create_standby_queue_item(
                db=db,
                manager_id=inbox.manager_id,
                sender=sender,
                subject=subject,
                body=body,
                failure_reason='no_board_match'
            )
            return None

    async def _create_ticket(self, db: Session, board: Board,
                            sender: str, subject: str, body: str,
                            inbox: EmailInbox) -> Ticket:
        """
        Create ticket and send confirmation email.

        Args:
            db: Database session
            board: Target board
            sender: Creator email
            subject: Email subject (becomes ticket title)
            body: Email body (becomes ticket description)
            inbox: Source inbox (for from_address in confirmation)

        Returns:
            Created Ticket instance

        Raises:
            Exception: If ticket creation fails
        """
        try:
            # Generate unique UUID
            unique_uuid = generate_unique_ticket_uuid(db)

            # Create ticket
            ticket = Ticket(
                uuid=unique_uuid,
                board_id=board.id,
                title=subject[:255],  # Truncate to field max length
                description=body[:6000],  # Truncate to field max length
                creator_email=sender,
                source="email",
                state="new"
            )

            db.add(ticket)
            db.commit()
            db.refresh(ticket)

            logger.info(f"Created ticket {ticket.id} from email")

            # Send confirmation email
            await email_service.send_ticket_confirmation_email(
                to_email=sender,
                ticket_uuid=str(ticket.uuid),
                ticket_title=ticket.title,
                ticket_description=ticket.description,
                board_name=board.name,
                from_email=inbox.from_address
            )

            logger.info(f"Sent confirmation email to {sender}")

            return ticket

        except Exception as e:
            logger.error(f"Failed to create ticket: {str(e)}")
            db.rollback()
            raise

    def _create_standby_queue_item(self, db: Session, manager_id: int,
                                   sender: str, subject: str, body: str,
                                   failure_reason: str) -> StandbyQueueItem:
        """
        Create standby queue item for unrouted emails.

        Args:
            db: Database session
            manager_id: Manager ID
            sender: Email sender
            subject: Email subject
            body: Email body
            failure_reason: Reason for queue placement

        Returns:
            Created StandbyQueueItem instance
        """
        item = StandbyQueueItem(
            manager_id=manager_id,
            email_subject=subject[:255],  # Truncate to field max length
            email_body=body,
            sender_email=sender,
            failure_reason=failure_reason,
            retry_count=0
        )

        db.add(item)
        db.commit()

        logger.info(f"Created standby queue item for {sender}")
        return item

    def _mark_processed(self, db: Session, inbox_id: int, message_id: str,
                       sender: str, subject_hash: str) -> ProcessedEmail:
        """
        Mark email as processed in database.

        Args:
            db: Database session
            inbox_id: Inbox ID
            message_id: Email Message-ID header
            sender: Sender email
            subject_hash: SHA-256 hash of subject

        Returns:
            Created ProcessedEmail instance
        """
        processed = ProcessedEmail(
            inbox_id=inbox_id,
            message_id=message_id[:255],  # Truncate to field max length
            sender_email=sender[:255],  # Truncate to field max length
            subject_hash=subject_hash
        )

        db.add(processed)
        db.commit()

        return processed


# Singleton instance
email_polling_service = EmailPollingService()


# Scheduler management functions
async def initialize_polling_jobs(scheduler: AsyncIOScheduler) -> None:
    """
    Initialize polling jobs for all active inboxes on startup.

    Called from FastAPI startup event.

    Args:
        scheduler: APScheduler instance
    """
    logger.info("Initializing email polling jobs")

    # Get database session
    db = SessionLocal()

    try:
        # Get all active inboxes
        inboxes = db.query(EmailInbox).filter(
            EmailInbox.is_active == True
        ).all()

        logger.info(f"Found {len(inboxes)} active inboxes")

        # Add job for each inbox
        for inbox in inboxes:
            await add_polling_job(scheduler, inbox.id, inbox.polling_interval)

        logger.info("Email polling jobs initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing polling jobs: {str(e)}")
    finally:
        db.close()


async def add_polling_job(scheduler: AsyncIOScheduler, inbox_id: int,
                         polling_interval: int) -> None:
    """
    Add or update polling job for specific inbox.

    Creates a new job or replaces existing job if polling_interval changed.

    Args:
        scheduler: APScheduler instance
        inbox_id: Inbox ID
        polling_interval: Polling interval in minutes (1, 5, or 15)
    """
    job_id = f"poll_inbox_{inbox_id}"

    # Remove existing job if present
    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)
        logger.info(f"Removed existing job {job_id}")

    # Add new job
    scheduler.add_job(
        func=email_polling_service.poll_inbox,
        trigger=IntervalTrigger(minutes=polling_interval),
        args=[inbox_id],
        id=job_id,
        name=f"Poll inbox {inbox_id} every {polling_interval} min",
        replace_existing=True,
        max_instances=1  # Prevent concurrent polling of same inbox
    )

    logger.info(f"Added polling job for inbox {inbox_id} (interval: {polling_interval} min)")


async def remove_polling_job(scheduler: AsyncIOScheduler, inbox_id: int) -> None:
    """
    Remove polling job for specific inbox.

    Called when inbox is deactivated or deleted.

    Args:
        scheduler: APScheduler instance
        inbox_id: Inbox ID
    """
    job_id = f"poll_inbox_{inbox_id}"

    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)
        logger.info(f"Removed polling job {job_id}")
