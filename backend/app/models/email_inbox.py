"""
Email inbox model for IMAP/SMTP configuration.
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmailInbox(Base):
    """Email inbox configuration model."""

    __tablename__ = "email_inboxes"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("managers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    imap_host = Column(String(255), nullable=False)
    imap_port = Column(Integer, nullable=False, default=993)
    imap_username = Column(String(255), nullable=False)
    imap_password_encrypted = Column(Text, nullable=False)
    imap_use_ssl = Column(Boolean, nullable=False, default=True)
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False, default=587)
    smtp_username = Column(String(255), nullable=False)
    smtp_password_encrypted = Column(Text, nullable=False)
    smtp_use_tls = Column(Boolean, nullable=False, default=True)
    from_address = Column(String(255), nullable=False)
    polling_interval = Column(Integer, nullable=False, default=5)
    last_polled_at = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    manager = relationship("Manager", back_populates="email_inboxes")
    processed_emails = relationship("ProcessedEmail", back_populates="inbox", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "polling_interval IN (1, 5, 15)",
            name="check_polling_interval"
        ),
    )
