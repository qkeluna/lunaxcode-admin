"""
PostgreSQL database connection and session management using SQLAlchemy.
"""

import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import settings
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DatabaseManager:
    """PostgreSQL database manager with async support."""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections."""
        if self._initialized:
            return
        
        if not settings.DATABASE_URL:
            raise DatabaseError(
                "DATABASE_URL must be set for PostgreSQL connection",
                operation="initialize"
            )
        
        try:
            # Convert DATABASE_URL to async format using Neon's recommended approach
            import re
            
            # First remove problematic query parameters that asyncpg doesn't support
            db_url = settings.DATABASE_URL
            # Remove sslmode parameter as asyncpg uses different SSL handling
            db_url = re.sub(r'[?&]sslmode=[^&]*', '', db_url)
            # Remove other problematic parameters
            db_url = re.sub(r'[?&]channel_binding=[^&]*', '', db_url)
            
            # Then convert to async format
            db_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', db_url)
            
            # Create async engine
            self.async_engine = create_async_engine(
                db_url,
                echo=settings.DEBUG,
                future=True,
                pool_pre_ping=True,
                pool_recycle=300,
                # Connection pool settings
                pool_size=10,
                max_overflow=20,
            )
            
            # Create async session factory
            self.AsyncSessionLocal = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            
            # Test connection
            await self.health_check()
            self._initialized = True
            logger.info("✅ PostgreSQL database connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL connection: {e}")
            raise DatabaseError(f"Failed to initialize database: {str(e)}", operation="initialize")
    
    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        
        self.async_engine = None
        self.AsyncSessionLocal = None
        self._initialized = False
        logger.info("✅ PostgreSQL database connection closed")
    
    async def health_check(self):
        """Check database health."""
        if not self.async_engine:
            raise DatabaseError("Database not initialized", operation="health_check")
        
        try:
            from sqlalchemy import text
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ PostgreSQL health check successful")
        except Exception as e:
            logger.error(f"❌ PostgreSQL health check failed: {e}")
            raise DatabaseError(f"Health check failed: {str(e)}", operation="health_check")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if not self.AsyncSessionLocal:
            await self.initialize()
        
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all database tables."""
        if not self.async_engine:
            await self.initialize()
        
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise DatabaseError(f"Failed to create tables: {str(e)}", operation="create_tables")
    
    async def drop_tables(self):
        """Drop all database tables."""
        if not self.async_engine:
            await self.initialize()
        
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("✅ Database tables dropped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to drop tables: {e}")
            raise DatabaseError(f"Failed to drop tables: {str(e)}", operation="drop_tables")


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """Initialize database and create tables."""
    await db_manager.initialize()
    await db_manager.create_tables()


async def close_database():
    """Close database connections."""
    await db_manager.close()
