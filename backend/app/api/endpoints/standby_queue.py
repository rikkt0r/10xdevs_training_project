"""
Standby queue endpoints for managing unrouted emails.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import math

from app.api.dependencies import get_current_manager
from app.api.responses import DataResponse, PaginatedDataResponse, PaginationSerializer, DataWithMessageResponse, MessageResponse
from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.standby_queue import (
    StandbyQueueItemResponse,
    AssignToBoardRequest,
    AssignToBoardResponse,
    RetryExternalResponse
)
from app.services.standby_queue_service import standby_queue_service

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_queue_items(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Items per page"),
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> PaginatedDataResponse[list[StandbyQueueItemResponse]]:
    """
    List all standby queue items for the authenticated manager.

    Items are emails that couldn't be automatically routed to a board:
    - no_keyword_match: Email subject didn't match any board keywords
    - external_creation_failed: External platform ticket creation failed
    - no_board_match: No board found for exclusive inbox

    Returns paginated list sorted by creation date (newest first).
    """
    items, total_count = standby_queue_service.get_queue_items(
        db=db,
        manager=current_manager,
        page=page,
        limit=limit
    )

    # Calculate total pages
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 0

    pagination = PaginationSerializer(
        page=page,
        limit=limit,
        total_items=total_count,
        total_pages=total_pages
    )

    return PaginatedDataResponse[list[StandbyQueueItemResponse]](
        data=items,
        pagination=pagination
    )


@router.get("/{item_id}", status_code=status.HTTP_200_OK)
def get_queue_item(
    item_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[StandbyQueueItemResponse]:
    """
    Get details for a specific standby queue item.

    Returns 404 if item not found or doesn't belong to manager.
    """
    item = standby_queue_service.get_queue_item(db, current_manager, item_id)

    return DataResponse[StandbyQueueItemResponse](data=item)


@router.post("/{item_id}/assign", status_code=status.HTTP_200_OK)
def assign_to_board(
    item_id: int,
    request: AssignToBoardRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataWithMessageResponse[AssignToBoardResponse]:
    """
    Assign queue item to an internal board (creates ticket).

    Creates a new ticket from the queue item email data and removes
    the item from the standby queue.

    Returns 404 if item or board not found.
    Returns 403 if board doesn't belong to manager.
    """
    ticket_info = standby_queue_service.assign_to_board(
        db=db,
        manager=current_manager,
        item_id=item_id,
        board_id=request.board_id
    )

    # Pass dict - Pydantic will convert to AssignToBoardResponse
    response_data = {"ticket": ticket_info}

    return DataWithMessageResponse[AssignToBoardResponse](
        data=response_data,
        message="Ticket created successfully"
    )


@router.post("/{item_id}/retry", status_code=status.HTTP_200_OK)
def retry_external(
    item_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataWithMessageResponse[RetryExternalResponse]:
    """
    Retry external platform creation for a queue item.

    Only applicable for items with failure_reason='external_creation_failed'.
    Attempts to create the ticket in the configured external platform (Jira/Trello).

    Returns 404 if item not found.
    Returns 422 if retry is not applicable or external creation fails again.
    """
    external_info = standby_queue_service.retry_external(
        db=db,
        manager=current_manager,
        item_id=item_id
    )

    # Pass dict - Pydantic will convert to RetryExternalResponse
    response_data = {"external_ticket": external_info}

    return DataWithMessageResponse[RetryExternalResponse](
        data=response_data,
        message="External ticket created successfully"
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_queue_item(
    item_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Delete (discard) a queue item.

    Permanently removes the item from the standby queue without creating a ticket.

    Returns 404 if item not found or doesn't belong to manager.
    """
    standby_queue_service.delete_queue_item(db, current_manager, item_id)
    return None
