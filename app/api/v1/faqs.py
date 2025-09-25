"""
FAQs API endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import FAQ, FAQCreate, FAQUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.models.database import FAQCategory
from app.services.postgres_services import PostgresFAQService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db_session)) -> PostgresFAQService:
    """Get service instance."""
    return PostgresFAQService(session)


@router.post(
    "/",
    response_model=FAQ,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new FAQ"
)
async def create_faq(
    faq_data: FAQCreate,
    service: PostgresFAQService = Depends(get_service)
) -> FAQ:
    """Create a new FAQ."""
    try:
        return await service.create(faq_data)
    except Exception as e:
        logger.error(f"Error creating FAQ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create FAQ"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all FAQs"
)
async def get_faqs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[FAQCategory] = Query(None, description="Filter by category"),
    active_only: bool = Query(True),
    service: PostgresFAQService = Depends(get_service)
) -> PaginatedResponse:
    """Get all FAQs with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = {}
        if category:
            filters["category"] = category
        if active_only:
            filters["is_active"] = True
        
        return await service.get_all(
            pagination=pagination,
            filters=filters or None
        )
    except Exception as e:
        logger.error(f"Error getting FAQs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve FAQs"
        )


@router.get(
    "/category/{category}",
    response_model=List[FAQ],
    summary="Get FAQs by category"
)
async def get_faqs_by_category(
    category: FAQCategory,
    service: PostgresFAQService = Depends(get_service)
) -> List[FAQ]:
    """Get FAQs by category."""
    try:
        return await service.get_by_category(category)
    except Exception as e:
        logger.error(f"Error getting FAQs by category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve FAQs for category {category}"
        )


@router.get(
    "/{record_id}",
    response_model=FAQ,
    summary="Get FAQ by ID"
)
async def get_faq(
    record_id: str,
    service: PostgresFAQService = Depends(get_service)
) -> FAQ:
    """Get FAQ by ID."""
    try:
        faq = await service.get_by_id(record_id)
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID '{record_id}' not found"
            )
        return faq
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQ {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve FAQ"
        )


@router.patch(
    "/{record_id}",
    response_model=FAQ,
    summary="Update FAQ"
)
async def update_faq(
    record_id: str,
    faq_data: FAQUpdate,
    service: PostgresFAQService = Depends(get_service)
) -> FAQ:
    """Update FAQ."""
    try:
        return await service.update(record_id, faq_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating FAQ {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update FAQ"
        )


@router.delete(
    "/{record_id}",
    response_model=BaseResponse,
    summary="Delete FAQ"
)
async def delete_faq(
    record_id: str,
    hard_delete: bool = Query(False, description="Perform hard delete"),
    service: PostgresFAQService = Depends(get_service)
) -> BaseResponse:
    """Delete FAQ."""
    try:
        if hard_delete:
            success = await service.delete(record_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"FAQ with ID '{record_id}' not found"
                )
            message = "FAQ deleted permanently"
        else:
            await service.update(record_id, FAQUpdate(is_active=False))
            message = "FAQ deactivated"
        
        return BaseResponse(success=True, message=message)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting FAQ {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete FAQ"
        )