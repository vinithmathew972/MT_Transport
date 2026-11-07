import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Mother Theresa Transport"
    APP_TAGLINE: str = "Safe Journey... Stronger Tomorrow..."
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mtt-super-secret-key-transport-2026-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days session
    
    # Database URL: fallback to SQLite if PostgreSQL is not provided
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./transport.db")
    
    # Default Owner setup
    DEFAULT_OWNER_USERNAME: str = os.getenv("DEFAULT_OWNER_USERNAME", "owner")
    DEFAULT_OWNER_PASSWORD: str = os.getenv("DEFAULT_OWNER_PASSWORD", "mtt2026")
    DEFAULT_OWNER_NAME: str = os.getenv("DEFAULT_OWNER_NAME", "Transport Owner")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
