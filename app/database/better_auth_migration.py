"""
Better Auth Database Migration Script for Neon PostgreSQL

This script creates the required tables for Better Auth integration:
- users: Store user account information
- sessions: Store user session information  
- accounts: Store OAuth provider account links

Based on the schema defined in docs/better-auth-database-schema.md
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import text, select, func
from sqlalchemy.exc import IntegrityError

from app.database.postgres import db_manager
from app.models.database import User, Session, Account, UserRole, OAuthProvider

logger = logging.getLogger(__name__)


class BetterAuthMigration:
    """Migration manager for Better Auth tables."""
    
    def __init__(self):
        self.migration_version = "better_auth_v1.0"
    
    async def check_migration_status(self) -> bool:
        """Check if Better Auth migration has already been run."""
        try:
            async with db_manager.get_session() as session:
                # Check if users table exists and has data
                result = await session.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'users'
                        );
                    """)
                )
                table_exists = result.scalar()
                
                if table_exists:
                    # Check if table has the right structure (emailVerified column)
                    result = await session.execute(
                        text("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.columns 
                                WHERE table_schema = 'public' 
                                AND table_name = 'users'
                                AND column_name = 'emailVerified'
                            );
                        """)
                    )
                    has_better_auth_structure = result.scalar()
                    return has_better_auth_structure
                
                return False
                
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return False
    
    async def backup_existing_data(self) -> bool:
        """Backup existing cms_users data if it exists."""
        try:
            async with db_manager.get_session() as session:
                # Check if cms_users table exists
                result = await session.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'cms_users'
                        );
                    """)
                )
                cms_users_exists = result.scalar()
                
                if not cms_users_exists:
                    logger.info("No cms_users table found, skipping backup")
                    return True
                
                # Create backup table
                await session.execute(
                    text("""
                        CREATE TABLE IF NOT EXISTS cms_users_backup AS 
                        SELECT * FROM cms_users;
                    """)
                )
                await session.commit()
                
                # Get count for verification
                result = await session.execute(text("SELECT COUNT(*) FROM cms_users_backup"))
                backup_count = result.scalar()
                
                logger.info(f"✅ Backed up {backup_count} records from cms_users to cms_users_backup")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error backing up existing data: {e}")
            return False
    
    async def create_better_auth_tables(self):
        """Create Better Auth tables using SQLAlchemy models."""
        try:
            if not db_manager.async_engine:
                await db_manager.initialize()
            
            # Create tables using the models
            async with db_manager.async_engine.begin() as conn:
                # Import the models to ensure they're registered
                from app.models.database import User, Session, Account
                
                # Create only the Better Auth tables
                await conn.run_sync(User.__table__.create, checkfirst=True)
                await conn.run_sync(Session.__table__.create, checkfirst=True)
                await conn.run_sync(Account.__table__.create, checkfirst=True)
            
            logger.info("✅ Better Auth tables created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create Better Auth tables: {e}")
            raise
    
    async def migrate_cms_users_data(self):
        """Migrate data from cms_users to users table if cms_users exists."""
        try:
            async with db_manager.get_session() as session:
                # Check if cms_users table exists
                result = await session.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'cms_users'
                        );
                    """)
                )
                cms_users_exists = result.scalar()
                
                if not cms_users_exists:
                    logger.info("No cms_users table found, skipping data migration")
                    return
                
                # Get cms_users data
                cms_users_result = await session.execute(
                    text("""
                        SELECT id, username, email, created_at, updated_at, is_active
                        FROM cms_users 
                        WHERE is_active = true 
                        AND email IS NOT NULL 
                        AND email != ''
                    """)
                )
                cms_users = cms_users_result.fetchall()
                
                if not cms_users:
                    logger.info("No active cms_users found to migrate")
                    return
                
                # Migrate users
                migrated_count = 0
                for cms_user in cms_users:
                    try:
                        # Create new user with cms_ prefix to avoid ID conflicts
                        user = User(
                            id=f"cms_{cms_user.id}",
                            name=cms_user.username,
                            email=cms_user.email,
                            emailVerified=True,  # Existing users are considered verified
                            role=UserRole.ADMIN,  # All cms users were admin
                            created_at=cms_user.created_at,
                            updated_at=cms_user.updated_at
                        )
                        session.add(user)
                        migrated_count += 1
                        
                    except IntegrityError as e:
                        # Handle duplicate emails by adding suffix
                        if "duplicate key" in str(e).lower() and "email" in str(e).lower():
                            user.email = f"{cms_user.email.split('@')[0]}+cms_{cms_user.id}@{cms_user.email.split('@')[1]}"
                            session.add(user)
                            migrated_count += 1
                        else:
                            logger.warning(f"Failed to migrate user {cms_user.id}: {e}")
                            continue
                
                await session.commit()
                logger.info(f"✅ Migrated {migrated_count} users from cms_users to users table")
                
        except Exception as e:
            logger.error(f"❌ Error migrating cms_users data: {e}")
            raise
    
    async def create_sample_admin_user(self):
        """Create a sample admin user for testing."""
        try:
            async with db_manager.get_session() as session:
                # Check if any users exist
                result = await session.execute(select(func.count(User.id)))
                user_count = result.scalar()
                
                if user_count > 0:
                    logger.info("Users already exist, skipping sample user creation")
                    return
                
                # Create sample admin user
                admin_user = User(
                    id="admin_001",
                    name="Admin User",
                    email="admin@lunaxcode.com",
                    emailVerified=True,
                    role=UserRole.ADMIN
                )
                
                session.add(admin_user)
                await session.commit()
                
                logger.info("✅ Created sample admin user: admin@lunaxcode.com")
                
        except Exception as e:
            logger.error(f"❌ Error creating sample admin user: {e}")
            raise
    
    async def add_security_constraints(self):
        """Add security constraints and validation rules."""
        try:
            async with db_manager.get_session() as session:
                # Add email format validation constraint
                await session.execute(
                    text(r"""
                        ALTER TABLE users 
                        ADD CONSTRAINT chk_email_format 
                        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
                    """)
                )
                
                # Add role validation constraint
                await session.execute(
                    text("""
                        ALTER TABLE users
                        ADD CONSTRAINT chk_role_values
                        CHECK (role IN ('admin', 'super_admin', 'user'));
                    """)
                )
                
                # Add session token length constraint
                await session.execute(
                    text("""
                        ALTER TABLE sessions
                        ADD CONSTRAINT chk_token_length
                        CHECK (LENGTH(token) >= 32);
                    """)
                )
                
                # Add provider validation constraint
                await session.execute(
                    text("""
                        ALTER TABLE accounts
                        ADD CONSTRAINT chk_provider_values
                        CHECK ("providerId" IN ('google', 'github', 'microsoft', 'apple'));
                    """)
                )
                
                # Add unique constraint for provider accounts
                await session.execute(
                    text("""
                        ALTER TABLE accounts
                        ADD CONSTRAINT unique_provider_account 
                        UNIQUE ("providerId", "accountId");
                    """)
                )
                
                # Add foreign key constraints
                await session.execute(
                    text("""
                        ALTER TABLE sessions
                        ADD CONSTRAINT fk_sessions_user
                        FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE;
                    """)
                )
                
                await session.execute(
                    text("""
                        ALTER TABLE accounts
                        ADD CONSTRAINT fk_accounts_user
                        FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE;
                    """)
                )
                
                await session.commit()
                logger.info("✅ Added security constraints and foreign keys")
                
        except Exception as e:
            # Some constraints might already exist, that's okay
            if "already exists" in str(e).lower():
                logger.info("Security constraints already exist, skipping")
            else:
                logger.warning(f"⚠️ Error adding security constraints: {e}")
    
    async def create_cleanup_procedures(self):
        """Create stored procedures for cleanup tasks."""
        try:
            async with db_manager.get_session() as session:
                # Create function to clean expired sessions
                await session.execute(
                    text("""
                        CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
                        RETURNS INTEGER AS $$
                        DECLARE
                            deleted_count INTEGER;
                        BEGIN
                            DELETE FROM sessions 
                            WHERE "expiresAt" < NOW();
                            
                            GET DIAGNOSTICS deleted_count = ROW_COUNT;
                            RETURN deleted_count;
                        END;
                        $$ LANGUAGE plpgsql;
                    """)
                )
                
                # Create function to clean expired OAuth tokens
                await session.execute(
                    text("""
                        CREATE OR REPLACE FUNCTION cleanup_expired_oauth_tokens()
                        RETURNS INTEGER AS $$
                        DECLARE
                            updated_count INTEGER;
                        BEGIN
                            UPDATE accounts 
                            SET "accessToken" = NULL, "refreshToken" = NULL 
                            WHERE "expiresAt" < NOW();
                            
                            GET DIAGNOSTICS updated_count = ROW_COUNT;
                            RETURN updated_count;
                        END;
                        $$ LANGUAGE plpgsql;
                    """)
                )
                
                await session.commit()
                logger.info("✅ Created cleanup procedures")
                
        except Exception as e:
            logger.warning(f"⚠️ Error creating cleanup procedures: {e}")
    
    async def verify_migration(self):
        """Verify that the migration completed successfully."""
        try:
            async with db_manager.get_session() as session:
                # Check that all tables exist
                tables_to_check = ['users', 'sessions', 'accounts']
                for table_name in tables_to_check:
                    result = await session.execute(
                        text(f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = '{table_name}'
                            );
                        """)
                    )
                    if not result.scalar():
                        raise Exception(f"Table {table_name} was not created")
                
                # Check that indexes exist
                result = await session.execute(
                    text("""
                        SELECT COUNT(*) FROM pg_indexes 
                        WHERE tablename IN ('users', 'sessions', 'accounts');
                    """)
                )
                index_count = result.scalar()
                
                # Get user count
                result = await session.execute(select(func.count(User.id)))
                user_count = result.scalar()
                
                logger.info(f"✅ Migration verification completed:")
                logger.info(f"   - All 3 Better Auth tables created")
                logger.info(f"   - {index_count} indexes created")
                logger.info(f"   - {user_count} users in database")
                
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            raise
    
    async def run_migration(self):
        """Run the complete Better Auth migration."""
        logger.info("🚀 Starting Better Auth migration...")
        
        # Check if migration already completed
        if await self.check_migration_status():
            logger.info("✅ Better Auth migration already completed")
            return
        
        try:
            # Step 1: Backup existing data
            logger.info("📦 Step 1: Backing up existing data...")
            await self.backup_existing_data()
            
            # Step 2: Create Better Auth tables
            logger.info("🗃️ Step 2: Creating Better Auth tables...")
            await self.create_better_auth_tables()
            
            # Step 3: Migrate existing cms_users data
            logger.info("📊 Step 3: Migrating existing user data...")
            await self.migrate_cms_users_data()
            
            # Step 4: Create sample admin user if needed
            logger.info("👤 Step 4: Creating sample admin user...")
            await self.create_sample_admin_user()
            
            # Step 5: Add security constraints
            logger.info("🔒 Step 5: Adding security constraints...")
            await self.add_security_constraints()
            
            # Step 6: Create cleanup procedures
            logger.info("🧹 Step 6: Creating cleanup procedures...")
            await self.create_cleanup_procedures()
            
            # Step 7: Verify migration
            logger.info("✅ Step 7: Verifying migration...")
            await self.verify_migration()
            
            logger.info("🎉 Better Auth migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Better Auth migration failed: {e}")
            raise


async def run_better_auth_migration():
    """Run the Better Auth migration."""
    migration = BetterAuthMigration()
    await migration.run_migration()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migration
    asyncio.run(run_better_auth_migration())
