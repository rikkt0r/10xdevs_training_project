"""
Ticket endpoints for managing internal tickets.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api.dependencies import get_current_manager
from app.api.responses import DataResponse, PaginatedDataResponse, PaginationSerializer
from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.ticket import (
    ChangeTicketStateRequest,
    TicketResponse,
    TicketDetailResponse,
    RecentTicketResponse
)
from app.services.ticket_service import ticket_service

router = APIRouter()


@router.get("/recent", status_code=status.HTTP_200_OK)
def get_recent_tickets(
    limit: int = Query(10, ge=1, le=50, description="Number of tickets to return"),
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[list[RecentTicketResponse]]:
    """
    Get recent tickets across all manager's boards.

    Returns the most recently created tickets for dashboard display.
    Maximum 50 tickets can be requested.
    """
    tickets = ticket_service.get_recent_tickets(db, current_manager, limit)

    # Transform to response format
    response_data = []
    for ticket in tickets:
        ticket_dict = {
            'id': ticket.id,
            'uuid': ticket.uuid,
            'title': ticket.title,
            'state': ticket.state,
            'board': {
                'id': ticket.board.id,
                'name': ticket.board.name,
                'unique_name': ticket.board.unique_name
            },
            'created_at': ticket.created_at
        }
        response_data.append(ticket_dict)

    return DataResponse[list[RecentTicketResponse]](data=response_data)


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK)
def get_ticket(
    ticket_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[TicketDetailResponse]:
    """
    Get details for a specific ticket.

    Returns ticket with board information and full status change history.
    Returns 404 if ticket not found or doesn't belong to manager.
    """
    ticket = ticket_service.get_ticket(db, current_manager, ticket_id)

    # Transform to response format
    ticket_dict = {
        'id': ticket.id,
        'uuid': ticket.uuid,
        'board': {
            'id': ticket.board.id,
            'name': ticket.board.name,
            'unique_name': ticket.board.unique_name
        },
        'title': ticket.title,
        'description': ticket.description,
        'state': ticket.state,
        'creator_email': ticket.creator_email,
        'source': ticket.source,
        'created_at': ticket.created_at,
        'updated_at': ticket.updated_at,
        'status_changes': ticket.status_changes
    }

    return DataResponse[TicketDetailResponse](data=ticket_dict)


@router.patch("/{ticket_id}/state", status_code=status.HTTP_200_OK)
def change_ticket_state(
    ticket_id: int,
    request: ChangeTicketStateRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[TicketResponse]:
    """
    Change ticket state.

    Valid state transitions:
    - new → in_progress, rejected
    - in_progress → closed, rejected

    Manager can add an optional comment that will be sent to the ticket creator.
    Returns 422 if state transition is invalid.
    """
    ticket = ticket_service.change_ticket_state(
        db=db,
        manager=current_manager,
        ticket_id=ticket_id,
        new_state=request.state,
        comment=request.comment
    )

    return DataResponse[TicketResponse](data=ticket)
