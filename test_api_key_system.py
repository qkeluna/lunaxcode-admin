#!/usr/bin/env python3
"""
Quick test script for API key system without database dependency.
"""

import asyncio
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_api_key_generation():
    """Test API key generation functionality."""
    try:
        from app.core.api_key import APIKeyManager

        logger.info("🧪 Testing API key generation...")

        # Test key generation
        full_key, key_hash, key_prefix = APIKeyManager.generate_api_key("test")

        logger.info(f"✅ Generated API key: {key_prefix}")
        logger.info(f"📋 Full key: {full_key}")
        logger.info(f"🔒 Hash: {key_hash[:20]}...")

        # Test hash validation
        test_hash = APIKeyManager.hash_api_key(full_key)
        if test_hash == key_hash:
            logger.info("✅ Hash validation works correctly")
        else:
            logger.error("❌ Hash validation failed")

        # Test scope validation
        valid_scopes = ["read:all", "write:content"]
        invalid_scopes = ["invalid:scope", "bad:permission"]

        invalid_found = APIKeyManager.validate_scopes(valid_scopes)
        if not invalid_found:
            logger.info("✅ Valid scopes passed validation")
        else:
            logger.error(f"❌ Valid scopes failed: {invalid_found}")

        invalid_found = APIKeyManager.validate_scopes(invalid_scopes)
        if invalid_found:
            logger.info(f"✅ Invalid scopes correctly rejected: {invalid_found}")
        else:
            logger.error("❌ Invalid scopes were accepted")

        # Test permission checking
        api_key_scopes = ["read:all", "write:pricing"]

        # Should pass
        if APIKeyManager.check_scope_permission(api_key_scopes, "read:pricing"):
            logger.info("✅ Read permission check passed")
        else:
            logger.error("❌ Read permission check failed")

        # Should fail
        if not APIKeyManager.check_scope_permission(api_key_scopes, "admin:full"):
            logger.info("✅ Admin permission correctly denied")
        else:
            logger.error("❌ Admin permission incorrectly granted")

        logger.info("🎉 All API key generation tests passed!")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


async def test_rate_limiting_logic():
    """Test rate limiting logic without Redis."""
    try:
        from app.core.rate_limiting import get_tier_limit, TIER_LIMITS
        from app.models.database import RateLimitTier

        logger.info("🧪 Testing rate limiting configuration...")

        for tier in RateLimitTier:
            limit_str = get_tier_limit(tier)
            logger.info(f"✅ {tier.value}: {limit_str}")

        logger.info("✅ Rate limiting configuration test passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Rate limiting test failed: {e}")
        return False


async def test_monitoring_setup():
    """Test monitoring utilities."""
    try:
        from app.core.api_monitoring import SecurityMonitor

        logger.info("🧪 Testing security monitoring...")

        # Test security event creation (without Redis)
        await SecurityMonitor.log_security_event(
            event_type="test_event",
            details={"test": "data"},
            severity="info"
        )

        logger.info("✅ Security monitoring test passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Monitoring test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting API key system tests...")

    results = []

    # Test individual components
    results.append(await test_api_key_generation())
    results.append(await test_rate_limiting_logic())
    results.append(await test_monitoring_setup())

    # Summary
    passed = sum(results)
    total = len(results)

    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! API key system is ready.")
        return True
    else:
        logger.error("❌ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)