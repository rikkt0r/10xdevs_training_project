"""
Pydantic schemas for health check endpoint.
"""
from pydantic import BaseModel
from typing import Optional, Dict


class ComponentStatus(BaseModel):
    """Status of a single component."""
    status: str
    message: Optional[str] = None


class HealthyResponse(BaseModel):
    """Response when application is healthy."""
    status: str = "healthy"
    timestamp: str


class UnhealthyResponse(BaseModel):
    """Response when application is unhealthy."""
    status: str = "unhealthy"
    timestamp: str
    details: Dict[str, ComponentStatus]
