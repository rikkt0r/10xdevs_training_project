"""
Manager profile endpoints for viewing and updating profile information.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.manager import (
    ManagerProfileResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
    SuspendAccountRequest
)
from app.schemas.auth import MessageResponse
from app.services.manager_service import manager_service
from app.api.dependencies import get_current_manager
from app.models.manager import Manager

router = APIRouter()


@router.get("/me", response_model=dict, status_code=status.HTTP_200_OK)
def get_profile(
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Get current manager profile.

    Returns the authenticated manager's profile information including:
    - ID, email, name, timezone
    - Account status (suspended, email verified)
    - Creation timestamp
    """
    profile = ManagerProfileResponse.model_validate(current_manager)
    return {
        "data": profile.model_dump()
    }


@router.patch("/me", response_model=dict, status_code=status.HTTP_200_OK)
def update_profile(
    request: UpdateProfileRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Update manager profile.

    Allows updating:
    - **name**: Display name (max 255 characters)
    - **timezone**: IANA timezone string (e.g., 'Europe/Warsaw', 'America/New_York')

    Only provided fields will be updated.
    """
    # Update profile
    updated_manager = manager_service.update_profile(
        db=db,
        manager=current_manager,
        name=request.name,
        timezone=request.timezone
    )

    profile = ManagerProfileResponse.model_validate(updated_manager)
    return {
        "data": profile.model_dump()
    }


@router.put("/me/password", response_model=dict, status_code=status.HTTP_200_OK)
def change_password(
    request: ChangePasswordRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Change manager password.

    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)

    Returns 401 if current password is incorrect.
    """
    # Change password
    manager_service.change_password(
        db=db,
        manager=current_manager,
        current_password=request.current_password,
        new_password=request.new_password
    )

    return {
        "message": "Password changed successfully"
    }


@router.post("/me/suspend", response_model=dict, status_code=status.HTTP_200_OK)
def suspend_account(
    request: SuspendAccountRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Suspend own manager account.

    - **suspension_message**: Message to display when account is suspended (required)
    - **password**: Current password for confirmation (required)

    This action is irreversible. Upon suspension:
    - All board web forms will be disabled and display the suspension message
    - Incoming emails will receive auto-reply with the suspension message
    - Existing tickets remain viewable via secret links

    Returns 401 if password is incorrect.
    Returns 409 if account is already suspended.
    """
    # Suspend account
    manager_service.suspend_account(
        db=db,
        manager=current_manager,
        suspension_message=request.suspension_message,
        password=request.password
    )

    return {
        "message": "Account suspended successfully"
    }
