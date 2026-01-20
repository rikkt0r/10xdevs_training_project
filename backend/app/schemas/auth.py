"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Registration
class RegisterRequest(BaseModel):
    """Manager registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., max_length=255)


class RegisterResponse(BaseModel):
    """Manager registration response."""
    id: int
    email: str
    name: str
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Login
class LoginRequest(BaseModel):
    """Manager login request."""
    email: EmailStr
    password: str


class ManagerInfo(BaseModel):
    """Manager information for login response."""
    id: int
    email: str
    name: str
    timezone: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Manager login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    manager: ManagerInfo


# Email verification
class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str


# Resend verification
class ResendVerificationRequest(BaseModel):
    """Resend verification email request."""
    email: EmailStr


# Forgot password
class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: EmailStr


# Reset password
class ResetPasswordRequest(BaseModel):
    """Reset password request."""
    token: str
    password: str = Field(..., min_length=8)


# Token refresh
class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    """Generic token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
