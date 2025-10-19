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
    
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # Import models to ensure they're registered
        from app import models
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Create indexes for better performance
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON jobs 
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_resume_embedding ON users 
            USING ivfflat (resume_embedding vector_cosine_ops) WITH (lists = 100);
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs (created_at DESC);
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company);
        """))


async def close_db():
    """Close database connections"""
    await engine.dispose()
