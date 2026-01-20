"""
Pydantic schemas for board endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# Ticket counts nested in board responses
class TicketCounts(BaseModel):
    """Ticket counts by state."""
    new: int = 0
    in_progress: int = 0
    closed: int = 0
    rejected: int = 0


# Request schemas
class CreateBoardRequest(BaseModel):
    """Create board request."""
    name: str = Field(..., max_length=255, description="Board display name")
    unique_name: str = Field(..., max_length=255, description="URL-safe slug for public form")
    greeting_message: Optional[str] = Field(None, description="Message shown above public form")
    exclusive_inbox_id: Optional[int] = Field(None, description="Exclusive inbox assignment")
    external_platform_type: Optional[str] = Field(None, description="External platform: 'jira' or 'trello'")
    external_platform_config: Optional[dict] = Field(None, description="Platform-specific configuration")

    @field_validator('unique_name')
    @classmethod
    def validate_unique_name(cls, v: str) -> str:
        """Validate unique_name is URL-safe slug."""
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', v):
            raise ValueError(
                'unique_name must be lowercase alphanumeric with hyphens, '
                'cannot start or end with hyphen'
            )
        return v

    @field_validator('external_platform_type')
    @classmethod
    def validate_platform_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate external_platform_type."""
        if v is not None and v not in ('jira', 'trello'):
            raise ValueError("external_platform_type must be 'jira' or 'trello'")
        return v


class UpdateBoardRequest(BaseModel):
    """Update board request."""
    name: Optional[str] = Field(None, max_length=255)
    unique_name: Optional[str] = Field(None, max_length=255)
    greeting_message: Optional[str] = None
    exclusive_inbox_id: Optional[int] = None
    external_platform_type: Optional[str] = None
    external_platform_config: Optional[dict] = None

    @field_validator('unique_name')
    @classmethod
    def validate_unique_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate unique_name is URL-safe slug."""
        if v is not None and not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', v):
            raise ValueError(
                'unique_name must be lowercase alphanumeric with hyphens, '
                'cannot start or end with hyphen'
            )
        return v

    @field_validator('external_platform_type')
    @classmethod
    def validate_platform_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate external_platform_type."""
        if v is not None and v not in ('jira', 'trello'):
            raise ValueError("external_platform_type must be 'jira' or 'trello'")
        return v


# Response schemas
class BoardResponse(BaseModel):
    """Basic board response."""
    id: int
    name: str
    unique_name: str
    greeting_message: Optional[str]
    is_archived: bool
    external_platform_type: Optional[str]
    exclusive_inbox_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BoardWithTicketCountsResponse(BaseModel):
    """Board response with ticket counts."""
    id: int
    name: str
    unique_name: str
    greeting_message: Optional[str]
    is_archived: bool
    external_platform_type: Optional[str]
    exclusive_inbox_id: Optional[int]
    ticket_counts: TicketCounts
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestExternalConnectionResponse(BaseModel):
    """Test external platform connection response."""
    status: str = Field(..., description="'success' or 'failed'")
    message: str = Field(..., description="Human-readable message")


# Board Keyword schemas
class CreateKeywordRequest(BaseModel):
    """Create keyword request."""
    keyword: str = Field(..., max_length=255, description="Keyword for email subject matching")


class KeywordResponse(BaseModel):
    """Keyword response."""
    id: int
    keyword: str
    created_at: datetime

    class Config:
        from_attributes = True
