"""
Email inbox endpoints for managing IMAP/SMTP configurations.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_manager
from app.api.responses import DataResponse
from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.email_inbox import (
    CreateEmailInboxRequest,
    UpdateEmailInboxRequest,
    EmailInboxResponse,
    TestConnectionRequest,
    TestConnectionResponse
)
from app.services.email_inbox_service import email_inbox_service

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_inboxes(
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[list[EmailInboxResponse]]:
    """
    List all email inboxes for the authenticated manager.

    Returns a list of configured email inboxes (passwords excluded).
    """
    inboxes = email_inbox_service.get_inboxes(db, current_manager)

    return DataResponse[list[EmailInboxResponse]](data=inboxes)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_inbox(
    request: CreateEmailInboxRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[EmailInboxResponse]:
    """
    Create a new email inbox configuration.

    - **name**: Display name for the inbox
    - **imap_***: IMAP server configuration
    - **smtp_***: SMTP server configuration
    - **from_address**: Email address for outgoing messages
    - **polling_interval**: Must be 1, 5, or 15 minutes

    Passwords are encrypted before storage.
    """
    inbox = email_inbox_service.create_inbox(
        db=db,
        manager=current_manager,
        name=request.name,
        imap_host=request.imap_host,
        imap_port=request.imap_port,
        imap_username=request.imap_username,
        imap_password=request.imap_password,
        imap_use_ssl=request.imap_use_ssl,
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        smtp_username=request.smtp_username,
        smtp_password=request.smtp_password,
        smtp_use_tls=request.smtp_use_tls,
        from_address=request.from_address,
        polling_interval=request.polling_interval
    )
    return DataResponse[EmailInboxResponse](data=inbox)


@router.get("/{inbox_id}", status_code=status.HTTP_200_OK)
def get_inbox(
    inbox_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[EmailInboxResponse]:
    """
    Get details for a specific email inbox.

    Returns inbox configuration (passwords excluded).
    Returns 404 if inbox not found.
    Returns 403 if inbox belongs to another manager.
    """
    inbox = email_inbox_service.get_inbox(db, current_manager, inbox_id)

    return DataResponse[EmailInboxResponse](data=inbox)


@router.put("/{inbox_id}", status_code=status.HTTP_200_OK)
def update_inbox(
    inbox_id: int,
    request: UpdateEmailInboxRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[EmailInboxResponse]:
    """
    Update email inbox configuration.

    Only provided fields will be updated.
    Passwords will be re-encrypted if changed.
    """
    update_data = request.model_dump(exclude_unset=True)

    inbox = email_inbox_service.update_inbox(
        db=db,
        manager=current_manager,
        inbox_id=inbox_id,
        **update_data
    )
    
    return DataResponse[EmailInboxResponse](data=inbox)


@router.delete("/{inbox_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inbox(
    inbox_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Delete an email inbox.

    Returns 404 if inbox not found.
    Returns 403 if inbox belongs to another manager.
    """
    email_inbox_service.delete_inbox(db, current_manager, inbox_id)
    return None


@router.post("/test", status_code=status.HTTP_200_OK)
def test_connection(
    request: TestConnectionRequest,
    current_manager: Manager = Depends(get_current_manager)
) -> DataResponse[TestConnectionResponse]:
    """
    Test email connection with provided credentials.

    Use this endpoint to test IMAP and SMTP connections before saving
    inbox configuration.

    Returns connection test results for both IMAP and SMTP.
    Status code 200 is returned regardless of test results.
    Check imap_status and smtp_status in response for actual results.
    """
    result = email_inbox_service.test_connection(
        imap_host=request.imap_host,
        imap_port=request.imap_port,
        imap_username=request.imap_username,
        imap_password=request.imap_password,
        imap_use_ssl=request.imap_use_ssl,
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        smtp_username=request.smtp_username,
        smtp_password=request.smtp_password,
        smtp_use_tls=request.smtp_use_tls
    )
    return DataResponse[TestConnectionResponse](data=result)


@router.post("/{inbox_id}/test", status_code=status.HTTP_200_OK)
def test_inbox_connection(
    inbox_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[TestConnectionResponse]:
    """
    Test connection for an existing inbox.

    Uses stored credentials from the database.
    Returns connection test results for both IMAP and SMTP.
    Status code 200 is returned regardless of test results.
    Check imap_status and smtp_status in response for actual results.
    """
    result = email_inbox_service.test_inbox_connection(
        db=db,
        manager=current_manager,
        inbox_id=inbox_id
    )
    return DataResponse[TestConnectionResponse](data=result)
