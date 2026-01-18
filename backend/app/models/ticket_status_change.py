"""
Ticket status change model for audit log of ticket state transitions.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TicketStatusChange(Base):
    """Ticket status change audit log model."""

    __tablename__ = "ticket_status_changes"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_state = Column(String(20), nullable=False)
    new_state = Column(String(20), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="status_changes")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "previous_state IN ('new', 'in_progress', 'closed', 'rejected')",
            name="check_previous_state"
        ),
        CheckConstraint(
            "new_state IN ('new', 'in_progress', 'closed', 'rejected')",
            name="check_new_state"
        ),
        CheckConstraint(
            "previous_state <> new_state",
            name="check_state_different"
        ),
        Index("idx_ticket_status_changes_ticket_created", "ticket_id", "created_at"),
    )
