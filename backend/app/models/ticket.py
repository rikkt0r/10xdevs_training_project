"""
Ticket model for internal tickets.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Ticket(Base):
    """Internal ticket model."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    state = Column(String(20), nullable=False, default="new")
    creator_email = Column(String(255), nullable=False, index=True)
    source = Column(String(20), nullable=False, default="web")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    board = relationship("Board", back_populates="tickets")
    status_changes = relationship("TicketStatusChange", back_populates="ticket", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "state IN ('new', 'in_progress', 'closed', 'rejected')",
            name="check_ticket_state"
        ),
        CheckConstraint(
            "source IN ('web', 'email')",
            name="check_ticket_source"
        ),
        Index("idx_tickets_board_state", "board_id", "state"),
        Index("idx_tickets_board_created", "board_id", "created_at"),
    )
