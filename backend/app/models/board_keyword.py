"""
Board keyword model for email routing to boards.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class BoardKeyword(Base):
    """Board keyword model for email subject matching."""

    __tablename__ = "board_keywords"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    board = relationship("Board", back_populates="keywords")

    # Constraints
    __table_args__ = (
        UniqueConstraint("board_id", "keyword", name="uq_board_keyword"),
        Index("idx_board_keywords_keyword_lower", func.lower(keyword)),
    )
