"""
Configuration settings for the Lunaxcode CMS Admin API.
"""

from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import secrets
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Project info
    PROJECT_NAME: str = "Lunaxcode CMS Admin API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "CMS Admin API for Lunaxcode.com - Manage content, pricing, and site settings"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000", "https://lunaxcode.com"]
    
    # Xata Database
    XATA_API_KEY: Optional[str] = None
    XATA_DATABASE_URL: Optional[str] = None
    XATA_BRANCH: str = "main"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300  # 5 minutes default
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v
    
    @validator("DEBUG")
    def validate_debug(cls, v, values):
        environment = values.get("ENVIRONMENT")
        if environment == "production" and v:
            raise ValueError("DEBUG must be False in production")
        return v
    
    @validator("ALLOWED_HOSTS")
    def validate_allowed_hosts(cls, v):
        if not v:
            raise ValueError("ALLOWED_HOSTS cannot be empty")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
