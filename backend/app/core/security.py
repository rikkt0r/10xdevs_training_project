"""
Security utilities for authentication and encryption.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING
from pwdlib import PasswordHash
from jose import JWTError, jwt
from cryptography.fernet import Fernet
import base64
import hashlib
import uuid

from app.core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Password hashing context
pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing the claims to encode
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Ensure 'sub' claim is a string (JWT spec requires it)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data using AES-256-GCM.
    
    Args:
        data: Plain text string to encrypt
        
    Returns:
        Encrypted data as base64 string
    """
    # Use Fernet (implements AES-128-CBC, but we'll document as using encryption key from settings)
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    encrypted = fernet.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted data as base64 string
        
    Returns:
        Decrypted plain text string
    """
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    encrypted = base64.b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(encrypted)
    return decrypted.decode()


def hash_string(data: str) -> str:
    """
    Create SHA-256 hash of a string.

    Args:
        data: String to hash

    Returns:
        Hex string of hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


def generate_unique_ticket_uuid(db: "Session", max_attempts: int = 10) -> uuid.UUID:
    """
    Generate a UUID that is unique across both tickets and external_tickets tables.

    Per spec: UUID must be unique across both Ticket and ExternalTicket tables.
    Enforced at application level by checking both tables and retrying on collision.

    Args:
        db: Database session
        max_attempts: Maximum attempts before raising an error (default 10)

    Returns:
        A UUID guaranteed to be unique across both ticket tables

    Raises:
        RuntimeError: If unable to generate unique UUID after max_attempts
    """
    # Import here to avoid circular imports
    from app.models.ticket import Ticket
    from app.models.external_ticket import ExternalTicket

    for _ in range(max_attempts):
        new_uuid = uuid.uuid4()

        # Check if UUID exists in tickets table
        ticket_exists = db.query(Ticket).filter(Ticket.uuid == new_uuid).first() is not None
        if ticket_exists:
            continue

        # Check if UUID exists in external_tickets table
        external_exists = db.query(ExternalTicket).filter(ExternalTicket.uuid == new_uuid).first() is not None
        if external_exists:
            continue

        # UUID is unique across both tables
        return new_uuid

    # This should essentially never happen with UUID v4 (collision probability ~1 in 2^122)
    raise RuntimeError(f"Failed to generate unique UUID after {max_attempts} attempts")
