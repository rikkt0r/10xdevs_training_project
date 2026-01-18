"""
Email service for sending authentication-related emails.
"""
import logging
from typing import Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_host = settings.SMTP_DEFAULT_HOST
        self.smtp_port = settings.SMTP_DEFAULT_PORT
        self.smtp_use_tls = settings.SMTP_DEFAULT_USE_TLS

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
            message["From"] = from_email or f"noreply@{self.smtp_host}"
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            # In development, just log the email instead of sending
            if settings.APP_ENV == "development":
                logger.info(f"[EMAIL] To: {to_email}")
                logger.info(f"[EMAIL] Subject: {subject}")
                logger.info(f"[EMAIL] Body:\n{body}")
                return True

            # Production: send actual email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls,
            )
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


# Singleton instance
email_service = EmailService()
