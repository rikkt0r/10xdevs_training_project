"""
Ticket service for managing internal tickets.
"""
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from datetime import datetime

from app.models.ticket import Ticket
from app.models.ticket_status_change import TicketStatusChange
from app.models.board import Board
from app.models.manager import Manager


class TicketService:
    """Service for ticket operations."""

    # Valid state transitions
    STATE_TRANSITIONS = {
        'new': ['in_progress', 'rejected'],
        'in_progress': ['closed', 'rejected'],
        'closed': [],
        'rejected': []
    }

    def get_board_tickets(
        self,
        db: Session,
        manager: Manager,
        board_id: int,
        page: int = 1,
        limit: int = 25,
        state: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[Ticket], int]:
        """
        Get tickets for a board with filtering, pagination, and sorting.

        Args:
            db: Database session
            manager: Manager instance
            board_id: Board ID
            page: Page number (1-indexed)
            limit: Items per page
            state: Filter by state (comma-separated for multiple)
            title: Search in title (partial match)
            description: Search in description (partial match)
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)
            sort_by: Sort field
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Tuple of (list of tickets, total count)

        Raises:
            HTTPException: If board not found or doesn't belong to manager
        """
        # Verify board belongs to manager
        board = db.query(Board).filter(
            Board.id == board_id,
            Board.manager_id == manager.id
        ).first()

        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Board {board_id} not found"
            )

        # Build query
        query = db.query(Ticket).filter(Ticket.board_id == board_id)

        # Apply filters
        if state:
            states = [s.strip() for s in state.split(',')]
            query = query.filter(Ticket.state.in_(states))

        if title:
            query = query.filter(Ticket.title.ilike(f'%{title}%'))

        if description:
            query = query.filter(Ticket.description.ilike(f'%{description}%'))

        if date_from:
            query = query.filter(Ticket.created_at >= date_from)

        if date_to:
            query = query.filter(Ticket.created_at <= date_to)

        # Get total count before pagination
        total_count = query.count()

        # Apply sorting
        sort_column = getattr(Ticket, sort_by, Ticket.created_at)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        offset = (page - 1) * limit
        tickets = query.offset(offset).limit(limit).all()

        return tickets, total_count

    def get_ticket(self, db: Session, manager: Manager, ticket_id: int) -> Ticket:
        """
        Get a specific ticket by ID.

        Args:
            db: Database session
            manager: Manager instance
            ticket_id: Ticket ID

        Returns:
            Ticket instance with board and status_changes loaded

        Raises:
            HTTPException: If ticket not found or doesn't belong to manager's board
        """
        ticket = db.query(Ticket).join(Board).filter(
            Ticket.id == ticket_id,
            Board.manager_id == manager.id
        ).first()

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found"
            )

        return ticket

    def change_ticket_state(
        self,
        db: Session,
        manager: Manager,
        ticket_id: int,
        new_state: str,
        comment: Optional[str] = None
    ) -> Ticket:
        """
        Change ticket state with validation.

        Creates a status change record and updates the ticket.

        Args:
            db: Database session
            manager: Manager instance
            ticket_id: Ticket ID
            new_state: New state
            comment: Optional manager comment

        Returns:
            Updated Ticket instance

        Raises:
            HTTPException: If ticket not found, invalid transition, or doesn't belong to manager
        """
        # Get ticket
        ticket = db.query(Ticket).join(Board).filter(
            Ticket.id == ticket_id,
            Board.manager_id == manager.id
        ).first()

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found"
            )

        # Validate state transition
        current_state = ticket.state
        if new_state not in self.STATE_TRANSITIONS.get(current_state, []):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot transition from '{current_state}' to '{new_state}'"
            )

        # Create status change record
        status_change = TicketStatusChange(
            ticket_id=ticket.id,
            previous_state=current_state,
            new_state=new_state,
            comment=comment
        )
        db.add(status_change)

        # Update ticket state
        ticket.state = new_state
        ticket.updated_at = func.now()

        db.commit()
        db.refresh(ticket)

        return ticket

    def get_recent_tickets(
        self,
        db: Session,
        manager: Manager,
        limit: int = 10
    ) -> List[Ticket]:
        """
        Get recent tickets across all manager's boards.

        Args:
            db: Database session
            manager: Manager instance
            limit: Maximum number of tickets to return

        Returns:
            List of recent Ticket instances
        """
        tickets = db.query(Ticket).join(Board).filter(
            Board.manager_id == manager.id
        ).order_by(Ticket.created_at.desc()).limit(limit).all()

        return tickets


# Singleton instance
ticket_service = TicketService()
