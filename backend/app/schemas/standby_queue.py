"""
Pydantic schemas for standby queue endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Queue item response
class StandbyQueueItemResponse(BaseModel):
    """Standby queue item response."""
    id: int
    email_subject: str
    email_body: str
    sender_email: str
    failure_reason: str
    original_board_id: Optional[int]
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Assign to board
class AssignToBoardRequest(BaseModel):
    """Request to assign queue item to board."""
    board_id: int = Field(..., gt=0)


class AssignedTicketInfo(BaseModel):
    """Ticket info after assignment."""
    id: int
    uuid: str
    title: str
    board_id: int


class AssignToBoardResponse(BaseModel):
    """Response after assigning to board."""
    ticket: AssignedTicketInfo


# Retry external creation
class RetryExternalInfo(BaseModel):
    """External ticket info after retry."""
    id: int
    external_url: str
    external_id: str


class RetryExternalResponse(BaseModel):
    """Response after retrying external creation."""
    external_ticket: RetryExternalInfo
