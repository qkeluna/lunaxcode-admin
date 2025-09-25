"""
Base service class for PostgreSQL operations using SQLAlchemy.
"""

import logging
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Sequence
from sqlalchemy import select, func, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database.postgres import Base
from app.models.schemas import PaginationParams, PaginatedResponse
from app.core.exceptions import NotFoundError, DatabaseError, ValidationException

logger = logging.getLogger(__name__)

# Type variables
ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
ResponseSchemaType = TypeVar('ResponseSchemaType', bound=BaseModel)


class PostgresBaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """Base service for PostgreSQL operations."""
    
    def __init__(
        self,
        model: Type[ModelType],
        response_schema: Type[ResponseSchemaType],
        session: AsyncSession
    ):
        self.model = model
        self.response_schema = response_schema
        self.session = session
    
    async def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        """Create a new record."""
        try:
            # Convert Pydantic model to dict and create SQLAlchemy instance
            obj_data = obj_in.dict(exclude_unset=True)
            db_obj = self.model(**obj_data)
            
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return self.response_schema.from_orm(db_obj)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create {self.model.__name__}", operation="create")
    
    async def get_by_id(self, id: str) -> Optional[ResponseSchemaType]:
        """Get record by ID."""
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if db_obj:
                return self.response_schema.from_orm(db_obj)
            return None
            
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__}", operation="get_by_id")
    
    async def update(self, id: str, obj_in: UpdateSchemaType) -> ResponseSchemaType:
        """Update a record."""
        try:
            # Get existing record
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                raise NotFoundError(self.model.__name__, id)
            
            # Update fields
            obj_data = obj_in.dict(exclude_unset=True, exclude_none=True)
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return self.response_schema.from_orm(db_obj)
            
        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to update {self.model.__name__}", operation="update")
    
    async def delete(self, id: str) -> bool:
        """Delete a record."""
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if not db_obj:
                raise NotFoundError(self.model.__name__, id)
            
            await self.session.delete(db_obj)
            await self.session.commit()
            
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise DatabaseError(f"Failed to delete {self.model.__name__}", operation="delete")
    
    async def get_all(
        self,
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "display_order",
        order_direction: str = "asc"
    ) -> PaginatedResponse:
        """Get all records with pagination and filtering."""
        try:
            # Build base query
            stmt = select(self.model)
            count_stmt = select(func.count(self.model.id))
            
            # Apply filters
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            filter_conditions.append(getattr(self.model, key).in_(value))
                        else:
                            filter_conditions.append(getattr(self.model, key) == value)
                
                if filter_conditions:
                    stmt = stmt.where(and_(*filter_conditions))
                    count_stmt = count_stmt.where(and_(*filter_conditions))
            
            # Apply default active filter if model has is_active field
            if hasattr(self.model, 'is_active') and (not filters or 'is_active' not in filters):
                stmt = stmt.where(self.model.is_active == True)
                count_stmt = count_stmt.where(self.model.is_active == True)
            
            # Apply ordering
            if hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_direction.lower() == "desc":
                    stmt = stmt.order_by(order_column.desc())
                else:
                    stmt = stmt.order_by(order_column.asc())
            
            # Apply pagination
            stmt = stmt.offset(pagination.offset).limit(pagination.size)
            
            # Execute queries
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            count_result = await self.session.execute(count_stmt)
            total = count_result.scalar()
            
            # Convert to response schemas
            items = [self.response_schema.from_orm(record) for record in records]
            
            return PaginatedResponse.create(
                items=items,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
            
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__} records", operation="get_all")
    
    async def search(
        self,
        query: str,
        pagination: PaginationParams,
        search_fields: List[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponse:
        """Full-text search in records."""
        try:
            # Default search fields
            if not search_fields:
                search_fields = ["name"] if hasattr(self.model, "name") else []
            
            # Build search conditions
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    search_conditions.append(column.ilike(f"%{query}%"))
            
            if not search_conditions:
                # Fallback to get_all if no searchable fields
                return await self.get_all(pagination, filters)
            
            # Build base query with search
            stmt = select(self.model).where(or_(*search_conditions))
            count_stmt = select(func.count(self.model.id)).where(or_(*search_conditions))
            
            # Apply additional filters
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            filter_conditions.append(getattr(self.model, key).in_(value))
                        else:
                            filter_conditions.append(getattr(self.model, key) == value)
                
                if filter_conditions:
                    stmt = stmt.where(and_(*filter_conditions))
                    count_stmt = count_stmt.where(and_(*filter_conditions))
            
            # Apply default active filter
            if hasattr(self.model, 'is_active') and (not filters or 'is_active' not in filters):
                stmt = stmt.where(self.model.is_active == True)
                count_stmt = count_stmt.where(self.model.is_active == True)
            
            # Apply ordering
            if hasattr(self.model, 'display_order'):
                stmt = stmt.order_by(self.model.display_order.asc())
            
            # Apply pagination
            stmt = stmt.offset(pagination.offset).limit(pagination.size)
            
            # Execute queries
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            count_result = await self.session.execute(count_stmt)
            total = count_result.scalar()
            
            # Convert to response schemas
            items = [self.response_schema.from_orm(record) for record in records]
            
            return PaginatedResponse.create(
                items=items,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
            
        except Exception as e:
            logger.error(f"Error searching {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to search {self.model.__name__}", operation="search")
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ResponseSchemaType]:
        """Get record by specific field."""
        try:
            if not hasattr(self.model, field):
                return None
            
            stmt = select(self.model).where(getattr(self.model, field) == value)
            result = await self.session.execute(stmt)
            db_obj = result.scalar_one_or_none()
            
            if db_obj:
                return self.response_schema.from_orm(db_obj)
            return None
            
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field}={value}: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__}", operation="get_by_field")
    
    async def get_many_by_field(
        self,
        field: str,
        value: Any,
        limit: Optional[int] = None,
        order_by: str = "display_order"
    ) -> List[ResponseSchemaType]:
        """Get multiple records by specific field."""
        try:
            if not hasattr(self.model, field):
                return []
            
            stmt = select(self.model).where(getattr(self.model, field) == value)
            
            # Apply ordering
            if hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                stmt = stmt.order_by(order_column.asc())
            
            # Apply limit
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            return [self.response_schema.from_orm(record) for record in records]
            
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field}={value}: {e}")
            raise DatabaseError(f"Failed to get {self.model.__name__} records", operation="get_many_by_field")
    
    async def update_many(self, updates: List[Dict[str, Any]]) -> List[ResponseSchemaType]:
        """Update multiple records."""
        try:
            updated_records = []
            
            for update_data in updates:
                record_id = update_data.get("id")
                if not record_id:
                    continue
                
                # Get existing record
                stmt = select(self.model).where(self.model.id == record_id)
                result = await self.session.execute(stmt)
                db_obj = result.scalar_one_or_none()
                
                if not db_obj:
                    continue
                
                # Update fields (exclude id)
                for field, value in update_data.items():
                    if field != "id" and hasattr(db_obj, field):
                        setattr(db_obj, field, value)
                
                updated_records.append(db_obj)
            
            await self.session.commit()
            
            # Refresh all updated records
            for record in updated_records:
                await self.session.refresh(record)
            
            return [self.response_schema.from_orm(record) for record in updated_records]
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating multiple {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to update {self.model.__name__} records", operation="update_many")
