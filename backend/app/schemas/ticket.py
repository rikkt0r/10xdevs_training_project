"""
Pydantic schemas for ticket endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# Request schemas
class ChangeTicketStateRequest(BaseModel):
    """Change ticket state request."""
    state: str = Field(..., description="New state: 'new', 'in_progress', 'closed', or 'rejected'")
    comment: Optional[str] = Field(None, description="Optional manager comment")

    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate state is one of the allowed values."""
        if v not in ('new', 'in_progress', 'closed', 'rejected'):
            raise ValueError("state must be 'new', 'in_progress', 'closed', or 'rejected'")
        return v


# Response schemas - Nested objects
class StatusChangeResponse(BaseModel):
    """Status change response."""
    id: int
    previous_state: str
    new_state: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BoardInfoResponse(BaseModel):
    """Minimal board info for ticket responses."""
    id: int
    name: str
    unique_name: str

    class Config:
        from_attributes = True


# Response schemas - Main
class TicketResponse(BaseModel):
    """Basic ticket response for list views."""
    id: int
    uuid: UUID
    title: str
    description: str
    state: str
    creator_email: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketDetailResponse(BaseModel):
    """Detailed ticket response with board info and status changes."""
    id: int
    uuid: UUID
    board: BoardInfoResponse
    title: str
    description: str
    state: str
    creator_email: str
    source: str
    created_at: datetime
    updated_at: datetime
    status_changes: list[StatusChangeResponse]

    class Config:
        from_attributes = True


class RecentTicketResponse(BaseModel):
    """Recent ticket response for dashboard."""
    id: int
    uuid: UUID
    title: str
    state: str
    board: BoardInfoResponse
    created_at: datetime

    class Config:
        from_attributes = True
