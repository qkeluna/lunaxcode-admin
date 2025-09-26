#!/usr/bin/env python3
"""
Better Auth Migration Script

This script migrates your Neon PostgreSQL database to support Better Auth authentication.
It will:
1. Create the required tables (users, sessions, accounts)
2. Migrate existing cms_users data if present
3. Add security constraints and indexes
4. Create cleanup procedures

Usage:
    python scripts/migrate_better_auth.py
    
Or from the project root:
    python -m scripts.migrate_better_auth
"""

import sys
import os
import asyncio
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.better_auth_migration import run_better_auth_migration
from app.core.config import settings


async def main():
    """Main migration function."""
    print("🚀 Better Auth Migration Tool")
    print("=" * 50)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL[:30]}..." if settings.DATABASE_URL else "No DATABASE_URL set")
    print("=" * 50)
    
    if not settings.DATABASE_URL:
        print("❌ ERROR: DATABASE_URL environment variable is not set!")
        print("Please set your Neon PostgreSQL connection string:")
        print("export DATABASE_URL='postgresql://username:password@host/database'")
        sys.exit(1)
    
    # Confirm before proceeding in production
    if settings.ENVIRONMENT == "production":
        confirm = input("\n⚠️ WARNING: You are about to run migration in PRODUCTION!\nType 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)
    
    print("\n🏁 Starting Better Auth migration...")
    
    try:
        await run_better_auth_migration()
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your frontend to use Better Auth")
        print("2. Configure OAuth providers (Google, GitHub, etc.)")
        print("3. Test authentication flow")
        print("4. Set up automated cleanup jobs for expired sessions")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        logging.exception("Migration error details:")
        sys.exit(1)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the migration
    asyncio.run(main())
