"""
PostgreSQL service for Better Auth users management.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.database import User as UserModel, UserRole
from app.models.schemas import (
    User, UserCreate, UserUpdate, UserList,
    PaginationParams, PaginatedResponse
)
from app.services.postgres_base import PostgresBaseService
from app.core.exceptions import ValidationException, NotFoundError, DatabaseError

logger = logging.getLogger(__name__)


class PostgresUserService(PostgresBaseService[UserModel, UserCreate, UserUpdate, User]):
    """PostgreSQL service for Better Auth users."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            model=UserModel,
            response_schema=User,
            session=session
        )

    async def create(self, obj_in: UserCreate) -> User:
        """Create a new user with duplicate email check."""
        try:
            # Check if user with this email already exists
            existing_user = await self.get_by_email(obj_in.email)
            if existing_user:
                raise ValidationException(
                    f"User with email '{obj_in.email}' already exists",
                    field="email"
                )
            
            return await super().create(obj_in)
            
        except ValidationException:
            raise
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise ValidationException(
                    f"User with email '{obj_in.email}' already exists",
                    field="email"
                )
            raise DatabaseError("Failed to create user due to data constraint", operation="create")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating user: {e}")
            raise DatabaseError("Failed to create user", operation="create")

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            stmt = select(self.model).where(self.model.email == email.lower())
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if db_obj:
                return self.response_schema.from_orm(db_obj)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise DatabaseError("Failed to get user by email", operation="get_by_email")

    async def update_email_verification(self, user_id: str, verified: bool = True) -> User:
        """Update user email verification status."""
        try:
            stmt = select(self.model).where(self.model.id == user_id)
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                raise NotFoundError("User", user_id)
            
            db_obj.emailVerified = verified
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return self.response_schema.from_orm(db_obj)
            
        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating email verification for user {user_id}: {e}")
            raise DatabaseError("Failed to update email verification", operation="update_verification")

    async def update_role(self, user_id: str, role: UserRole) -> User:
        """Update user role."""
        try:
            stmt = select(self.model).where(self.model.id == user_id)
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                raise NotFoundError("User", user_id)
            
            db_obj.role = role
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return self.response_schema.from_orm(db_obj)
            
        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating role for user {user_id}: {e}")
            raise DatabaseError("Failed to update user role", operation="update_role")

    async def list_users(
        self,
        pagination: PaginationParams,
        filters: Optional[UserList] = None
    ) -> PaginatedResponse:
        """List users with filtering and pagination."""
        try:
            # Build base query
            stmt = select(self.model)
            count_stmt = select(func.count(self.model.id))
            
            # Apply filters
            if filters:
                conditions = []
                
                if filters.role:
                    conditions.append(self.model.role == filters.role)
                
                if filters.emailVerified is not None:
                    conditions.append(self.model.emailVerified == filters.emailVerified)
                
                if filters.search:
                    search_term = f"%{filters.search.lower()}%"
                    conditions.append(
                        or_(
                            func.lower(self.model.name).like(search_term),
                            func.lower(self.model.email).like(search_term)
                        )
                    )
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
                    count_stmt = count_stmt.where(and_(*conditions))
            
            # Get total count
            count_result = await self.session.execute(count_stmt)
            total = count_result.scalar()
            
            # Apply pagination and ordering
            stmt = stmt.order_by(self.model.created_at.desc())
            stmt = stmt.offset(pagination.offset).limit(pagination.size)
            
            # Execute query
            result = await self.session.execute(stmt)
            db_objs = result.scalars().all()
            
            # Convert to response schemas
            items = [self.response_schema.from_orm(obj) for obj in db_objs]
            
            return PaginatedResponse.create(
                items=items,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise DatabaseError("Failed to list users", operation="list")

    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            # Total users
            total_stmt = select(func.count(self.model.id))
            total_result = await self.session.execute(total_stmt)
            total_users = total_result.scalar()
            
            # Verified users
            verified_stmt = select(func.count(self.model.id)).where(
                self.model.emailVerified == True
            )
            verified_result = await self.session.execute(verified_stmt)
            verified_users = verified_result.scalar()
            
            # Users by role
            role_stmt = select(
                self.model.role,
                func.count(self.model.id).label('count')
            ).group_by(self.model.role)
            role_result = await self.session.execute(role_stmt)
            role_stats = {row.role: row.count for row in role_result}
            
            # Recent registrations (last 30 days)
            recent_stmt = select(func.count(self.model.id)).where(
                self.model.created_at >= func.now() - func.interval('30 days')
            )
            recent_result = await self.session.execute(recent_stmt)
            recent_registrations = recent_result.scalar()
            
            return {
                "total_users": total_users,
                "verified_users": verified_users,
                "unverified_users": total_users - verified_users,
                "verification_rate": round((verified_users / total_users * 100), 2) if total_users > 0 else 0,
                "users_by_role": role_stats,
                "recent_registrations": recent_registrations
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise DatabaseError("Failed to get user statistics", operation="stats")

    async def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by name or email."""
        try:
            search_term = f"%{query.lower()}%"
            stmt = select(self.model).where(
                or_(
                    func.lower(self.model.name).like(search_term),
                    func.lower(self.model.email).like(search_term)
                )
            ).order_by(self.model.created_at.desc()).limit(limit)
            
            result = await self.session.execute(stmt)
            db_objs = result.scalars().all()
            
            return [self.response_schema.from_orm(obj) for obj in db_objs]
            
        except Exception as e:
            logger.error(f"Error searching users with query '{query}': {e}")
            raise DatabaseError("Failed to search users", operation="search")

    async def get_admins(self) -> List[User]:
        """Get all admin users."""
        try:
            stmt = select(self.model).where(
                self.model.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
            ).order_by(self.model.created_at.desc())
            
            result = await self.session.execute(stmt)
            db_objs = result.scalars().all()
            
            return [self.response_schema.from_orm(obj) for obj in db_objs]
            
        except Exception as e:
            logger.error(f"Error getting admin users: {e}")
            raise DatabaseError("Failed to get admin users", operation="get_admins")

    async def bulk_update_verification(self, user_ids: List[str], verified: bool = True) -> List[User]:
        """Bulk update email verification for multiple users."""
        try:
            stmt = select(self.model).where(self.model.id.in_(user_ids))
            result = await self.session.execute(stmt)
            db_objs = result.scalars().all()
            
            if len(db_objs) != len(user_ids):
                found_ids = [obj.id for obj in db_objs]
                missing_ids = [uid for uid in user_ids if uid not in found_ids]
                raise NotFoundError("User", missing_ids[0] if missing_ids else "unknown")
            
            # Update verification status
            for db_obj in db_objs:
                db_obj.emailVerified = verified
            
            await self.session.commit()
            
            # Refresh and return updated objects
            for db_obj in db_objs:
                await self.session.refresh(db_obj)
            
            return [self.response_schema.from_orm(obj) for obj in db_objs]
            
        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error bulk updating verification for users: {e}")
            raise DatabaseError("Failed to bulk update verification", operation="bulk_update_verification")

    async def delete_unverified_users(self, days_old: int = 30) -> int:
        """Delete unverified users older than specified days."""
        try:
            # Find unverified users older than specified days
            stmt = select(self.model).where(
                and_(
                    self.model.emailVerified == False,
                    self.model.created_at <= func.now() - func.interval(f'{days_old} days')
                )
            )
            result = await self.session.execute(stmt)
            users_to_delete = result.scalars().all()
            
            deleted_count = len(users_to_delete)
            
            # Delete the users
            for user in users_to_delete:
                await self.session.delete(user)
            
            await self.session.commit()
            
            logger.info(f"Deleted {deleted_count} unverified users older than {days_old} days")
            return deleted_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting unverified users: {e}")
            raise DatabaseError("Failed to delete unverified users", operation="delete_unverified")
