"""
Standby queue item model for unrouted emails and failed external ticket creations.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class StandbyQueueItem(Base):
    """Standby queue item model."""

    __tablename__ = "standby_queue_items"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("managers.id", ondelete="CASCADE"), nullable=False, index=True)
    email_subject = Column(String(255), nullable=False)
    email_body = Column(Text, nullable=False)
    sender_email = Column(String(255), nullable=False)
    failure_reason = Column(String(50), nullable=False)
    original_board_id = Column(Integer, ForeignKey("boards.id", ondelete="SET NULL"), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    manager = relationship("Manager", back_populates="standby_queue_items")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "failure_reason IN ('no_keyword_match', 'external_creation_failed', 'no_board_match')",
            name="check_failure_reason"
        ),
    )
