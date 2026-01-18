"""
SQLAlchemy models for the application.
"""
from app.core.database import Base

# Import all models here for Alembic to detect them
from app.models.manager import Manager
from app.models.manager_token import ManagerToken

__all__ = ["Base", "Manager", "ManagerToken"]
