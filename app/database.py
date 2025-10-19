"""
Database connection and session management
"""
import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to False to reduce logging
    poolclass=NullPool,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables, extensions)"""
    try:
        logger.info("🔄 Testing database connection...")

        # Test connection - FIX: Use text() for raw SQL
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful!")

            # Enable pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("✅ pgvector extension enabled")
            except Exception as e:
                logger.warning(f"⚠️  pgvector extension: {e}")

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created/verified")

            # Create indexes (optional - skip if fails)
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_job_embedding 
                    ON jobs USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """))
                logger.info("✅ Job embedding index created")
            except Exception as e:
                logger.warning(f"⚠️  Index creation skipped: {e}")

            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_user_embedding 
                    ON users USING ivfflat (resume_embedding vector_cosine_ops)
                    WITH (lists = 100)
                """))
                logger.info("✅ User embedding index created")
            except Exception as e:
                logger.warning(f"⚠️  Index creation skipped: {e}")

    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        logger.warning("⚠️  Starting app without database (read-only mode)")


async def close_db():
    """Close database connection"""
    try:
        await engine.dispose()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")
