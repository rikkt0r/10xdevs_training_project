"""
SQLAlchemy models for the application.
"""
from app.core.database import Base

# Import all models here for Alembic to detect them
from app.models.manager import Manager
from app.models.manager_token import ManagerToken
from app.models.email_inbox import EmailInbox
from app.models.board import Board
from app.models.board_keyword import BoardKeyword
from app.models.ticket import Ticket
from app.models.ticket_status_change import TicketStatusChange
from app.models.external_ticket import ExternalTicket
from app.models.standby_queue_item import StandbyQueueItem
from app.models.processed_email import ProcessedEmail

__all__ = [
    "Base",
    "Manager",
    "ManagerToken",
    "EmailInbox",
    "Board",
    "BoardKeyword",
    "Ticket",
    "TicketStatusChange",
    "ExternalTicket",
    "StandbyQueueItem",
    "ProcessedEmail",
]
