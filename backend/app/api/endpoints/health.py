"""
Health check endpoint for monitoring application status.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import engine
from app.schemas.health import HealthyResponse, UnhealthyResponse, ComponentStatus

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        200: Application is healthy
        503: Application is unhealthy (with details)
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    is_healthy = True
    details = {}

    # Check database connectivity
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        db_status = "healthy"
        db_message = None
    except Exception as e:
        is_healthy = False
        db_status = "unhealthy"
        db_message = str(e)

    if is_healthy:
        response = HealthyResponse(
            status="healthy",
            timestamp=timestamp
        )
        return JSONResponse(
            status_code=200,
            content=response.model_dump()
        )
    else:
        details["database"] = ComponentStatus(
            status=db_status,
            message=db_message
        )

        response = UnhealthyResponse(
            status="unhealthy",
            timestamp=timestamp,
            details=details
        )
        return JSONResponse(
            status_code=503,
            content=response.model_dump()
        )
