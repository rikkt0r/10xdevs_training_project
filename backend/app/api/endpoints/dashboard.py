"""
Dashboard endpoints for manager statistics.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_manager
from app.api.responses import DataResponse
from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/stats", status_code=status.HTTP_200_OK)
def get_dashboard_stats(
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
) -> DataResponse[DashboardStatsResponse]:
    """
    Get dashboard statistics for the authenticated manager.

    Returns:
    - Total boards count (including archived)
    - Active boards count (non-archived)
    - Standby queue count
    - Ticket counts by state (new, in_progress, closed, rejected)
    - Recent activity (tickets created today and this week)
    """
    stats = dashboard_service.get_dashboard_stats(db, current_manager)

    return DataResponse[DashboardStatsResponse](data=stats)
