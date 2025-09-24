"""
Authentication and authorization utilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    def create_api_key_token(self, api_key_id: str, permissions: list = None) -> str:
        """Create a token for API key authentication."""
        data = {
            "sub": api_key_id,
            "type": "api_key",
            "permissions": permissions or []
        }
        return self.create_access_token(data)


# Global auth manager instance
auth_manager = AuthManager()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    This is a simplified version - in production you'd validate against a user database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token
        payload = auth_manager.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        # Get user info from payload
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "user")
        
        if user_id is None:
            raise credentials_exception
        
        # In a real application, you would fetch user data from database here
        # For now, we'll return the payload data
        return {
            "id": user_id,
            "type": token_type,
            "permissions": payload.get("permissions", []),
            "email": payload.get("email"),
            "is_active": payload.get("is_active", True)
        }
        
    except JWTError:
        raise credentials_exception


def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user."""
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permissions(required_permissions: list):
    """
    Dependency factory to require specific permissions.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user = Depends(require_permissions(["admin"]))):
            pass
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        
        # Check if user has all required permissions
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return permission_checker


def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user if authenticated, None otherwise.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)
        
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return {
            "id": user_id,
            "type": payload.get("type", "user"),
            "permissions": payload.get("permissions", []),
            "email": payload.get("email"),
            "is_active": payload.get("is_active", True)
        }
        
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None


# Helper functions for specific permission checks
def require_admin():
    """Require admin permissions."""
    return require_permissions(["admin"])


def require_editor():
    """Require editor permissions."""
    return require_permissions(["editor"])


def require_content_manager():
    """Require content management permissions."""
    return require_permissions(["content_manager", "editor", "admin"])


# Rate limiting for authentication endpoints
class RateLimiter:
    """Simple in-memory rate limiter for authentication attempts."""
    
    def __init__(self):
        self.attempts = {}
        self.max_attempts = 5
        self.window_minutes = 15
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited."""
        now = datetime.utcnow()
        
        # Clean old attempts
        self._clean_old_attempts(now)
        
        if identifier not in self.attempts:
            return False
        
        attempts = self.attempts[identifier]
        recent_attempts = [
            attempt for attempt in attempts
            if (now - attempt).total_seconds() < (self.window_minutes * 60)
        ]
        
        return len(recent_attempts) >= self.max_attempts
    
    def record_attempt(self, identifier: str):
        """Record an authentication attempt."""
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append(now)
        
        # Keep only recent attempts
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier]
            if (now - attempt).total_seconds() < (self.window_minutes * 60)
        ]
    
    def _clean_old_attempts(self, now: datetime):
        """Clean old attempts to prevent memory leaks."""
        cutoff = now - timedelta(minutes=self.window_minutes * 2)
        
        for identifier in list(self.attempts.keys()):
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if attempt > cutoff
            ]
            
            if not self.attempts[identifier]:
                del self.attempts[identifier]


# Global rate limiter
rate_limiter = RateLimiter()
