"""
Base service class with common CRUD operations.
"""

import logging
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic
from pydantic import BaseModel

from app.database.xata import XataDB
from app.models.base import PaginationParams, PaginatedResponse
from app.core.exceptions import NotFoundError, DatabaseError
from app.core.cache import cache_key_builder, get_cache, set_cache, delete_cache_pattern

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)
CreateT = TypeVar('CreateT', bound=BaseModel)
UpdateT = TypeVar('UpdateT', bound=BaseModel)


class BaseService(Generic[T, CreateT, UpdateT]):
    """Base service with common CRUD operations."""
    
    def __init__(
        self,
        db: XataDB,
        table_name: str,
        model_class: Type[T],
        create_model_class: Type[CreateT],
        update_model_class: Type[UpdateT]
    ):
        self.db = db
        self.table_name = table_name
        self.model_class = model_class
        self.create_model_class = create_model_class
        self.update_model_class = update_model_class
    
    async def create(self, data: CreateT, record_id: Optional[str] = None) -> T:
        """Create a new record."""
        try:
            # Convert Pydantic model to dict
            create_data = data.dict(exclude_unset=True)
            
            # Create record in database
            result = await self.db.create_record(
                table=self.table_name,
                data=create_data,
                record_id=record_id
            )
            
            # Invalidate cache
            await self._invalidate_cache()
            
            # Return as Pydantic model
            return self.model_class(**result)
            
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}")
            raise DatabaseError(f"Failed to create {self.table_name}", operation="create")
    
    async def get_by_id(self, record_id: str, use_cache: bool = True) -> Optional[T]:
        """Get record by ID."""
        try:
            # Try cache first
            if use_cache:
                cache_key = cache_key_builder("get_by_id", self.table_name, record_id)
                cached_result = await get_cache(cache_key)
                if cached_result:
                    return self.model_class(**cached_result)
            
            # Get from database
            result = await self.db.get_record(self.table_name, record_id)
            if not result:
                return None
            
            # Cache result
            if use_cache:
                cache_key = cache_key_builder("get_by_id", self.table_name, record_id)
                await set_cache(cache_key, result)
            
            return self.model_class(**result)
            
        except Exception as e:
            logger.error(f"Error getting {self.table_name} by ID {record_id}: {e}")
            raise DatabaseError(f"Failed to get {self.table_name}", operation="get_by_id")
    
    async def update(self, record_id: str, data: UpdateT) -> T:
        """Update a record."""
        try:
            # Check if record exists
            existing = await self.get_by_id(record_id, use_cache=False)
            if not existing:
                raise NotFoundError(self.table_name, record_id)
            
            # Convert Pydantic model to dict, excluding unset values
            update_data = data.dict(exclude_unset=True, exclude_none=True)
            
            if not update_data:
                # No data to update, return existing record
                return existing
            
            # Update record in database
            result = await self.db.update_record(
                table=self.table_name,
                record_id=record_id,
                data=update_data
            )
            
            # Invalidate cache
            await self._invalidate_cache()
            
            return self.model_class(**result)
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating {self.table_name} {record_id}: {e}")
            raise DatabaseError(f"Failed to update {self.table_name}", operation="update")
    
    async def delete(self, record_id: str) -> bool:
        """Delete a record."""
        try:
            # Check if record exists
            existing = await self.get_by_id(record_id, use_cache=False)
            if not existing:
                raise NotFoundError(self.table_name, record_id)
            
            # Delete from database
            success = await self.db.delete_record(self.table_name, record_id)
            
            if success:
                # Invalidate cache
                await self._invalidate_cache()
            
            return success
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting {self.table_name} {record_id}: {e}")
            raise DatabaseError(f"Failed to delete {self.table_name}", operation="delete")
    
    async def get_all(
        self,
        pagination: PaginationParams,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = "displayOrder",
        sort_direction: str = "asc",
        use_cache: bool = True
    ) -> PaginatedResponse:
        """Get all records with pagination and filtering."""
        try:
            # Build cache key
            cache_key = None
            if use_cache:
                cache_key = cache_key_builder(
                    "get_all",
                    self.table_name,
                    page=pagination.page,
                    size=pagination.size,
                    filter=str(filter_conditions) if filter_conditions else None,
                    sort_by=sort_by,
                    sort_direction=sort_direction
                )
                cached_result = await get_cache(cache_key)
                if cached_result:
                    return PaginatedResponse(**cached_result)
            
            # Build sort configuration
            sort_config = []
            if sort_by:
                sort_config.append({sort_by: sort_direction})
            
            # Add default active filter if not specified
            if filter_conditions is None:
                filter_conditions = {"isActive": True}
            elif "isActive" not in filter_conditions:
                filter_conditions["isActive"] = True
            
            # Query database
            result = await self.db.query_records(
                table=self.table_name,
                filter_conditions=filter_conditions,
                sort=sort_config,
                page_size=pagination.size,
                offset=pagination.offset
            )
            
            # Convert to Pydantic models
            records = [self.model_class(**record) for record in result.get("records", [])]
            
            # Get total count (Xata doesn't return total in paginated queries)
            # We need to make a separate count query
            total = await self._get_total_count(filter_conditions)
            
            # Create paginated response
            paginated_response = PaginatedResponse.create(
                items=records,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
            
            # Cache result
            if use_cache and cache_key:
                await set_cache(cache_key, paginated_response.dict())
            
            return paginated_response
            
        except Exception as e:
            logger.error(f"Error getting all {self.table_name}: {e}")
            raise DatabaseError(f"Failed to get {self.table_name} records", operation="get_all")
    
    async def search(
        self,
        query: str,
        pagination: PaginationParams,
        target_columns: Optional[List[str]] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponse:
        """Full-text search in records."""
        try:
            # Add default active filter
            if filter_conditions is None:
                filter_conditions = {"isActive": True}
            elif "isActive" not in filter_conditions:
                filter_conditions["isActive"] = True
            
            # Search in database
            result = await self.db.search_records(
                table=self.table_name,
                query=query,
                target_columns=target_columns,
                filter_conditions=filter_conditions,
                page_size=pagination.size,
                offset=pagination.offset
            )
            
            # Convert to Pydantic models
            records = [self.model_class(**record["record"]) for record in result.get("records", [])]
            
            # Xata search includes total count
            total = result.get("totalCount", len(records))
            
            return PaginatedResponse.create(
                items=records,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
            
        except Exception as e:
            logger.error(f"Error searching {self.table_name}: {e}")
            raise DatabaseError(f"Failed to search {self.table_name}", operation="search")
    
    async def _get_total_count(self, filter_conditions: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of records matching filter."""
        try:
            result = await self.db.query_records(
                table=self.table_name,
                filter_conditions=filter_conditions,
                page_size=1,  # We only need count
                offset=0,
                columns=["xata_id"]  # Only get ID to minimize data transfer
            )
            
            # For now, we'll estimate based on the meta information
            # Xata doesn't provide total count directly in queries
            # This is a limitation we'll need to work with
            records = result.get("records", [])
            if len(records) == 1:
                # If we got a record, there's at least 1
                # We'll need to implement a proper count method
                return await self._estimate_total_count(filter_conditions)
            return 0
            
        except Exception as e:
            logger.error(f"Error getting total count for {self.table_name}: {e}")
            return 0
    
    async def _estimate_total_count(self, filter_conditions: Optional[Dict[str, Any]] = None) -> int:
        """Estimate total count by querying larger batches."""
        try:
            # Query with a large page size to estimate total
            result = await self.db.query_records(
                table=self.table_name,
                filter_conditions=filter_conditions,
                page_size=1000,  # Large page size
                offset=0,
                columns=["xata_id"]
            )
            
            records = result.get("records", [])
            return len(records)
            
        except Exception:
            # Fallback to 0 if estimation fails
            return 0
    
    async def _invalidate_cache(self):
        """Invalidate all cache entries for this table."""
        try:
            pattern = f"lunaxcode-cms:*:{self.table_name}:*"
            await delete_cache_pattern(pattern)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for {self.table_name}: {e}")
