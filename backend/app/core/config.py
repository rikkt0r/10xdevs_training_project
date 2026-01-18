"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Project
    PROJECT_NAME: str = "Simple Issue Tracker"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "issue_tracker"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Encryption
    ENCRYPTION_KEY: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_PUBLIC_TICKET_PER_MINUTE: int = 20
    RATE_LIMIT_GENERAL_PER_MINUTE: int = 100
    
    # Email
    DUPLICATE_EMAIL_THRESHOLD_MINUTES: int = 60
    DEFAULT_POLLING_INTERVAL: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"

    # SMTP Defaults (optional)
    SMTP_DEFAULT_HOST: str = "localhost"
    SMTP_DEFAULT_PORT: int = 587
    SMTP_DEFAULT_USE_TLS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
