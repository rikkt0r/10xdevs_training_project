"""
Email service for sending authentication and notification emails.
"""
import logging
from typing import Optional, TYPE_CHECKING
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

if TYPE_CHECKING:
    from app.models.ticket import Ticket
    from app.models.board import Board
    from app.models.ticket_status_change import TicketStatusChange

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_host = settings.SMTP_DEFAULT_HOST
        self.smtp_port = settings.SMTP_DEFAULT_PORT
        self.smtp_use_tls = settings.SMTP_DEFAULT_USE_TLS
        self.smtp_user = settings.SMTP_DEFAULT_USER or None
        self.smtp_password = settings.SMTP_DEFAULT_PASSWORD or None

    @property
    def _has_auth(self) -> bool:
        """Check if SMTP authentication credentials are configured."""
        return bool(self.smtp_user and self.smtp_password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email address (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            message = MIMEMultipart()
            message["From"] = from_email or self.smtp_user or f"noreply@{self.smtp_host}"
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            # In development, just log the email instead of sending
            if settings.APP_ENV == "development":
                logger.info(f"[EMAIL] To: {to_email}")
                logger.info(f"[EMAIL] Subject: {subject}")
                logger.info(f"[EMAIL] Body:\n{body}")
                return True

            # Build SMTP connection options
            smtp_options = {
                "hostname": self.smtp_host,
                "port": self.smtp_port,
                "use_tls": self.smtp_use_tls,
            }

            # Add authentication if credentials are provided
            if self._has_auth:
                smtp_options["username"] = self.smtp_user
                smtp_options["password"] = self.smtp_password

            await aiosmtplib.send(message, **smtp_options)
            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_verification_email(self, to_email: str, token: str) -> bool:
        """
        Send email verification link.

        Args:
            to_email: Recipient email address
            token: Verification token

        Returns:
            True if email sent successfully
        """
        verification_url = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/auth/verify-email?token={token}"

        subject = f"Verify your email - {settings.PROJECT_NAME}"
        body = f"""
Hello,

Thank you for registering with {settings.PROJECT_NAME}.

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
{settings.PROJECT_NAME} Team
        """

        return await self.send_email(to_email, subject, body)

    async def send_password_reset_email(self, to_email: str, token: str) -> bool:
        """
        Send password reset link.

        Args:
            to_email: Recipient email address
            token: Password reset token

        Returns:
            True if email sent successfully
        """
        reset_url = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/reset-password?token={token}"

        subject = f"Reset your password - {settings.PROJECT_NAME}"
        body = f"""
Hello,

We received a request to reset your password for {settings.PROJECT_NAME}.

To reset your password, click the link below:

{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email.

Best regards,
{settings.PROJECT_NAME} Team
        """

        return await self.send_email(to_email, subject, body)

    async def send_ticket_confirmation_email(
        self,
        to_email: str,
        ticket_uuid: str,
        ticket_title: str,
        ticket_description: str,
        board_name: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send ticket creation confirmation email.

        Args:
            to_email: Creator's email address
            ticket_uuid: Ticket UUID for secret link
            ticket_title: Ticket title
            ticket_description: Ticket description
            board_name: Name of the board
            from_email: Sender email address (manager's inbox or default)

        Returns:
            True if email sent successfully
        """
        ticket_url = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/ticket/{ticket_uuid}"

        # Truncate description if too long for email
        desc_preview = ticket_description[:500] + "..." if len(ticket_description) > 500 else ticket_description

        subject = f"Ticket Submitted: {ticket_title}"
        body = f"""
Hello,

Your ticket has been successfully submitted to {board_name}.

Ticket Details:
---------------
Title: {ticket_title}

Description:
{desc_preview}

You can view your ticket status at any time using this link:
{ticket_url}

Please save this link - it's the only way to check your ticket status.

Best regards,
{board_name} Team
        """

        return await self.send_email(to_email, subject, body, from_email)

    async def send_status_change_notification(
        self,
        to_email: str,
        ticket_uuid: str,
        ticket_title: str,
        board_name: str,
        previous_state: str,
        new_state: str,
        comment: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send ticket status change notification email.

        Args:
            to_email: Creator's email address
            ticket_uuid: Ticket UUID for secret link
            ticket_title: Ticket title
            board_name: Name of the board
            previous_state: Previous ticket state
            new_state: New ticket state
            comment: Optional manager comment
            from_email: Sender email address (manager's inbox or default)

        Returns:
            True if email sent successfully
        """
        ticket_url = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/ticket/{ticket_uuid}"

        # Human-readable state names
        state_names = {
            "new": "New",
            "in_progress": "In Progress",
            "closed": "Closed",
            "rejected": "Rejected"
        }
        readable_new_state = state_names.get(new_state, new_state)
        readable_prev_state = state_names.get(previous_state, previous_state)

        subject = f"Ticket Update: {ticket_title} - Now {readable_new_state}"

        comment_section = ""
        if comment:
            comment_section = f"""
Manager's Comment:
{comment}
"""

        body = f"""
Hello,

The status of your ticket has been updated.

Ticket: {ticket_title}
Board: {board_name}

Status Change:
  From: {readable_prev_state}
  To: {readable_new_state}
{comment_section}
You can view your ticket at:
{ticket_url}

Best regards,
{board_name} Team
        """

        return await self.send_email(to_email, subject, body, from_email)


# Singleton instance
email_service = EmailService()
