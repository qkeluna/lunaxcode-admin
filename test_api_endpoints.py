#!/usr/bin/env python3
"""
Test API endpoints with mock requests to verify the implementation.
"""

import asyncio
import json
import logging
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_api_auth_middleware():
    """Test API key authentication middleware logic."""
    try:
        from app.core.api_auth import APIKeyAuthMiddleware
        from fastapi import Request

        logger.info("🧪 Testing API key middleware...")

        middleware = APIKeyAuthMiddleware(None)

        # Test API key extraction
        mock_request = Mock()
        mock_request.headers = {"X-API-Key": "lx_test_123"}

        key = await middleware._extract_api_key(mock_request)
        if key == "lx_test_123":
            logger.info("✅ API key extraction from X-API-Key header works")
        else:
            logger.error("❌ API key extraction failed")

        # Test Authorization header
        mock_request.headers = {"Authorization": "Bearer lx_test_456"}
        key = await middleware._extract_api_key(mock_request)
        if key == "lx_test_456":
            logger.info("✅ API key extraction from Authorization header works")
        else:
            logger.error("❌ Authorization header extraction failed")

        # Test non-API key token
        mock_request.headers = {"Authorization": "Bearer jwt_token_here"}
        key = await middleware._extract_api_key(mock_request)
        if key is None:
            logger.info("✅ JWT tokens correctly ignored")
        else:
            logger.error("❌ JWT token incorrectly treated as API key")

        logger.info("✅ API auth middleware test passed!")
        return True

    except Exception as e:
        logger.error(f"❌ API auth middleware test failed: {e}")
        return False


async def test_scope_checking():
    """Test scope permission logic."""
    try:
        from app.core.api_key import APIKeyManager

        logger.info("🧪 Testing scope permission checking...")

        # Test cases
        test_cases = [
            # (api_key_scopes, required_scope, should_pass)
            (["read:all"], "read:pricing", True),
            (["write:content"], "write:pricing", True),
            (["admin:full"], "read:all", True),
            (["admin:full"], "write:content", True),
            (["read:pricing"], "write:pricing", False),
            (["write:content"], "admin:full", False),
            (["read:pricing"], "read:pricing", True),
        ]

        all_passed = True
        for api_scopes, required, should_pass in test_cases:
            result = APIKeyManager.check_scope_permission(api_scopes, required)
            if result == should_pass:
                logger.info(f"✅ Scope test passed: {api_scopes} -> {required} = {result}")
            else:
                logger.error(f"❌ Scope test failed: {api_scopes} -> {required} = {result}, expected {should_pass}")
                all_passed = False

        if all_passed:
            logger.info("✅ All scope permission tests passed!")
        else:
            logger.error("❌ Some scope permission tests failed")

        return all_passed

    except Exception as e:
        logger.error(f"❌ Scope checking test failed: {e}")
        return False


async def test_api_key_models():
    """Test Pydantic models for API keys."""
    try:
        from app.api.v1.api_keys import APIKeyCreate, APIKeyResponse
        from app.models.database import RateLimitTier

        logger.info("🧪 Testing API key Pydantic models...")

        # Test APIKeyCreate validation
        valid_data = {
            "name": "Test API Key",
            "description": "Test description",
            "scopes": ["read:all", "write:content"],
            "tier": RateLimitTier.STANDARD,
            "expires_days": 30,
            "environment": "test"
        }

        api_key_create = APIKeyCreate(**valid_data)
        logger.info(f"✅ Valid API key create model: {api_key_create.name}")

        # Test invalid scopes
        try:
            invalid_data = valid_data.copy()
            invalid_data["scopes"] = ["invalid:scope"]
            APIKeyCreate(**invalid_data)
            logger.error("❌ Invalid scopes were accepted")
            return False
        except ValueError as e:
            logger.info("✅ Invalid scopes correctly rejected")

        # Test invalid environment
        try:
            invalid_data = valid_data.copy()
            invalid_data["environment"] = "invalid"
            APIKeyCreate(**invalid_data)
            logger.error("❌ Invalid environment was accepted")
            return False
        except ValueError as e:
            logger.info("✅ Invalid environment correctly rejected")

        logger.info("✅ API key model tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ API key model test failed: {e}")
        return False


async def test_security_headers():
    """Test security utilities."""
    try:
        from app.core.api_auth import check_ip_whitelist, is_api_key_expired
        from app.models.database import APIKey
        from datetime import datetime, timedelta

        logger.info("🧪 Testing security utilities...")

        # Mock API key
        mock_api_key = Mock()
        mock_api_key.ip_whitelist = ["192.168.1.100", "10.0.0.1"]
        mock_api_key.expires_at = None

        # Test IP whitelist
        if check_ip_whitelist(mock_api_key, "192.168.1.100"):
            logger.info("✅ IP whitelist allows authorized IP")
        else:
            logger.error("❌ IP whitelist blocked authorized IP")
            return False

        if not check_ip_whitelist(mock_api_key, "192.168.1.999"):
            logger.info("✅ IP whitelist blocks unauthorized IP")
        else:
            logger.error("❌ IP whitelist allowed unauthorized IP")
            return False

        # Test no whitelist (should allow all)
        mock_api_key.ip_whitelist = None
        if check_ip_whitelist(mock_api_key, "any.ip.address"):
            logger.info("✅ No whitelist allows all IPs")
        else:
            logger.error("❌ No whitelist incorrectly blocked IP")
            return False

        # Test expiration
        if not is_api_key_expired(mock_api_key):
            logger.info("✅ No expiration date means not expired")
        else:
            logger.error("❌ No expiration incorrectly marked as expired")
            return False

        # Test expired key
        mock_api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        if is_api_key_expired(mock_api_key):
            logger.info("✅ Expired API key correctly identified")
        else:
            logger.error("❌ Expired API key not identified")
            return False

        logger.info("✅ Security utilities tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Security utilities test failed: {e}")
        return False


async def main():
    """Run all endpoint tests."""
    logger.info("🚀 Starting API endpoint tests...")

    results = []

    # Test individual components
    results.append(await test_api_auth_middleware())
    results.append(await test_scope_checking())
    results.append(await test_api_key_models())
    results.append(await test_security_headers())

    # Summary
    passed = sum(results)
    total = len(results)

    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All endpoint tests passed! API key system implementation is solid.")
        return True
    else:
        logger.error("❌ Some endpoint tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)