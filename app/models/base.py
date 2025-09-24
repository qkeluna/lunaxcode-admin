"""
Base Pydantic models for Xata integration.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class XataRecord(BaseModel):
    """Base model for Xata records with system fields."""
    
    xata_id: Optional[str] = Field(None, description="Xata's unique record identifier")
    xata_version: Optional[int] = Field(None, description="Record version for optimistic concurrency")
    xata_createdat: Optional[datetime] = Field(None, description="Automatic creation timestamp")
    xata_updatedat: Optional[datetime] = Field(None, description="Automatic update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class BaseResponse(BaseModel):
    """Base response model."""
    
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    
    items: list
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        page: int,
        size: int
    ):
        """Create paginated response."""
        pages = (total + size - 1) // size  # Ceiling division
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )
