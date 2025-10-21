#!/usr/bin/env python3
"""
Force recreate database tables with correct schema
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import get_engine, Base
from app.config import settings

async def recreate_tables():
    """Drop and recreate all tables with correct schema"""
    print("🔄 Recreating database tables...")
    
    engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            print("🗑️  Dropping existing tables...")
            
            # Drop all tables
            await conn.execute(text("DROP TABLE IF EXISTS job_applications CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS jobs CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            
            print("✅ Tables dropped")
            
            # Enable pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                print("✅ pgvector extension enabled")
            except Exception as e:
                print(f"⚠️  pgvector extension: {e}")
            
            print("🏗️  Creating new tables...")
            
            # Create all tables from models
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully")
            
            # Create indexes
            try:
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)"))
                print("✅ Indexes created")
            except Exception as e:
                print(f"⚠️  Index creation: {e}")
                
        print("✅ Database recreation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Recreation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(recreate_tables())
    sys.exit(0 if success else 1)
