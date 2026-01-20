"""
Dependencies for FastAPI endpoints.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.manager import Manager

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_manager(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Manager:
    """
    Dependency to get current authenticated manager from JWT token.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        Current manager instance

    Raises:
        HTTPException: If token is invalid or manager not found
    """
    token = credentials.credentials

    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get manager ID from payload (convert from string to int)
    manager_id_str: Optional[str] = payload.get("sub")
    if manager_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        manager_id = int(manager_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get manager from database
    manager: Manager|None = db.query(Manager).filter(Manager.id == manager_id).first()
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Manager not found",
            headers={"WWW-Authenticate": "Bearer"},
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

    return manager


def get_current_active_manager(
    manager: Manager = Depends(get_current_manager)
) -> Manager:
    """
    Dependency to get current active (non-suspended) manager.

    Args:
        manager: Current manager from get_current_manager

    Returns:
        Current active manager

    Raises:
        HTTPException: If manager is suspended
    """
    if manager.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended"
        )

    return manager
