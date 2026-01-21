"""
Public service for unauthenticated endpoints (ticket creation and viewing).
"""
from typing import Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
import uuid as uuid_lib

from app.models.board import Board
from app.models.ticket import Ticket
from app.models.external_ticket import ExternalTicket
from app.models.manager import Manager
from app.core.security import generate_unique_ticket_uuid


class PublicService:
    """Service for public ticket operations."""

    def get_board_info(self, db: Session, unique_name: str) -> Dict[str, str]:
        """
        Get public board information for the ticket creation form.

        Args:
            db: Database session
            unique_name: Board's unique URL-safe name

        Returns:
            Dictionary with board name and greeting message

        Raises:
            HTTPException: If board not found, archived, or manager suspended
        """
        # Find board with manager info
        board = db.query(Board).join(Manager).filter(
            Board.unique_name == unique_name
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        # Check if manager is suspended
        if board.manager.is_suspended:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=board.manager.suspension_message or "This service is no longer available"
            )

        # Check if board is archived
        if board.is_archived:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This board is no longer accepting new tickets"
            )

        return {
            "name": board.name,
            "greeting_message": board.greeting_message
        }

    def create_ticket(
        self,
        db: Session,
        unique_name: str,
        email: str,
        title: str,
        description: str
    ) -> Dict:
        """
        Create a new ticket via public form.

        Args:
            db: Database session
            unique_name: Board's unique URL-safe name
            email: Creator's email
            title: Ticket title
            description: Ticket description

        Returns:
            Dictionary with ticket UUID, title, and success message

        Raises:
            HTTPException: If board not found, archived, or manager suspended
        """
        # Find board with manager info
        board = db.query(Board).join(Manager).filter(
            Board.unique_name == unique_name
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        # Check if manager is suspended
        if board.manager.is_suspended:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=board.manager.suspension_message or "This service is no longer available"
            )

        # Check if board is archived
        if board.is_archived:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This board is no longer accepting new tickets"
            )

        # Generate unique UUID across both tickets and external_tickets tables
        unique_uuid = generate_unique_ticket_uuid(db)

        # Create ticket
        ticket = Ticket(
            uuid=unique_uuid,
            board_id=board.id,
            title=title,
            description=description,
            creator_email=email,
            source="web",
            state="new"
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Determine from_email for confirmation (prefer exclusive inbox, then first active inbox)
        from_email = None
        if board.exclusive_inbox_id:
            for inbox in board.manager.email_inboxes:
                if inbox.id == board.exclusive_inbox_id and inbox.is_active:
                    from_email = inbox.from_address
                    break
        if not from_email and board.manager.email_inboxes:
            for inbox in board.manager.email_inboxes:
                if inbox.is_active:
                    from_email = inbox.from_address
                    break

        return {
            "uuid": ticket.uuid,
            "title": ticket.title,
            "description": ticket.description,
            "board_name": board.name,
            "creator_email": email,
            "from_email": from_email,
            "message": "Your ticket has been submitted. A confirmation email has been sent."
        }

    def get_ticket_by_uuid(self, db: Session, ticket_uuid: str) -> Dict:
        """
        Get ticket details by UUID (both internal and external tickets).

        Args:
            db: Database session
            ticket_uuid: Ticket UUID string

        Returns:
            Dictionary with ticket details (format depends on ticket type)

        Raises:
            HTTPException: If ticket not found
        """
        # Parse UUID
        try:
            uuid_obj = uuid_lib.UUID(ticket_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid ticket UUID"
            )

        # Try to find internal ticket
        ticket = db.query(Ticket).filter(Ticket.uuid == uuid_obj).first()

        if ticket:
            # Internal ticket - return full details
            return {
                "type": "internal",
                "uuid": ticket.uuid,
                "title": ticket.title,
                "description": ticket.description,
                "state": ticket.state,
                "board_name": ticket.board.name,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "status_changes": [
                    {
                        "previous_state": sc.previous_state,
                        "new_state": sc.new_state,
                        "comment": sc.comment,
                        "created_at": sc.created_at.isoformat()
                    }
                    for sc in ticket.status_changes
                ]
            }

        # Try to find external ticket
        external_ticket = db.query(ExternalTicket).filter(
            ExternalTicket.uuid == uuid_obj
        ).first()

        if external_ticket:
            # External ticket - return minimal info with external URL
            return {
                "type": "external",
                "uuid": external_ticket.uuid,
                "title": external_ticket.title,
                "board_name": external_ticket.board.name,
                "external_url": external_ticket.external_url,
                "platform_type": external_ticket.platform_type,
                "created_at": external_ticket.created_at.isoformat()
            }

        # Ticket not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )


# Singleton instance
public_service = PublicService()
