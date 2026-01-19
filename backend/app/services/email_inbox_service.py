"""
Email inbox service for managing IMAP/SMTP configurations.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.email_inbox import EmailInbox
from app.models.manager import Manager
from app.core.security import encrypt_data, decrypt_data


class EmailInboxService:
    """Service for email inbox operations."""

    def create_inbox(
        self,
        db: Session,
        manager: Manager,
        name: str,
        imap_host: str,
        imap_port: int,
        imap_username: str,
        imap_password: str,
        imap_use_ssl: bool,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        smtp_use_tls: bool,
        from_address: str,
        polling_interval: int
    ) -> EmailInbox:
        """
        Create a new email inbox configuration.

        Args:
            db: Database session
            manager: Manager instance
            (other args): Inbox configuration parameters

        Returns:
            Created EmailInbox instance
        """
        # Encrypt passwords
        imap_password_encrypted = encrypt_data(imap_password)
        smtp_password_encrypted = encrypt_data(smtp_password)

        # Create inbox
        inbox = EmailInbox(
            manager_id=manager.id,
            name=name,
            imap_host=imap_host,
            imap_port=imap_port,
            imap_username=imap_username,
            imap_password_encrypted=imap_password_encrypted,
            imap_use_ssl=imap_use_ssl,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password_encrypted=smtp_password_encrypted,
            smtp_use_tls=smtp_use_tls,
            from_address=from_address,
            polling_interval=polling_interval
        )

        db.add(inbox)
        db.commit()
        db.refresh(inbox)

        return inbox

    def get_inboxes(self, db: Session, manager: Manager) -> List[EmailInbox]:
        """
        Get all inboxes for a manager.

        Args:
            db: Database session
            manager: Manager instance

        Returns:
            List of EmailInbox instances
        """
        return db.query(EmailInbox).filter(
            EmailInbox.manager_id == manager.id
        ).order_by(EmailInbox.created_at.desc()).all()

    def get_inbox(self, db: Session, manager: Manager, inbox_id: int) -> EmailInbox:
        """
        Get a specific inbox by ID.

        Args:
            db: Database session
            manager: Manager instance
            inbox_id: Inbox ID

        Returns:
            EmailInbox instance

        Raises:
            HTTPException: If inbox not found or not owned by manager
        """
        inbox = db.query(EmailInbox).filter(EmailInbox.id == inbox_id).first()

        if not inbox:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inbox not found"
            )

        if inbox.manager_id != manager.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this inbox"
            )

        return inbox

    def update_inbox(
        self,
        db: Session,
        manager: Manager,
        inbox_id: int,
        **kwargs
    ) -> EmailInbox:
        """
        Update an inbox configuration.

        Args:
            db: Database session
            manager: Manager instance
            inbox_id: Inbox ID
            **kwargs: Fields to update

        Returns:
            Updated EmailInbox instance
        """
        inbox = self.get_inbox(db, manager, inbox_id)

        # Encrypt passwords if provided
        if 'imap_password' in kwargs and kwargs['imap_password']:
            kwargs['imap_password_encrypted'] = encrypt_data(kwargs.pop('imap_password'))

        if 'smtp_password' in kwargs and kwargs['smtp_password']:
            kwargs['smtp_password_encrypted'] = encrypt_data(kwargs.pop('smtp_password'))

        # Update fields
        for key, value in kwargs.items():
            if value is not None and hasattr(inbox, key):
                setattr(inbox, key, value)

        inbox.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(inbox)

        return inbox

    def delete_inbox(self, db: Session, manager: Manager, inbox_id: int) -> None:
        """
        Delete an inbox.

        Args:
            db: Database session
            manager: Manager instance
            inbox_id: Inbox ID

        Raises:
            HTTPException: If inbox not found or not owned by manager
        """
        inbox = self.get_inbox(db, manager, inbox_id)
        db.delete(inbox)
        db.commit()

    def test_connection(
        self,
        imap_host: str,
        imap_port: int,
        imap_username: str,
        imap_password: str,
        imap_use_ssl: bool,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        smtp_use_tls: bool
    ) -> Dict[str, str]:
        """
        Test IMAP and SMTP connections.

        Args:
            (connection parameters)

        Returns:
            Dictionary with connection test results

        Note:
            This is a placeholder implementation. In production, this would
            attempt actual connections to IMAP and SMTP servers.
        """
        # TODO: Implement actual IMAP/SMTP connection testing
        # For now, return success for basic validation
        result = {
            "imap_status": "success",
            "imap_error": None,
            "smtp_status": "success",
            "smtp_error": None
        }

        # Basic validation
        if not imap_host or not imap_username or not imap_password:
            result["imap_status"] = "failed"
            result["imap_error"] = "Missing required IMAP credentials"

        if not smtp_host or not smtp_username or not smtp_password:
            result["smtp_status"] = "failed"
            result["smtp_error"] = "Missing required SMTP credentials"

        return result

    def test_inbox_connection(
        self,
        db: Session,
        manager: Manager,
        inbox_id: int
    ) -> Dict[str, str]:
        """
        Test connection for an existing inbox.

        Args:
            db: Database session
            manager: Manager instance
            inbox_id: Inbox ID

        Returns:
            Dictionary with connection test results
        """
        inbox = self.get_inbox(db, manager, inbox_id)

        # Decrypt passwords
        imap_password = decrypt_data(inbox.imap_password_encrypted)
        smtp_password = decrypt_data(inbox.smtp_password_encrypted)

        # Test connection
        return self.test_connection(
            imap_host=inbox.imap_host,
            imap_port=inbox.imap_port,
            imap_username=inbox.imap_username,
            imap_password=imap_password,
            imap_use_ssl=inbox.imap_use_ssl,
            smtp_host=inbox.smtp_host,
            smtp_port=inbox.smtp_port,
            smtp_username=inbox.smtp_username,
            smtp_password=smtp_password,
            smtp_use_tls=inbox.smtp_use_tls
        )


# Singleton instance
email_inbox_service = EmailInboxService()
