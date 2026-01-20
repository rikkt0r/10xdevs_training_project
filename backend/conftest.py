"""
Pytest configuration and fixtures.
"""
import os
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
import hashlib

# Set test environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-jwt-token-generation-12345")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DEBUG", "false")


def _test_hash_password(password: str) -> str:
    """Simple password hashing for tests using SHA-256 (NOT for production)."""
    return "sha256$" + hashlib.sha256(password.encode()).hexdigest()


def _test_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification for tests."""
    if hashed_password.startswith("sha256$"):
        expected = "sha256$" + hashlib.sha256(plain_password.encode()).hexdigest()
        return hashed_password == expected
    return False


# Patch security module before importing app modules to avoid bcrypt compatibility issues
import app.core.security as security_module
security_module.hash_password = _test_hash_password
security_module.verify_password = _test_verify_password

# Also patch in auth_service which imports these directly
import app.services.auth_service as auth_service_module
auth_service_module.hash_password = _test_hash_password
auth_service_module.verify_password = _test_verify_password

# Also patch in manager_service which imports these directly
import app.services.manager_service as manager_service_module
manager_service_module.hash_password = _test_hash_password
manager_service_module.verify_password = _test_verify_password

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_string
from app.main import app
from app.models.manager import Manager
from app.models.manager_token import ManagerToken
# Import all models to ensure relationships are resolved
from app.models.email_inbox import EmailInbox
from app.models.board import Board
from app.models.standby_queue_item import StandbyQueueItem

# Use our test versions
hash_password = _test_hash_password
verify_password = _test_verify_password


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine using file-based SQLite."""
    import tempfile
    import os

    # Create a temporary file for the test database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Import all models to ensure they're registered with Base
    from app.models import Manager, ManagerToken, EmailInbox, Board, StandbyQueueItem

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Clean up temp file
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(test_db, test_engine):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_email_service():
    """Mock email service to prevent actual email sending."""
    with patch("app.api.endpoints.auth.email_service") as mock:
        mock.send_verification_email = AsyncMock()
        mock.send_password_reset_email = AsyncMock()
        yield mock


@pytest.fixture
def sample_manager_data():
    """Sample manager registration data."""
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test Manager"
    }


@pytest.fixture
def verified_manager(test_db):
    """Create a verified manager in the database."""
    manager = Manager(
        email="verified@example.com",
        password_hash=hash_password("password123"),
        name="Verified Manager",
        timezone="UTC",
        email_verified_at=datetime.now(timezone.utc),
        is_suspended=False
    )
    test_db.add(manager)
    test_db.commit()
    test_db.refresh(manager)
    return manager


@pytest.fixture
def unverified_manager(test_db):
    """Create an unverified manager in the database."""
    manager = Manager(
        email="unverified@example.com",
        password_hash=hash_password("password123"),
        name="Unverified Manager",
        timezone="UTC",
        email_verified_at=None,
        is_suspended=False
    )
    test_db.add(manager)
    test_db.commit()
    test_db.refresh(manager)
    return manager


@pytest.fixture
def suspended_manager(test_db):
    """Create a suspended manager in the database."""
    manager = Manager(
        email="suspended@example.com",
        password_hash=hash_password("password123"),
        name="Suspended Manager",
        timezone="UTC",
        email_verified_at=datetime.now(timezone.utc),
        is_suspended=True,
        suspension_message="Account suspended for testing"
    )
    test_db.add(manager)
    test_db.commit()
    test_db.refresh(manager)
    return manager


@pytest.fixture
def other_manager(test_db):
    """Create another verified manager for testing ownership checks."""
    manager = Manager(
        email="other@example.com",
        password_hash=hash_password("password123"),
        name="Other Manager",
        timezone="UTC",
        email_verified_at=datetime.now(timezone.utc),
        is_suspended=False
    )
    test_db.add(manager)
    test_db.commit()
    test_db.refresh(manager)
    return manager


@pytest.fixture
def auth_token(verified_manager):
    """Create a valid JWT token for the verified manager."""
    return create_access_token(
        data={"sub": verified_manager.id},
        expires_delta=timedelta(hours=24)
    )


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers with bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def verification_token(test_db, unverified_manager):
    """Create a valid email verification token."""
    import secrets
    token = secrets.token_urlsafe(32)
    token_hash = hash_string(token)

    manager_token = ManagerToken(
        manager_id=unverified_manager.id,
        token_hash=token_hash,
        token_type="email_verification",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    test_db.add(manager_token)
    test_db.commit()

    return token


@pytest.fixture
def expired_verification_token(test_db, unverified_manager):
    """Create an expired email verification token."""
    import secrets
    token = secrets.token_urlsafe(32)
    token_hash = hash_string(token)

    manager_token = ManagerToken(
        manager_id=unverified_manager.id,
        token_hash=token_hash,
        token_type="email_verification",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
    )
    test_db.add(manager_token)
    test_db.commit()

    return token


@pytest.fixture
def password_reset_token(test_db, verified_manager):
    """Create a valid password reset token."""
    import secrets
    token = secrets.token_urlsafe(32)
    token_hash = hash_string(token)

    manager_token = ManagerToken(
        manager_id=verified_manager.id,
        token_hash=token_hash,
        token_type="password_reset",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    test_db.add(manager_token)
    test_db.commit()

    return token


@pytest.fixture
def expired_password_reset_token(test_db, verified_manager):
    """Create an expired password reset token."""
    import secrets
    token = secrets.token_urlsafe(32)
    token_hash = hash_string(token)

    manager_token = ManagerToken(
        manager_id=verified_manager.id,
        token_hash=token_hash,
        token_type="password_reset",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
    )
    test_db.add(manager_token)
    test_db.commit()

    return token
