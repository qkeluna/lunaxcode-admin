"""
Testimonials API endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
# Caching temporarily disabled for deployment

from app.database.postgres import get_db_session
from app.models.schemas import Testimonial, TestimonialCreate, TestimonialUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.models.database import ProjectType
from app.core.exceptions import NotFoundError
from app.services.postgres_services import PostgresTestimonialsService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db_session)) -> PostgresTestimonialsService:
    """Get service instance."""
    return PostgresTestimonialsService(sessionsuccess=True, message=message)
