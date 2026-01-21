"""
Service layer for standby queue operations.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Tuple
import math

from app.models.manager import Manager
from app.models.standby_queue_item import StandbyQueueItem
from app.models.ticket import Ticket
from app.models.board import Board
from app.models.external_ticket import ExternalTicket
from app.schemas.standby_queue import AssignedTicketInfo, RetryExternalInfo
from app.core.security import generate_unique_ticket_uuid


class StandbyQueueService:
    """Service for standby queue operations."""

    def get_queue_items(
        self,
        db: Session,
        manager: Manager,
        page: int = 1,
        limit: int = 25
    ) -> Tuple[list[StandbyQueueItem], int]:
        """
        Get paginated list of standby queue items for manager.

        Args:
            db: Database session
            manager: Current manager
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (items list, total count)
        """
        # Base query
        query = db.query(StandbyQueueItem).filter(
            StandbyQueueItem.manager_id == manager.id
        )

        # Get total count
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        items = query.order_by(StandbyQueueItem.created_at.desc()).offset(offset).limit(limit).all()

        return items, total_count

    def get_queue_item(
        self,
        db: Session,
        manager: Manager,
        item_id: int
    ) -> StandbyQueueItem:
        """
        Get standby queue item by ID.

        Args:
            db: Database session
            manager: Current manager
            item_id: Queue item ID

        Returns:
            StandbyQueueItem instance

        Raises:
            HTTPException: If item not found or doesn't belong to manager
        """
        item = db.query(StandbyQueueItem).filter(
            StandbyQueueItem.id == item_id,
            StandbyQueueItem.manager_id == manager.id
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queue item not found"
            )

        return item

    def assign_to_board(
        self,
        db: Session,
        manager: Manager,
        item_id: int,
        board_id: int
    ) -> AssignedTicketInfo:
        """
        Assign queue item to board (creates ticket).

        Args:
            db: Database session
            manager: Current manager
            item_id: Queue item ID
            board_id: Board ID to assign to

        Returns:
            AssignedTicketInfo with created ticket data

        Raises:
            HTTPException: If item not found, board not found, or board doesn't belong to manager
        """
        # Get queue item
        item = self.get_queue_item(db, manager, item_id)

        # Verify board exists and belongs to manager
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        # Generate unique UUID across both tickets and external_tickets tables
        unique_uuid = generate_unique_ticket_uuid(db)

        # Create ticket from queue item
        ticket = Ticket(
            uuid=unique_uuid,
            board_id=board_id,
            title=item.email_subject,
            description=item.email_body,
            creator_email=item.sender_email,
            source="email",
            state="new"
        )

        db.add(ticket)
        db.flush()

        # Delete queue item
        db.delete(item)
        db.commit()
        db.refresh(ticket)

        return AssignedTicketInfo(
            id=ticket.id,
            uuid=str(ticket.uuid),
            title=ticket.title,
            board_id=ticket.board_id
        )

    def retry_external(
        self,
        db: Session,
        manager: Manager,
        item_id: int
    ) -> RetryExternalInfo:
        """
        Retry external platform creation for queue item.

        Args:
            db: Database session
            manager: Current manager
            item_id: Queue item ID

        Returns:
            RetryExternalInfo with external ticket data

        Raises:
            HTTPException: If item not found, retry failed, or not applicable
        """
        # Get queue item
        item = self.get_queue_item(db, manager, item_id)

        # Verify this is an external creation failure
        if item.failure_reason != "external_creation_failed":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Retry is only applicable for external creation failures"
            )

        # Verify original board exists
        if not item.original_board_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot retry: original board information missing"
            )

        board = db.query(Board).filter(
            Board.id == item.original_board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original board not found"
            )

        # Verify board has external platform configured
        if not board.external_platform_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Board does not have external platform configured"
            )

        # TODO: Implement actual external platform creation
        # For now, this is a placeholder that will fail
        # In a real implementation, this would call the external platform service
        # to create the ticket in Jira/Trello

        # Increment retry count
        item.retry_count += 1
        db.commit()

        # Placeholder error - replace with actual external platform integration
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to create ticket in {board.external_platform_type.capitalize()}: External platform service not yet implemented"
        )

    def delete_queue_item(
        self,
        db: Session,
        manager: Manager,
        item_id: int
    ) -> None:
        """
        Delete (discard) queue item.

        Args:
            db: Database session
            manager: Current manager
            item_id: Queue item ID

        Raises:
            HTTPException: If item not found or doesn't belong to manager
        """
        item = self.get_queue_item(db, manager, item_id)

        db.delete(item)
        db.commit()


# Singleton instance
standby_queue_service = StandbyQueueService()
