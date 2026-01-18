"""
Processed email model for tracking processed emails for duplicate prevention.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProcessedEmail(Base):
    """Processed email tracking model."""

    __tablename__ = "processed_emails"

    id = Column(Integer, primary_key=True, index=True)
    inbox_id = Column(Integer, ForeignKey("email_inboxes.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    subject_hash = Column(String(64), nullable=False)
    processed_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    inbox = relationship("EmailInbox", back_populates="processed_emails")

    # Constraints
    __table_args__ = (
        UniqueConstraint("inbox_id", "message_id", name="uq_inbox_message"),
        Index("idx_processed_emails_inbox_message", "inbox_id", "message_id"),
        Index("idx_processed_emails_duplicate_check", "inbox_id", "sender_email", "subject_hash", "processed_at"),
    )
