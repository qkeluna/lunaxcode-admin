"""
Contact info API endpoints.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import ContactInfo, ContactInfoCreate, ContactInfoUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.models.database import ContactType
from app.services.postgres_services import PostgresContactInfoService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db_session)) -> PostgresContactInfoService:
    """Get service instance."""
    return PostgresContactInfoService(session)


@router.post(
    "/",
    response_model=ContactInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact info"
)
async def create_contact_info(
    contact_data: ContactInfoCreate,
    service: PostgresContactInfoService = Depends(get_service)
) -> ContactInfo:
    """Create a new contact info."""
    try:
        return await service.create(contact_data)
    except Exception as e:
        logger.error(f"Error creating contact info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contact info"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all contact info"
)
async def get_contact_info(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    contact_type: ContactType = Query(None, description="Filter by contact type"),
    active_only: bool = Query(True),
    service: PostgresContactInfoService = Depends(get_service)
) -> PaginatedResponse:
    """Get all contact info with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = {}
        if contact_type:
            filters["type"] = contact_type
        if active_only:
            filters["is_active"] = True
        
        return await service.get_all(
            pagination=pagination,
            filters=filters or None
        )
    except Exception as e:
        logger.error(f"Error getting contact info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact info"
        )


@router.get(
    "/type/{contact_type}",
    response_model=List[ContactInfo],
    summary="Get contact info by type"
)
async def get_contact_info_by_type(
    contact_type: ContactType,
    service: PostgresContactInfoService = Depends(get_service)
) -> List[ContactInfo]:
    """Get contact info by type."""
    try:
        return await service.get_by_type(contact_type)
    except Exception as e:
        logger.error(f"Error getting contact info by type {contact_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contact info for type {contact_type}"
        )


@router.get(
    "/primary",
    response_model=List[ContactInfo],
    summary="Get primary contact info"
)
async def get_primary_contact_info(
    service: PostgresContactInfoService = Depends(get_service)
) -> List[ContactInfo]:
    """Get primary contact info."""
    try:
        return await service.get_primary_contacts()
    except Exception as e:
        logger.error(f"Error getting primary contact info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve primary contact info"
        )


@router.get(
    "/{record_id}",
    response_model=ContactInfo,
    summary="Get contact info by ID"
)
async def get_contact_info_by_id(
    record_id: str,
    service: PostgresContactInfoService = Depends(get_service)
) -> ContactInfo:
    """Get contact info by ID."""
    try:
        contact = await service.get_by_id(record_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact info with ID '{record_id}' not found"
            )
        return contact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contact info {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact info"
        )


@router.patch(
    "/{record_id}",
    response_model=ContactInfo,
    summary="Update contact info"
)
async def update_contact_info(
    record_id: str,
    contact_data: ContactInfoUpdate,
    service: PostgresContactInfoService = Depends(get_service)
) -> ContactInfo:
    """Update contact info."""
    try:
        return await service.update(record_id, contact_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating contact info {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact info"
        )


@router.delete(
    "/{record_id}",
    response_model=BaseResponse,
    summary="Delete contact info"
)
async def delete_contact_info(
    record_id: str,
    hard_delete: bool = Query(False, description="Perform hard delete"),
    service: PostgresContactInfoService = Depends(get_service)
) -> BaseResponse:
    """Delete contact info."""
    try:
        if hard_delete:
            success = await service.delete(record_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Contact info with ID '{record_id}' not found"
                )
            message = "Contact info deleted permanently"
        else:
            await service.update(record_id, ContactInfoUpdate(is_active=False))
            message = "Contact info deactivated"
        
        return BaseResponse(success=True, message=message)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting contact info {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contact info"
        )