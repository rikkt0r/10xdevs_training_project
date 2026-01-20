"""
Authentication endpoints for manager registration, login, and password management.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.responses import DataResponse, MessageResponse, DataWithMessageResponse
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ManagerInfo,
    TokenResponse
)
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.api.dependencies import get_current_manager
from app.models.manager import Manager

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> DataWithMessageResponse[RegisterResponse]:
    """
    Register a new manager account.

    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    - **name**: Display name (max 255 characters)

    Returns the created manager data and sends a verification email.
    """
    # Create manager
    manager = auth_service.create_manager(
        db=db,
        email=request.email,
        password=request.password,
        name=request.name
    )

    # Create verification token
    verification_token = auth_service.create_verification_token(db, manager)

    # Send verification email
    await email_service.send_verification_email(manager.email, verification_token)

    return DataWithMessageResponse[RegisterResponse](
        data=manager,
        message="Verification email sent"
    )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> DataResponse[LoginResponse]:
    """
    Authenticate and receive JWT token.

    - **email**: Manager email
    - **password**: Manager password

    Returns access token and manager information.
    """
    # Authenticate manager
    manager = auth_service.authenticate_manager(
        db=db,
        email=request.email,
        password=request.password
    )

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check if email is verified
    if not manager.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )

    # Check if account is suspended
    if manager.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": manager.id},
        expires_delta=timedelta(hours=settings.JWT_EXPIRY_HOURS)
    )

    # Prepare response
    response_data = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600,
        manager=ManagerInfo.model_validate(manager)
    )

    return DataResponse[LoginResponse](data=response_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_manager: Manager = Depends(get_current_manager)
) -> MessageResponse:
    """
    Invalidate current token (client-side token removal).

    Note: JWT tokens are stateless, so logout is primarily handled client-side.
    This endpoint exists for API consistency.
    """
    return MessageResponse(message="Logged out successfully")


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Verify email with token from verification email.

    - **token**: Verification token from email

    Marks the email as verified.
    """
    # Verify token
    manager = auth_service.verify_email_token(db, request.token)

    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Resend verification email.

    - **email**: Manager email address

    Sends a new verification email if the account exists and is not verified.
    """
    # Find manager
    manager = db.query(Manager).filter(Manager.email == request.email).first()

    if not manager:
        # Don't reveal if email exists (prevent enumeration)
        return MessageResponse(message="If the email exists, a verification link has been sent")

    # Check if already verified
    if manager.email_verified_at:
        return MessageResponse(message="Email already verified")

    # Create new verification token
    verification_token = auth_service.create_verification_token(db, manager)

    # Send verification email
    await email_service.send_verification_email(manager.email, verification_token)

    return MessageResponse(message="If the email exists, a verification link has been sent")


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Request password reset email.

    - **email**: Manager email address

    Always returns success to prevent email enumeration.
    """
    # Find manager
    manager = db.query(Manager).filter(Manager.email == request.email).first()

    if manager:
        # Create password reset token
        reset_token = auth_service.create_password_reset_token(db, manager)

        # Send password reset email
        await email_service.send_password_reset_email(manager.email, reset_token)

    # Always return success (prevent enumeration)
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Reset password with token from reset email.

    - **token**: Reset token from email
    - **password**: New password (minimum 8 characters)

    Resets the password and invalidates the token.
    """
    # Reset password
    manager = auth_service.reset_password(
        db=db,
        token=request.token,
        new_password=request.password
    )

    return MessageResponse(message="Password reset successfully")


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(
    current_manager: Manager = Depends(get_current_manager)
) -> DataResponse[TokenResponse]:
    """
    Refresh JWT token.

    Returns a new access token with extended expiration.
    Token is automatically refreshed on use.
    """
    # Create new access token
    access_token = create_access_token(
        data={"sub": current_manager.id},
        expires_delta=timedelta(hours=settings.JWT_EXPIRY_HOURS)
    )

    response_data = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )

    return DataResponse[TokenResponse](data=response_data)
