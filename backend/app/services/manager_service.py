"""
Manager service for profile management business logic.
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone as tz

from app.models.manager import Manager
from app.core.security import hash_password, verify_password


class ManagerService:
    """Service for manager profile operations."""

    def get_manager_profile(self, db: Session, manager_id: int) -> Manager:
        """
        Get manager profile by ID.

        Args:
            db: Database session
            manager_id: Manager ID

        Returns:
            Manager instance

        Raises:
            HTTPException: If manager not found
        """
        manager = db.query(Manager).filter(Manager.id == manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found"
            )
        return manager

    def update_profile(
        self,
        db: Session,
        manager: Manager,
        name: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Manager:
        """
        Update manager profile.

        Args:
            db: Database session
            manager: Manager instance
            name: New name (optional)
            timezone: New timezone (optional)

        Returns:
            Updated manager instance
        """
        if name is not None:
            manager.name = name
        if timezone is not None:
            manager.timezone = timezone

        manager.updated_at = datetime.now(tz.utc)
        db.commit()
        db.refresh(manager)

        return manager

    def change_password(
        self,
        db: Session,
        manager: Manager,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change manager password.

        Args:
            db: Database session
            manager: Manager instance
            current_password: Current password
            new_password: New password

        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, manager.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        # Update password
        manager.password_hash = hash_password(new_password)
        manager.updated_at = datetime.now(tz.utc)
        db.commit()

    def suspend_account(
        self,
        db: Session,
        manager: Manager,
        suspension_message: str,
        password: str
    ) -> None:
        """
        Suspend manager account.

        Args:
            db: Database session
            manager: Manager instance
            suspension_message: Message to display when account is suspended
            password: Current password for confirmation

        Raises:
            HTTPException: If password is incorrect or account already suspended
        """
        # Check if already suspended
        if manager.is_suspended:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account is already suspended"
            )

        # Verify password
        if not verify_password(password, manager.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect"
            )

        # Suspend account
        manager.is_suspended = True
        manager.suspension_message = suspension_message
        manager.updated_at = datetime.now(tz.utc)
        db.commit()


# Singleton instance
manager_service = ManagerService()
