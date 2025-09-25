"""
Hero section API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
# Caching temporarily disabled for deployment

from app.database.postgres import get_db_session
from app.models.schemas import HeroSection, HeroSectionCreate, HeroSectionUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.core.exceptions import NotFoundError
from app.services.postgres_services import PostgresHeroSectionService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db_session)) -> PostgresHeroSectionService:
    """Get service instance."""
    return PostgresHeroSectionService(sessionsuccess=True, message=message)
