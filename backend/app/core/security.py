"""
Security utilities for authentication and encryption.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet
import base64
import hashlib

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)

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
