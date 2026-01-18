"""
Authentication service for business logic.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.manager import Manager
from app.models.manager_token import ManagerToken
from app.core.security import hash_password, verify_password, create_access_token, hash_string
from app.core.config import settings
from app.services.email_service import email_service


class AuthService:
    """Service for authentication operations."""

    def create_manager(
        self,
        db: Session,
        email: str,
        password: str,
        name: str
    ) -> Manager:
        """
        Create a new manager account.

        Args:
            db: Database session
            email: Manager email
            password: Plain text password
            name: Manager name

        Returns:
            Created manager instance

        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_manager = db.query(Manager).filter(Manager.email == email).first()
        if existing_manager:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create manager
        hashed_password = hash_password(password)
        manager = Manager(
            email=email,
            password_hash=hashed_password,
            name=name,
            timezone="UTC"
        )
        db.add(manager)
        db.commit()
        db.refresh(manager)

        return manager

    def create_verification_token(self, db: Session, manager: Manager) -> str:
        """
        Create email verification token.

        Args:
            db: Database session
            manager: Manager instance

        Returns:
            Verification token string
        """
        # Generate random token
        token = secrets.token_urlsafe(32)
        token_hash = hash_string(token)

        # Store token in database
        manager_token = ManagerToken(
            manager_id=manager.id,
            token_hash=token_hash,
            token_type="email_verification",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(manager_token)
        db.commit()

        return token

    def verify_email_token(self, db: Session, token: str) -> Manager:
        """
        Verify email token and mark email as verified.

        Args:
            db: Database session
            token: Verification token

        Returns:
            Verified manager instance

        Raises:
            HTTPException: If token is invalid or expired
        """
        token_hash = hash_string(token)

        # Find token
        manager_token = db.query(ManagerToken).filter(
            ManagerToken.token_hash == token_hash,
            ManagerToken.token_type == "email_verification",
            ManagerToken.used_at.is_(None)
        ).first()

        if not manager_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or already used token"
            )

        # Check expiration
        if manager_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )

        # Mark token as used
        manager_token.used_at = datetime.utcnow()

        # Mark email as verified
        manager = db.query(Manager).filter(Manager.id == manager_token.manager_id).first()
        manager.email_verified_at = datetime.utcnow()

        db.commit()
        db.refresh(manager)

        return manager

    def authenticate_manager(self, db: Session, email: str, password: str) -> Optional[Manager]:
        """
        Authenticate manager with email and password.

        Args:
            db: Database session
            email: Manager email
            password: Plain text password

        Returns:
            Manager instance if authenticated, None otherwise
        """
        manager = db.query(Manager).filter(Manager.email == email).first()

        if not manager:
            return None

        if not verify_password(password, manager.password_hash):
            return None

        return manager

    def create_password_reset_token(self, db: Session, manager: Manager) -> str:
        """
        Create password reset token.

        Args:
            db: Database session
            manager: Manager instance

        Returns:
            Reset token string
        """
        # Generate random token
        token = secrets.token_urlsafe(32)
        token_hash = hash_string(token)

        # Invalidate any existing password reset tokens
        db.query(ManagerToken).filter(
            ManagerToken.manager_id == manager.id,
            ManagerToken.token_type == "password_reset",
            ManagerToken.used_at.is_(None)
        ).update({"used_at": datetime.utcnow()})

        # Store token in database
        manager_token = ManagerToken(
            manager_id=manager.id,
            token_hash=token_hash,
            token_type="password_reset",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(manager_token)
        db.commit()

        return token

    def reset_password(self, db: Session, token: str, new_password: str) -> Manager:
        """
        Reset password using reset token.

        Args:
            db: Database session
            token: Reset token
            new_password: New plain text password

        Returns:
            Manager instance

        Raises:
            HTTPException: If token is invalid or expired
        """
        token_hash = hash_string(token)

        # Find token
        manager_token = db.query(ManagerToken).filter(
            ManagerToken.token_hash == token_hash,
            ManagerToken.token_type == "password_reset",
            ManagerToken.used_at.is_(None)
        ).first()

        if not manager_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or already used token"
            )

        # Check expiration
        if manager_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has expired"
            )

        # Mark token as used
        manager_token.used_at = datetime.utcnow()

        # Update password
        manager = db.query(Manager).filter(Manager.id == manager_token.manager_id).first()
        manager.password_hash = hash_password(new_password)

        db.commit()
        db.refresh(manager)

        return manager


# Singleton instance
auth_service = AuthService()
