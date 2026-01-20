"""
Board endpoints for managing ticket boards.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import math

from app.api.dependencies import get_current_manager
from app.api.responses import DataResponse, MessageResponse, PaginatedDataResponse, PaginationSerializer
from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.board import (
    CreateBoardRequest,
    UpdateBoardRequest,
    BoardResponse,
    BoardWithTicketCountsResponse,
    TestExternalConnectionResponse,
    CreateKeywordRequest,
    KeywordResponse
)
from app.schemas.ticket import TicketResponse
from app.services.board_service import board_service
from app.services.ticket_service import ticket_service

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def list_boards(
    include_archived: bool = Query(False, description="Include archived boards"),
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[list[BoardWithTicketCountsResponse]]:
    """
    List all boards for the authenticated manager.

    Returns boards with ticket counts by state.
    By default, archived boards are excluded.
    """
    boards_with_counts = board_service.get_boards(db, current_manager, include_archived)

    # Transform to response format
    response_data = []
    for board, ticket_counts in boards_with_counts:
        board_dict = {
            'id': board.id,
            'name': board.name,
            'unique_name': board.unique_name,
            'greeting_message': board.greeting_message,
            'is_archived': board.is_archived,
            'external_platform_type': board.external_platform_type,
            'exclusive_inbox_id': board.exclusive_inbox_id,
            'ticket_counts': ticket_counts,
            'created_at': board.created_at,
            'updated_at': board.updated_at
        }
        response_data.append(board_dict)

    return DataResponse[list[BoardWithTicketCountsResponse]](data=response_data)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_board(
    request: CreateBoardRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[BoardResponse]:
    """
    Create a new board.

    - **name**: Display name for the board
    - **unique_name**: URL-safe slug for public form (globally unique)
    - **greeting_message**: Optional message shown above public form
    - **exclusive_inbox_id**: Optional exclusive inbox assignment
    - **external_platform_type**: Optional 'jira' or 'trello'
    - **external_platform_config**: Platform-specific configuration (required if platform_type set)

    Returns the created board.
    """
    board = board_service.create_board(
        db=db,
        manager=current_manager,
        name=request.name,
        unique_name=request.unique_name,
        greeting_message=request.greeting_message,
        exclusive_inbox_id=request.exclusive_inbox_id,
        external_platform_type=request.external_platform_type,
        external_platform_config=request.external_platform_config
    )

    return DataResponse[BoardResponse](data=board)


@router.get("/{board_id}", status_code=status.HTTP_200_OK)
def get_board(
    board_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[BoardWithTicketCountsResponse]:
    """
    Get details for a specific board.

    Returns board configuration with ticket counts by state.
    Returns 404 if board not found.
    Returns 403 if board belongs to another manager.
    """
    board, ticket_counts = board_service.get_board(db, current_manager, board_id)

    board_dict = {
        'id': board.id,
        'name': board.name,
        'unique_name': board.unique_name,
        'greeting_message': board.greeting_message,
        'is_archived': board.is_archived,
        'external_platform_type': board.external_platform_type,
        'exclusive_inbox_id': board.exclusive_inbox_id,
        'ticket_counts': ticket_counts,
        'created_at': board.created_at,
        'updated_at': board.updated_at
    }

    return DataResponse[BoardWithTicketCountsResponse](data=board_dict)


@router.put("/{board_id}", status_code=status.HTTP_200_OK)
def update_board(
    board_id: int,
    request: UpdateBoardRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[BoardResponse]:
    """
    Update board configuration.

    Only provided fields will be updated.
    """
    update_data = request.model_dump(exclude_unset=True)

    board = board_service.update_board(
        db=db,
        manager=current_manager,
        board_id=board_id,
        **update_data
    )

    return DataResponse[BoardResponse](data=board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    board_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Delete a board.

    Only allowed if all tickets are in "rejected" state or no tickets exist.
    Returns 422 if board has active tickets (must archive instead).
    """
    board_service.delete_board(db, current_manager, board_id)
    return None


@router.post("/{board_id}/archive", status_code=status.HTTP_200_OK)
def archive_board(
    board_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[BoardResponse]:
    """
    Archive a board.

    Archived boards do not accept new tickets via public forms.
    Existing tickets remain accessible via secret links.
    """
    board = board_service.archive_board(db, current_manager, board_id)

    return DataResponse[BoardResponse](data=board)


@router.post("/{board_id}/test-external", status_code=status.HTTP_200_OK)
def test_external_connection(
    board_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[TestExternalConnectionResponse]:
    """
    Test external platform connection for a configured board.

    Tests the connection using stored credentials.
    Returns 422 if no external platform is configured.
    """
    result = board_service.test_external_connection(db, current_manager, board_id)

    return DataResponse[TestExternalConnectionResponse](data=result)


# Board Tickets endpoint
@router.get("/{board_id}/tickets", status_code=status.HTTP_200_OK)
def list_board_tickets(
    board_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(25, ge=1, le=100, description="Items per page (10, 25, 50)"),
    state: Optional[str] = Query(None, description="Filter by state (comma-separated)"),
    title: Optional[str] = Query(None, description="Search in title (partial match)"),
    description: Optional[str] = Query(None, description="Search in description (partial match)"),
    date_from: Optional[datetime] = Query(None, description="Filter by creation date (from)"),
    date_to: Optional[datetime] = Query(None, description="Filter by creation date (to)"),
    sort_by: str = Query('created_at', description="Sort field: created_at, title, state, updated_at"),
    sort_order: str = Query('desc', description="Sort order: asc, desc"),
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> PaginatedDataResponse[list[TicketResponse]]:
    """
    List tickets for a board with filtering, sorting, and pagination.

    **Query parameters:**
    - **page**: Page number (1-indexed)
    - **limit**: Items per page (10, 25, 50)
    - **state**: Filter by state (comma-separated for multiple, e.g., "new,in_progress")
    - **title**: Search in title (partial match, case-insensitive)
    - **description**: Search in description (partial match, case-insensitive)
    - **date_from**: Filter by creation date (ISO 8601 format)
    - **date_to**: Filter by creation date (ISO 8601 format)
    - **sort_by**: Sort field (created_at, title, state, updated_at)
    - **sort_order**: Sort order (asc, desc)

    Returns paginated list of tickets with pagination metadata.
    """
    tickets, total_count = ticket_service.get_board_tickets(
        db=db,
        manager=current_manager,
        board_id=board_id,
        page=page,
        limit=limit,
        state=state,
        title=title,
        description=description,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Calculate total pages
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 0

    pagination = PaginationSerializer(
        page=page,
        limit=limit,
        total_items=total_count,
        total_pages=total_pages
    )

    return PaginatedDataResponse[list[TicketResponse]](
        data=tickets,
        pagination=pagination
    )


# Board Keyword endpoints
@router.get("/{board_id}/keywords", status_code=status.HTTP_200_OK)
def list_keywords(
    board_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[list[KeywordResponse]]:
    """
    List all keywords for a board.

    Returns keywords for email subject matching.
    Returns 404 if board not found or doesn't belong to manager.
    """
    keywords = board_service.get_keywords(db, current_manager, board_id)

    return DataResponse[list[KeywordResponse]](data=keywords)


@router.post("/{board_id}/keywords", status_code=status.HTTP_201_CREATED)
def create_keyword(
    board_id: int,
    request: CreateKeywordRequest,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[KeywordResponse]:
    """
    Add a keyword to a board.

    Keywords are used to route incoming emails to this board based on subject matching.
    Keywords must be unique across all manager's boards (case-insensitive).

    Returns 409 if keyword already exists on another board.
    """
    keyword = board_service.create_keyword(
        db=db,
        manager=current_manager,
        board_id=board_id,
        keyword=request.keyword
    )

    return DataResponse[KeywordResponse](data=keyword)


@router.delete("/{board_id}/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    board_id: int,
    keyword_id: int,
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    """
    Remove a keyword from a board.

    Returns 404 if board or keyword not found.
    """
    board_service.delete_keyword(db, current_manager, board_id, keyword_id)
    return None
