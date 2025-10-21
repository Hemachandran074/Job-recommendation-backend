#!/usr/bin/env python3
"""
Database migration script to add missing columns
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import get_engine
from app.config import settings

async def migrate_database():
    """Add missing columns to the users table"""
    print("🔄 Starting database migration...")
    
    engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            # Check if location column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'location'
            """))
            
            if result.fetchone() is None:
                print("➕ Adding missing columns to users table...")
                
                # Add missing columns
                await conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS location VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS bio TEXT,
                    ADD COLUMN IF NOT EXISTS linkedin VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS github VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS portfolio VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS resume_embedding vector(768),
                    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                    ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false,
                    ADD COLUMN IF NOT EXISTS last_login TIMESTAMP
                """))
                
                print("✅ Missing columns added successfully!")
            else:
                print("✅ All columns already exist")
            
            # Check if pgvector extension is enabled
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                print("✅ pgvector extension enabled")
            except Exception as e:
                print(f"⚠️  pgvector extension: {e}")
            
            # Create indexes for better performance
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                    CREATE INDEX IF NOT EXISTS idx_users_location ON users(location);
                """))
                print("✅ Indexes created")
            except Exception as e:
                print(f"⚠️  Index creation: {e}")
                
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(migrate_database())
    sys.exit(0 if success else 1)
