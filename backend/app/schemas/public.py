"""
Pydantic schemas for public endpoints (no authentication required).
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from uuid import UUID


# GET /api/public/boards/{unique_name} - Response
class PublicBoardInfoResponse(BaseModel):
    """Public board info for the ticket creation form."""
    name: str = Field(..., description="Board name")
    greeting_message: str | None = Field(None, description="Optional greeting message displayed above the form")

    class Config:
        from_attributes = True


# POST /api/public/boards/{unique_name}/tickets - Request
class CreatePublicTicketRequest(BaseModel):
    """Request to create a ticket via public form."""
    email: EmailStr = Field(..., description="Creator's email address")
    title: str = Field(..., min_length=1, max_length=255, description="Ticket title")
    description: str = Field(..., min_length=1, max_length=6000, description="Ticket description")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


# POST /api/public/boards/{unique_name}/tickets - Response
class CreatePublicTicketResponse(BaseModel):
    """Response after creating a ticket via public form."""
    uuid: UUID = Field(..., description="Ticket UUID for viewing the ticket")
    title: str = Field(..., description="Ticket title")
    message: str = Field(..., description="Success message")

    class Config:
        from_attributes = True


# GET /api/public/tickets/{uuid} - Response (Internal Ticket)
class PublicTicketStatusChangeResponse(BaseModel):
    """Public view of a ticket status change."""
    previous_state: str
    new_state: str
    comment: str | None
    created_at: str  # Use string for ISO format in public API

    class Config:
        from_attributes = True


class PublicTicketViewResponse(BaseModel):
    """Public view of an internal ticket."""
    uuid: UUID
    title: str
    description: str
    state: str
    board_name: str
    created_at: str  # Use string for ISO format
    updated_at: str  # Use string for ISO format
    status_changes: list[PublicTicketStatusChangeResponse]

    class Config:
        from_attributes = True


# GET /api/public/tickets/{uuid} - Response (External Ticket)
class PublicExternalTicketViewResponse(BaseModel):
    """Public view of an external ticket (redirects to external platform)."""
    uuid: UUID
    title: str
    board_name: str
    external_url: str
    platform_type: str
    created_at: str  # Use string for ISO format

    class Config:
        from_attributes = True
