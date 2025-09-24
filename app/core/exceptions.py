"""
Custom exceptions and exception handlers for the API.
"""

from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional context."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        context: Dict[str, Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


class ValidationException(CustomHTTPException):
    """Exception for validation errors."""
    
    def __init__(self, detail: str, field: str = None):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context={"field": field} if field else {}
        )


class NotFoundError(CustomHTTPException):
    """Exception for resource not found."""
    
    def __init__(self, resource: str, identifier: str = None):
        detail = f"{resource} not found"
        if identifier:
            detail += f" with identifier: {identifier}"
        
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND",
            context={"resource": resource, "identifier": identifier}
        )


class DatabaseError(CustomHTTPException):
    """Exception for database errors."""
    
    def __init__(self, detail: str, operation: str = None):
        super().__init__(
            status_code=500,
            detail=f"Database error: {detail}",
            error_code="DATABASE_ERROR",
            context={"operation": operation}
        )


class CacheError(CustomHTTPException):
    """Exception for cache errors."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            detail=f"Cache error: {detail}",
            error_code="CACHE_ERROR"
        )


async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """Handler for custom HTTP exceptions."""
    logger.error(
        f"Custom HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "error_code": exc.error_code,
            "context": exc.context,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": exc.error_code,
                "status_code": exc.status_code,
                "context": exc.context
            },
            "path": request.url.path,
            "method": request.method
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for validation exceptions."""
    logger.error(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "message": "Validation error",
                "code": "VALIDATION_ERROR",
                "status_code": 422,
                "details": exc.errors()
            },
            "path": request.url.path,
            "method": request.method
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for general exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_SERVER_ERROR",
                "status_code": 500
            },
            "path": request.url.path,
            "method": request.method
        }
    )
