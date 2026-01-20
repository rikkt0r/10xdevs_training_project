"""
Pydantic schemas for dashboard statistics endpoints.
"""
from pydantic import BaseModel, Field


# Nested response schemas
class TicketsByStateResponse(BaseModel):
    """Ticket counts by state."""
    new: int = Field(..., description="Count of tickets in 'new' state")
    in_progress: int = Field(..., description="Count of tickets in 'in_progress' state")
    closed: int = Field(..., description="Count of tickets in 'closed' state")
    rejected: int = Field(..., description="Count of tickets in 'rejected' state")


class RecentActivityResponse(BaseModel):
    """Recent activity statistics."""
    tickets_created_today: int = Field(..., description="Number of tickets created today")
    tickets_created_this_week: int = Field(..., description="Number of tickets created this week")


# Main response schema
class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    boards_count: int = Field(..., description="Total number of boards (including archived)")
    active_boards_count: int = Field(..., description="Number of active (non-archived) boards")
    standby_queue_count: int = Field(..., description="Number of items in standby queue")
    tickets_by_state: TicketsByStateResponse = Field(..., description="Ticket counts by state")
    recent_activity: RecentActivityResponse = Field(..., description="Recent activity statistics")
