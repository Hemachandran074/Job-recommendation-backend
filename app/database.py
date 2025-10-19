"""
Database connection and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,  # Use NullPool for serverless deployments
    pool_pre_ping=True,  # Verify connections before using
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
    """
    Dependency for getting database sessions
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables and enable pgvector"""
    from sqlalchemy import text
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        async with engine.begin() as conn:
            # Enable pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("✅ pgvector extension enabled")
            except Exception as e:
                logger.warning(f"⚠️ pgvector extension setup: {e}")
            
            # Import models to ensure they're registered
            from app import models
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created")
            
            # Create indexes for better performance
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON jobs 
                    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
                """))
            except Exception as e:
                logger.warning(f"⚠️ Could not create jobs embedding index: {e}")
            
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_resume_embedding ON users 
                    USING ivfflat (resume_embedding vector_cosine_ops) WITH (lists = 100);
                """))
            except Exception as e:
                logger.warning(f"⚠️ Could not create users embedding index: {e}")
            
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs (created_at DESC);
                """))
            except Exception as e:
                logger.warning(f"⚠️ Could not create jobs timestamp index: {e}")
            
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company);
                """))
            except Exception as e:
                logger.warning(f"⚠️ Could not create jobs company index: {e}")
            
            logger.info("✅ Database initialization complete")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    await engine.dispose()
