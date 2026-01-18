"""
Manager model for authentication and account management.
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Manager(Base):
    """Manager account model."""

    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    timezone = Column(String(64), nullable=False, default="UTC")
    is_suspended = Column(Boolean, nullable=False, default=False)
    suspension_message = Column(Text, nullable=True)
    email_verified_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    tokens = relationship("ManagerToken", back_populates="manager", cascade="all, delete-orphan")
    email_inboxes = relationship("EmailInbox", back_populates="manager", cascade="all, delete-orphan")
    boards = relationship("Board", back_populates="manager")
    standby_queue_items = relationship("StandbyQueueItem", back_populates="manager", cascade="all, delete-orphan")
