"""
Board model for ticket boards.
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, CheckConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Board(Base):
    """Ticket board model."""

    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("managers.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    unique_name = Column(String(255), unique=True, nullable=False, index=True)
    greeting_message = Column(Text, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    external_platform_type = Column(String(20), nullable=True)
    external_platform_config = Column(JSON, nullable=True)  # Use JSON instead of JSONB for SQLite compatibility
    exclusive_inbox_id = Column(Integer, ForeignKey("email_inboxes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    manager = relationship("Manager", back_populates="boards")
    keywords = relationship("BoardKeyword", back_populates="board", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="board", cascade="all, delete-orphan")
    external_tickets = relationship("ExternalTicket", back_populates="board", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "external_platform_type IS NULL OR external_platform_type IN ('jira', 'trello')",
            name="check_external_platform_type"
        ),
    )
