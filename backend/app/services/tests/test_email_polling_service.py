"""
Unit tests for email polling service.

Note: The APScheduler is globally mocked in conftest.py to prevent
"SchedulerAlreadyRunningError" during tests. All scheduler interactions
are mocked and don't actually execute.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.services.email_polling_service import EmailPollingService, email_polling_service
from app.models.email_inbox import EmailInbox
from app.models.board import Board
from app.models.board_keyword import BoardKeyword
from app.models.ticket import Ticket
from app.models.standby_queue_item import StandbyQueueItem
from app.models.processed_email import ProcessedEmail
from app.core.config import settings


class TestEmailPollingService:
    """Unit tests for EmailPollingService."""

    def test_hash_subject(self):
        """Test subject hashing produces consistent SHA-256 hashes."""
        service = EmailPollingService()

        subject1 = "Test Subject"
        subject2 = "Test Subject"
        subject3 = "Different Subject"

        hash1 = service._hash_subject(subject1)
        hash2 = service._hash_subject(subject2)
        hash3 = service._hash_subject(subject3)

        # Same subjects should produce same hash
        assert hash1 == hash2
        # Different subjects should produce different hashes
        assert hash1 != hash3
        # Should be valid hex string of 64 chars (SHA-256)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)

    def test_strip_html_simple(self):
        """Test HTML stripping produces clean plain text."""
        service = EmailPollingService()

        html = """
        <html>
            <body>
                <p>This is a <strong>test</strong> email.</p>
                <p>Second paragraph.</p>
            </body>
        </html>
        """

        result = service._strip_html(html)

        assert "This is a test email." in result
        assert "Second paragraph." in result
        assert "<html>" not in result
        assert "<p>" not in result
        assert "<strong>" not in result

    def test_strip_html_with_scripts(self):
        """Test HTML stripping removes script and style tags."""
        service = EmailPollingService()

        html = """
        <html>
            <head>
                <style>body { color: red; }</style>
            </head>
            <body>
                <script>alert('xss');</script>
                <p>Clean content</p>
            </body>
        </html>
        """

        result = service._strip_html(html)

        assert "Clean content" in result
        assert "alert" not in result
        assert "color: red" not in result

    def test_parse_email_plain_text(self):
        """Test parsing plain text email."""
        service = EmailPollingService()

        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Message-ID: <12345@example.com>
Content-Type: text/plain

This is the email body.
"""

        parsed = service._parse_email(raw_email)

        assert parsed['sender'] == 'sender@example.com'
        assert parsed['subject'] == 'Test Subject'
        assert 'This is the email body.' in parsed['body']
        assert parsed['message_id'] == '<12345@example.com>'

    def test_parse_email_sender_with_name(self):
        """Test parsing email with sender name."""
        service = EmailPollingService()

        raw_email = b"""From: John Doe <john@example.com>
To: recipient@example.com
Subject: Test
Message-ID: <123@example.com>
Content-Type: text/plain

Body text.
"""

        parsed = service._parse_email(raw_email)

        # Should extract just the email address
        assert parsed['sender'] == 'john@example.com'

    def test_parse_email_html(self):
        """Test parsing HTML email with stripping."""
        service = EmailPollingService()

        raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: HTML Test
Message-ID: <123@example.com>
Content-Type: text/html

<html>
<body>
<p>This is <strong>HTML</strong> content.</p>
</body>
</html>
"""

        parsed = service._parse_email(raw_email)

        assert 'This is HTML content.' in parsed['body']
        assert '<html>' not in parsed['body']
        assert '<strong>' not in parsed['body']

    @pytest.mark.asyncio
    async def test_is_duplicate_within_threshold(self, test_db, verified_manager):
        """Test duplicate detection within threshold."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="test@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="test@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="test@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create processed email within threshold
        subject_hash = service._hash_subject("Test Subject")
        processed = ProcessedEmail(
            inbox_id=inbox.id,
            message_id="<123@example.com>",
            sender_email="sender@example.com",
            subject_hash=subject_hash,
            processed_at=datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        test_db.add(processed)
        test_db.commit()

        # Check if duplicate (should be True within 60 min threshold)
        is_dup = service._is_duplicate(
            test_db,
            inbox.id,
            "sender@example.com",
            subject_hash
        )

        assert is_dup is True

    @pytest.mark.asyncio
    async def test_is_duplicate_outside_threshold(self, test_db, verified_manager):
        """Test email not duplicate outside threshold."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="test@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="test@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="test@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create processed email OUTSIDE threshold (90 minutes ago)
        subject_hash = service._hash_subject("Test Subject")
        processed = ProcessedEmail(
            inbox_id=inbox.id,
            message_id="<123@example.com>",
            sender_email="sender@example.com",
            subject_hash=subject_hash,
            processed_at=datetime.now(timezone.utc) - timedelta(minutes=90)
        )
        test_db.add(processed)
        test_db.commit()

        # Check if duplicate (should be False outside 60 min threshold)
        is_dup = service._is_duplicate(
            test_db,
            inbox.id,
            "sender@example.com",
            subject_hash
        )

        assert is_dup is False

    @pytest.mark.asyncio
    async def test_route_email_exclusive_inbox(self, test_db, verified_manager):
        """Test routing via exclusive inbox (priority 1)."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Support Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="support@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="support@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="support@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create board with exclusive inbox
        board = Board(
            manager_id=verified_manager.id,
            name="Support Board",
            unique_name="support-board",
            exclusive_inbox_id=inbox.id,
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()

        # Route email
        with patch.object(service, '_create_ticket', new_callable=AsyncMock) as mock_create:
            mock_ticket = MagicMock(spec=Ticket)
            mock_ticket.id = 1
            mock_create.return_value = mock_ticket

            ticket = await service._route_email(
                test_db,
                inbox,
                "user@example.com",
                "Help needed",
                "I need help with something"
            )

            # Should create ticket
            assert mock_create.called
            assert ticket is not None

    @pytest.mark.asyncio
    async def test_route_email_keyword_match(self, test_db, verified_manager):
        """Test routing via keyword matching (priority 2)."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="General Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="general@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="general@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="general@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Create board WITHOUT exclusive inbox
        board = Board(
            manager_id=verified_manager.id,
            name="Bug Reports",
            unique_name="bug-reports",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()

        # Add keyword
        keyword = BoardKeyword(
            board_id=board.id,
            keyword="bug"
        )
        test_db.add(keyword)
        test_db.commit()

        # Route email with keyword in subject
        with patch.object(service, '_create_ticket', new_callable=AsyncMock) as mock_create:
            mock_ticket = MagicMock(spec=Ticket)
            mock_ticket.id = 1
            mock_create.return_value = mock_ticket

            ticket = await service._route_email(
                test_db,
                inbox,
                "user@example.com",
                "BUG: Login not working",
                "I cannot log in"
            )

            # Should create ticket
            assert mock_create.called
            assert ticket is not None

    @pytest.mark.asyncio
    async def test_route_email_keyword_case_insensitive(self, test_db, verified_manager):
        """Test keyword matching is case-insensitive."""
        service = EmailPollingService()

        # Create inbox and board
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="General Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="general@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="general@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="general@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        board = Board(
            manager_id=verified_manager.id,
            name="Urgent Issues",
            unique_name="urgent-issues",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()

        # Add lowercase keyword
        keyword = BoardKeyword(
            board_id=board.id,
            keyword="urgent"
        )
        test_db.add(keyword)
        test_db.commit()

        # Route email with UPPERCASE keyword in subject
        with patch.object(service, '_create_ticket', new_callable=AsyncMock) as mock_create:
            mock_ticket = MagicMock(spec=Ticket)
            mock_ticket.id = 1
            mock_create.return_value = mock_ticket

            ticket = await service._route_email(
                test_db,
                inbox,
                "user@example.com",
                "URGENT: Server is down",
                "The server crashed"
            )

            # Should match despite case difference
            assert mock_create.called
            assert ticket is not None

    @pytest.mark.asyncio
    async def test_route_email_no_match_standby_queue(self, test_db, verified_manager):
        """Test routing to standby queue when no match (priority 3)."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="General Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="general@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="general@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="general@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # No boards or keywords

        # Route email - should go to standby queue
        ticket = await service._route_email(
            test_db,
            inbox,
            "user@example.com",
            "Random question",
            "I have a question"
        )

        # Should NOT create ticket
        assert ticket is None

        # Should create standby queue item
        queue_item = test_db.query(StandbyQueueItem).filter(
            StandbyQueueItem.manager_id == verified_manager.id
        ).first()

        assert queue_item is not None
        assert queue_item.email_subject == "Random question"
        assert queue_item.sender_email == "user@example.com"
        assert queue_item.failure_reason == "no_keyword_match"

    @pytest.mark.asyncio
    async def test_create_ticket(self, test_db, verified_manager):
        """Test ticket creation with confirmation email."""
        service = EmailPollingService()

        # Create inbox and board
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Support Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="support@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="support@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="support@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        board = Board(
            manager_id=verified_manager.id,
            name="Support Board",
            unique_name="support",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()

        # Create ticket
        with patch('app.services.email_polling_service.email_service.send_ticket_confirmation_email', new_callable=AsyncMock) as mock_send:
            ticket = await service._create_ticket(
                test_db,
                board,
                "user@example.com",
                "Help with login",
                "I cannot log in to my account",
                inbox
            )

            # Verify ticket created
            assert ticket is not None
            assert ticket.title == "Help with login"
            assert ticket.description == "I cannot log in to my account"
            assert ticket.creator_email == "user@example.com"
            assert ticket.source == "email"
            assert ticket.state == "new"
            assert ticket.board_id == board.id

            # Verify confirmation email sent
            assert mock_send.called

    @pytest.mark.asyncio
    async def test_create_ticket_truncates_long_title(self, test_db, verified_manager):
        """Test title truncation to 255 chars."""
        service = EmailPollingService()

        # Create inbox and board
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Support Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="support@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="support@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="support@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        board = Board(
            manager_id=verified_manager.id,
            name="Support Board",
            unique_name="support",
            is_archived=False
        )
        test_db.add(board)
        test_db.commit()

        # Create ticket with very long title
        long_title = "A" * 300  # 300 characters

        with patch('app.services.email_polling_service.email_service.send_ticket_confirmation_email', new_callable=AsyncMock):
            ticket = await service._create_ticket(
                test_db,
                board,
                "user@example.com",
                long_title,
                "Body text",
                inbox
            )

            # Verify title truncated to 255 chars
            assert len(ticket.title) == 255
            assert ticket.title == "A" * 255

    def test_mark_processed(self, test_db, verified_manager):
        """Test marking email as processed."""
        service = EmailPollingService()

        # Create inbox
        inbox = EmailInbox(
            manager_id=verified_manager.id,
            name="Test Inbox",
            imap_host="imap.example.com",
            imap_port=993,
            imap_username="test@example.com",
            imap_password_encrypted="encrypted",
            imap_use_ssl=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_username="test@example.com",
            smtp_password_encrypted="encrypted",
            smtp_use_tls=True,
            from_address="test@example.com",
            polling_interval=5,
            is_active=True
        )
        test_db.add(inbox)
        test_db.commit()

        # Mark as processed
        subject_hash = service._hash_subject("Test Subject")
        processed = service._mark_processed(
            test_db,
            inbox.id,
            "<123@example.com>",
            "sender@example.com",
            subject_hash
        )

        # Verify record created
        assert processed is not None
        assert processed.inbox_id == inbox.id
        assert processed.message_id == "<123@example.com>"
        assert processed.sender_email == "sender@example.com"
        assert processed.subject_hash == subject_hash
        assert processed.processed_at is not None
