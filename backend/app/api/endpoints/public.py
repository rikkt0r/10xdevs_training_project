"""
Public endpoints for unauthenticated ticket creation and viewing.
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.api.responses import DataResponse
from app.core.database import get_db
from app.core.config import settings
from app.core.middleware import limiter
from app.schemas.public import (
    PublicBoardInfoResponse,
    CreatePublicTicketRequest,
    CreatePublicTicketResponse,
    PublicTicketViewResponse,
    PublicExternalTicketViewResponse
)
from app.services.public_service import public_service

router = APIRouter()


@router.get("/boards/{unique_name}", status_code=status.HTTP_200_OK)
def get_board_info(
    unique_name: str,
    db: Session = Depends(get_db)
) -> DataResponse[PublicBoardInfoResponse]:
    """
    Get public board information for the ticket creation form.

    Returns board name and greeting message.

    Errors:
    - 404: Board not found
    - 403: Manager suspended (with suspension message)
    - 410: Board archived
    """
    board_info = public_service.get_board_info(db, unique_name)

    return DataResponse[PublicBoardInfoResponse](data=board_info)


@router.post("/boards/{unique_name}/tickets", status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.RATE_LIMIT_PUBLIC_TICKET_PER_MINUTE}/minute")
async def create_ticket(
    request: Request,
    unique_name: str,
    body: CreatePublicTicketRequest,
    db: Session = Depends(get_db)
) -> DataResponse[CreatePublicTicketResponse]:
    """
    Create a new ticket via public form.

    Creates a ticket and sends confirmation email to the creator.

    Errors:
    - 404: Board not found
    - 403: Manager suspended (with suspension message)
    - 410: Board archived
    """
    ticket_info = public_service.create_ticket(
        db=db,
        unique_name=unique_name,
        email=body.email,
        title=body.title,
        description=body.description
    )

    return DataResponse[CreatePublicTicketResponse](data=ticket_info)


@router.get("/tickets/{ticket_uuid}", status_code=status.HTTP_200_OK)
def get_ticket(
    ticket_uuid: str,
    db: Session = Depends(get_db)
) -> DataResponse[PublicTicketViewResponse | PublicExternalTicketViewResponse]:
    """
    View ticket details by UUID (works for both internal and external tickets).

    For internal tickets: returns full details with status changes.
    For external tickets: returns minimal info with external URL for redirect.

    Errors:
    - 404: Ticket not found or invalid UUID
    """
    ticket_data = public_service.get_ticket_by_uuid(db, ticket_uuid)

    # Return appropriate response based on ticket type
    if ticket_data["type"] == "internal":
        # Remove the 'type' key before returning
        ticket_data_clean = {k: v for k, v in ticket_data.items() if k != "type"}
        return DataResponse[PublicTicketViewResponse](data=ticket_data_clean)
    else:
        # External ticket
        ticket_data_clean = {k: v for k, v in ticket_data.items() if k != "type"}
        return DataResponse[PublicExternalTicketViewResponse](data=ticket_data_clean)
