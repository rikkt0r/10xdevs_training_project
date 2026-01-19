"""
Pydantic schemas for email inbox endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# Create inbox
class CreateEmailInboxRequest(BaseModel):
    """Create email inbox request."""
    name: str = Field(..., max_length=255)
    imap_host: str = Field(..., max_length=255)
    imap_port: int = Field(..., ge=1, le=65535)
    imap_username: str = Field(..., max_length=255)
    imap_password: str
    imap_use_ssl: bool = True
    smtp_host: str = Field(..., max_length=255)
    smtp_port: int = Field(..., ge=1, le=65535)
    smtp_username: str = Field(..., max_length=255)
    smtp_password: str
    smtp_use_tls: bool = True
    from_address: str = Field(..., max_length=255)
    polling_interval: int = 5

    @field_validator('polling_interval')
    @classmethod
    def validate_polling_interval(cls, v):
        if v not in [1, 5, 15]:
            raise ValueError('polling_interval must be 1, 5, or 15')
        return v


# Update inbox
class UpdateEmailInboxRequest(BaseModel):
    """Update email inbox request."""
    name: Optional[str] = Field(None, max_length=255)
    imap_host: Optional[str] = Field(None, max_length=255)
    imap_port: Optional[int] = Field(None, ge=1, le=65535)
    imap_username: Optional[str] = Field(None, max_length=255)
    imap_password: Optional[str] = None
    imap_use_ssl: Optional[bool] = None
    smtp_host: Optional[str] = Field(None, max_length=255)
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_username: Optional[str] = Field(None, max_length=255)
    smtp_password: Optional[str] = None
    smtp_use_tls: Optional[bool] = None
    from_address: Optional[str] = Field(None, max_length=255)
    polling_interval: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('polling_interval')
    @classmethod
    def validate_polling_interval(cls, v):
        if v is not None and v not in [1, 5, 15]:
            raise ValueError('polling_interval must be 1, 5, or 15')
        return v


# Email inbox response
class EmailInboxResponse(BaseModel):
    """Email inbox response (passwords excluded)."""
    id: int
    name: str
    from_address: str
    imap_host: str
    imap_port: int
    smtp_host: str
    smtp_port: int
    polling_interval: int
    is_active: bool
    last_polled_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Test connection request
class TestConnectionRequest(BaseModel):
    """Test email connection request."""
    imap_host: str = Field(..., max_length=255)
    imap_port: int = Field(..., ge=1, le=65535)
    imap_username: str = Field(..., max_length=255)
    imap_password: str
    imap_use_ssl: bool = True
    smtp_host: str = Field(..., max_length=255)
    smtp_port: int = Field(..., ge=1, le=65535)
    smtp_username: str = Field(..., max_length=255)
    smtp_password: str
    smtp_use_tls: bool = True


# Test connection response
class TestConnectionResponse(BaseModel):
    """Test connection response."""
    imap_status: str
    imap_error: Optional[str] = None
    smtp_status: str
    smtp_error: Optional[str] = None
