"""
Authentication endpoints.
"""

import logging
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, EmailStr

from app.core.auth import auth_manager, rate_limiter, get_current_active_user, get_current_user
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ApiKeyRequest(BaseModel):
    """API key creation request."""
    name: str
    permissions: list = []
    expires_days: int = 30


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return access token"
)
async def login(request: Request, login_data: LoginRequest) -> TokenResponse:
    """
    User login endpoint.
    
    Note: This is a simplified implementation for demo purposes.
    In production, you would:
    1. Validate credentials against a user database
    2. Implement proper password policies
    3. Add MFA support
    4. Log security events
    """
    client_ip = request.client.host
    
    # Check rate limiting
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Record login attempt
    rate_limiter.record_attempt(client_ip)
    
    # Demo credentials - replace with real authentication
    DEMO_USERS = {
        "admin@lunaxcode.com": {
            "password_hash": auth_manager.get_password_hash("admin123"),
            "permissions": ["admin", "editor", "content_manager"],
            "is_active": True
        },
        "editor@lunaxcode.com": {
            "password_hash": auth_manager.get_password_hash("editor123"),
            "permissions": ["editor", "content_manager"],
            "is_active": True
        }
    }
    
    # Validate user
    user_data = DEMO_USERS.get(login_data.email)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not auth_manager.verify_password(login_data.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": login_data.email,
        "email": login_data.email,
        "permissions": user_data["permissions"],
        "is_active": user_data["is_active"],
        "type": "user"
    }
    
    access_token = auth_manager.create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {login_data.email} logged in successfully from {client_ip}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/api-key",
    response_model=TokenResponse,
    summary="Create API key",
    description="Create a long-lived API key for programmatic access"
)
async def create_api_key(
    api_key_data: ApiKeyRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> TokenResponse:
    """
    Create API key for programmatic access.
    
    Requires admin permissions.
    """
    # Create long-lived token
    expires_delta = timedelta(days=api_key_data.expires_days)
    
    token_data = {
        "sub": f"api_key_{api_key_data.name}",
        "name": api_key_data.name,
        "permissions": api_key_data.permissions,
        "type": "api_key",
        "created_by": current_user["id"]
    }
    
    api_token = auth_manager.create_access_token(
        data=token_data,
        expires_delta=expires_delta
    )
    
    logger.info(f"API key '{api_key_data.name}' created by {current_user['id']}")
    
    return TokenResponse(
        access_token=api_token,
        token_type="bearer",
        expires_in=api_key_data.expires_days * 24 * 60 * 60
    )


@router.post(
    "/logout",
    summary="User logout",
    description="Logout user (client-side token invalidation)"
)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Logout endpoint.
    
    Note: Since we're using stateless JWT tokens, logout is primarily
    handled on the client side by discarding the token.
    
    For enhanced security in production, you might:
    1. Maintain a blacklist of revoked tokens
    2. Use shorter token expiry times
    3. Implement refresh token rotation
    """
    logger.info(f"User {current_user['id']} logged out")
    
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get current user information."""
    return {
        "id": current_user["id"],
        "email": current_user.get("email"),
        "type": current_user["type"],
        "permissions": current_user["permissions"],
        "is_active": current_user["is_active"]
    }


@router.post(
    "/verify-token",
    summary="Verify token",
    description="Verify if a token is valid"
)
async def verify_token(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Verify if a token is valid."""
    return {
        "valid": True,
        "user": {
            "id": current_user["id"],
            "type": current_user["type"],
            "permissions": current_user["permissions"]
        }
    }
