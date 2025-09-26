"""
Database migration script for API key tables.
"""

import asyncio
import logging
from datetime import datetime

from app.database.postgres import db_manager
from app.models.database import APIKey, Base

logger = logging.getLogger(__name__)


async def create_api_key_tables():
    """Create API key tables in the database."""
    try:
        logger.info("🔧 Creating API key tables...")

        # Initialize database manager first
        await db_manager.initialize()

        async with db_manager.async_engine.begin() as conn:
            # Create only the APIKey table
            await conn.run_sync(Base.metadata.create_all, tables=[APIKey.__table__])

        logger.info("✅ API key tables created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create API key tables: {e}")
        raise


async def seed_demo_api_key():
    """Create a demo API key for testing."""
    try:
        from app.core.api_key import APIKeyManager

        logger.info("🌱 Creating demo API key...")

        # Check if demo key already exists
        existing_keys = await APIKeyManager.list_api_keys(created_by="system_demo")
        if existing_keys:
            logger.info("⚠️  Demo API key already exists, skipping...")
            return existing_keys[0]

        # Create demo API key with basic permissions
        demo_scopes = [
            "read:all",
            "write:content"
        ]

        api_key, raw_key = await APIKeyManager.create_api_key(
            name="Demo API Key",
            scopes=demo_scopes,
            description="Demo API key for testing and documentation",
            created_by="system_demo",
            environment="test"
        )

        logger.info(f"✅ Demo API key created: {api_key.key_prefix}")
        logger.info(f"📋 Raw API key: {raw_key}")
        logger.info("⚠️  Save this key securely - it won't be shown again!")

        return api_key

    except Exception as e:
        logger.error(f"❌ Failed to create demo API key: {e}")
        raise


async def migrate_api_keys():
    """Run complete API key migration."""
    try:
        logger.info("🚀 Starting API key migration...")

        # Initialize database connection
        await db_manager.initialize()
        logger.info("✅ Database connection established")

        # Create tables
        await create_api_key_tables()

        # Create demo API key
        demo_key = await seed_demo_api_key()

        logger.info("🎉 API key migration completed successfully!")

        return {
            "status": "success",
            "demo_api_key": {
                "id": str(demo_key.id),
                "key_prefix": demo_key.key_prefix,
                "scopes": demo_key.scopes,
                "created_at": demo_key.created_at.isoformat()
            }
        }

    except Exception as e:
        logger.error(f"❌ API key migration failed: {e}")
        raise


async def rollback_api_keys():
    """Rollback API key migration (drop tables)."""
    try:
        logger.info("🔄 Rolling back API key migration...")

        # Initialize database manager first
        await db_manager.initialize()

        async with db_manager.async_engine.begin() as conn:
            # Drop only the APIKey table
            await conn.run_sync(lambda sync_conn: APIKey.__table__.drop(sync_conn, checkfirst=True))

        logger.info("✅ API key tables dropped successfully")

    except Exception as e:
        logger.error(f"❌ Failed to rollback API key migration: {e}")
        raise


if __name__ == "__main__":
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_api_keys())
    else:
        result = asyncio.run(migrate_api_keys())
        print("\n📋 Migration Summary:")
        print(f"Status: {result['status']}")
        print(f"Demo API Key ID: {result['demo_api_key']['id']}")
        print(f"Demo API Key Prefix: {result['demo_api_key']['key_prefix']}")
        print(f"Demo API Key Scopes: {', '.join(result['demo_api_key']['scopes'])}")
        print("\n⚠️  Remember to save the raw API key from the logs above!")