"""
Better Auth users API endpoints.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import (
    User, 
    UserCreate, 
    UserUpdate, 
    UserList,
    PaginationParams, 
    PaginatedResponse, 
    BaseResponse
)
from app.models.database import UserRole
from app.services.postgres_users import PostgresUserService
from app.core.exceptions import NotFoundError, ValidationException
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> PostgresUserService:
    """Get user service instance."""
    return PostgresUserService(session)


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new Better Auth user with unique email"
)
async def create_user(
    user_data: UserCreate,
    service: PostgresUserService = Depends(get_user_service)
) -> User:
    """Create a new user."""
    try:
        return await service.create(user_data)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all users",
    description="Get paginated list of users with optional filtering"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    email_verified: Optional[bool] = Query(None, description="Filter by email verification"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    service: PostgresUserService = Depends(get_user_service)
) -> PaginatedResponse:
    """Get all users with pagination and filtering."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = UserList(
            role=role,
            emailVerified=email_verified,
            search=search
        )
        
        return await service.list_users(pagination, filters)
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )


@router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="Get user statistics",
    description="Get comprehensive user statistics including counts, verification rates, and role distribution"
)
async def get_user_stats(
    service: PostgresUserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """Get user statistics."""
    try:
        return await service.get_user_stats()
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.get(
    "/search",
    response_model=List[User],
    summary="Search users",
    description="Search users by name or email"
)
async def search_users(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    service: PostgresUserService = Depends(get_user_service)
) -> List[User]:
    """Search users by name or email."""
    try:
        return await service.search_users(q, limit)
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


@router.get(
    "/admins",
    response_model=List[User],
    summary="Get admin users",
    description="Get all users with admin or super_admin roles"
)
async def get_admin_users(
    service: PostgresUserService = Depends(get_user_service)
) -> List[User]:
    """Get all admin users."""
    try:
        return await service.get_admins()
    except Exception as e:
        logger.error(f"Error getting admin users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get admin users"
        )


@router.get(
    "/{user_id}",
    response_model=User,
    summary="Get user by ID",
    description="Get a specific user by their ID"
)
async def get_user(
    user_id: str,
    service: PostgresUserService = Depends(get_user_service)
) -> User:
    """Get a user by ID."""
    try:
        user = await service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.get(
    "/email/{email}",
    response_model=User,
    summary="Get user by email",
    description="Get a specific user by their email address"
)
async def get_user_by_email(
    email: str,
    service: PostgresUserService = Depends(get_user_service)
) -> User:
    """Get a user by email."""
    try:
        user = await service.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.put(
    "/{user_id}",
    response_model=User,
    summary="Update user",
    description="Update user information"
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: PostgresUserService = Depends(get_user_service)
) -> User:
    """Update a user."""
    try:
        return await service.update(user_id, user_data)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.patch(
    "/{user_id}/verify-email",
    response_model=User,
    summary="Verify user email",
    description="Mark user's email as verified"
)
async def verify_user_email(
    user_id: str,
    verified: bool = Query(True, description="Verification status"),
    service: PostgresUserService = Depends(get_user_service)
) -> User:
    """Verify user's email."""
    try:
        return await service.update_email_verification(user_id, verified)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    except Exception as e:
        logger.error(f"Error verifying email for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )


@router.patch(
    "/{user_id}/role",
    response_model=User,
    summary="Update user role",
    description="Update user's role"
)
async def update_user_role(
    user_id: str,
    role: UserRole = Query(..., description="New role"),
    service: PostgresUserService = Depends(get_user_service)
) -> User:
    """Update user's role."""
    try:
        return await service.update_role(user_id, role)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    except Exception as e:
        logger.error(f"Error updating role for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.patch(
    "/bulk/verify-email",
    response_model=List[User],
    summary="Bulk verify emails",
    description="Verify email for multiple users at once"
)
async def bulk_verify_emails(
    user_ids: List[str] = Query(..., description="List of user IDs"),
    verified: bool = Query(True, description="Verification status"),
    service: PostgresUserService = Depends(get_user_service)
) -> List[User]:
    """Bulk verify user emails."""
    try:
        if len(user_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot process more than 100 users at once"
            )
        
        return await service.bulk_update_verification(user_ids, verified)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk verifying emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk verify emails"
        )


@router.delete(
    "/{user_id}",
    response_model=BaseResponse,
    summary="Delete user",
    description="Delete a user by ID"
)
async def delete_user(
    user_id: str,
    service: PostgresUserService = Depends(get_user_service)
) -> BaseResponse:
    """Delete a user."""
    try:
        success = await service.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID '{user_id}' not found"
            )
        
        return BaseResponse(
            success=True,
            message=f"User '{user_id}' deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.delete(
    "/cleanup/unverified",
    response_model=BaseResponse,
    summary="Clean up unverified users",
    description="Delete unverified users older than specified days"
)
async def cleanup_unverified_users(
    days_old: int = Query(30, ge=1, le=365, description="Delete users unverified for this many days"),
    service: PostgresUserService = Depends(get_user_service)
) -> BaseResponse:
    """Clean up old unverified users."""
    try:
        deleted_count = await service.delete_unverified_users(days_old)
        
        return BaseResponse(
            success=True,
            message=f"Deleted {deleted_count} unverified users older than {days_old} days",
            data={"deleted_count": deleted_count}
        )
    except Exception as e:
        logger.error(f"Error cleaning up unverified users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clean up unverified users"
        )


# Health check endpoint for user service
@router.get(
    "/health",
    response_model=BaseResponse,
    summary="User service health check",
    description="Check if the user service is healthy"
)
async def user_service_health(
    service: PostgresUserService = Depends(get_user_service)
) -> BaseResponse:
    """Check user service health."""
    try:
        # Simple health check - try to count users
        stats = await service.get_user_stats()
        
        return BaseResponse(
            success=True,
            message="User service is healthy",
            data={"total_users": stats.get("total_users", 0)}
        )
    except Exception as e:
        logger.error(f"User service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service is unhealthy"
        )
