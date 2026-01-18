"""
External ticket model for references to tickets created in external platforms.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ExternalTicket(Base):
    """External ticket reference model."""

    __tablename__ = "external_tickets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4, index=True)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    creator_email = Column(String(255), nullable=False, index=True)
    external_url = Column(String(2048), nullable=False)
    external_id = Column(String(255), nullable=True)
    platform_type = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    board = relationship("Board", back_populates="external_tickets")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "platform_type IN ('jira', 'trello')",
            name="check_platform_type"
        ),
    )
