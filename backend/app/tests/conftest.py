"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base
from app.main import app


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test."""
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client
