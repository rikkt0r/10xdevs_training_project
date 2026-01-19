"""
Pydantic schemas for manager profile endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Manager profile response
class ManagerProfileResponse(BaseModel):
    """Manager profile response."""
    id: int
    email: str
    name: str
    timezone: str
    is_suspended: bool
    email_verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Update profile
class UpdateProfileRequest(BaseModel):
    """Update profile request."""
    name: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=64)


# Change password
class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# Suspend account
class SuspendAccountRequest(BaseModel):
    """Suspend account request."""
    suspension_message: str = Field(..., min_length=1)
    password: str
