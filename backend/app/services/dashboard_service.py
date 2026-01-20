"""
Dashboard service for manager dashboard statistics.
"""
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timezone, timedelta

from app.models.manager import Manager
from app.models.board import Board
from app.models.ticket import Ticket
from app.models.standby_queue_item import StandbyQueueItem


class DashboardService:
    """Service for dashboard statistics operations."""

    def get_dashboard_stats(self, db: Session, manager: Manager) -> Dict:
        """
        Get dashboard statistics for a manager.

        Args:
            db: Database session
            manager: Manager instance

        Returns:
            Dictionary with dashboard statistics
        """
        # Get current datetime in UTC
        now = datetime.now(timezone.utc)

        # Calculate start of today (00:00:00 UTC)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        # Calculate start of this week (Monday 00:00:00 UTC)
        # weekday() returns 0 for Monday, 6 for Sunday
        days_since_monday = now.weekday()
        week_start = today_start - timedelta(days=days_since_monday)

        # Count total boards
        boards_count = db.query(func.count(Board.id)).filter(
            Board.manager_id == manager.id
        ).scalar()

        # Count active (non-archived) boards
        active_boards_count = db.query(func.count(Board.id)).filter(
            Board.manager_id == manager.id,
            Board.is_archived == False
        ).scalar()

        # Count standby queue items
        standby_queue_count = db.query(func.count(StandbyQueueItem.id)).filter(
            StandbyQueueItem.manager_id == manager.id
        ).scalar()

        # Count tickets by state across all manager's boards
        # Get all tickets for manager's boards
        tickets_query = db.query(Ticket).join(Board).filter(
            Board.manager_id == manager.id
        )

        # Count by state
        new_count = tickets_query.filter(Ticket.state == 'new').count()
        in_progress_count = tickets_query.filter(Ticket.state == 'in_progress').count()
        closed_count = tickets_query.filter(Ticket.state == 'closed').count()
        rejected_count = tickets_query.filter(Ticket.state == 'rejected').count()

        # Count tickets created today
        tickets_created_today = db.query(func.count(Ticket.id)).join(Board).filter(
            Board.manager_id == manager.id,
            Ticket.created_at >= today_start.replace(tzinfo=None)  # Compare as naive datetime
        ).scalar()

        # Count tickets created this week
        tickets_created_this_week = db.query(func.count(Ticket.id)).join(Board).filter(
            Board.manager_id == manager.id,
            Ticket.created_at >= week_start.replace(tzinfo=None)  # Compare as naive datetime
        ).scalar()

        return {
            "boards_count": boards_count,
            "active_boards_count": active_boards_count,
            "standby_queue_count": standby_queue_count,
            "tickets_by_state": {
                "new": new_count,
                "in_progress": in_progress_count,
                "closed": closed_count,
                "rejected": rejected_count
            },
            "recent_activity": {
                "tickets_created_today": tickets_created_today,
                "tickets_created_this_week": tickets_created_this_week
            }
        }


# Singleton instance
dashboard_service = DashboardService()
