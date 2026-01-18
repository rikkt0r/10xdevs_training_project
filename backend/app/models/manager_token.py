"""
Manager token model for JWT refresh tokens, email verification, and password reset.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ManagerToken(Base):
    """Manager token model for various token types."""

    __tablename__ = "manager_tokens"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("managers.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    token_type = Column(String(20), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    manager = relationship("Manager", back_populates="tokens")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "token_type IN ('refresh', 'email_verification', 'password_reset')",
            name="check_token_type"
        ),
    )
