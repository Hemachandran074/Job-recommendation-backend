#!/usr/bin/env python3
"""
Database schema fix - Add missing columns to existing users table
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import get_engine

async def fix_database_schema():
    """Add missing columns to the users table"""
    print("🔄 Fixing database schema...")
    
    engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            # Check current table structure
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY column_name
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"📋 Existing columns: {existing_columns}")
            
            # Add missing columns one by one
            missing_columns = [
                ("location", "VARCHAR(255)"),
                ("phone", "VARCHAR(50)"),
                ("bio", "TEXT"),
                ("linkedin", "VARCHAR(255)"),
                ("github", "VARCHAR(255)"),
                ("portfolio", "VARCHAR(255)"),
                ("resume_embedding", "vector(768)"),
            ]
            
            for column_name, column_type in missing_columns:
                if column_name not in existing_columns:
                    try:
                        await conn.execute(text(f"""
                            ALTER TABLE users 
                            ADD COLUMN {column_name} {column_type}
                        """))
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"⚠️  Failed to add {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            # Enable pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                print("✅ pgvector extension enabled")
            except Exception as e:
                print(f"⚠️  pgvector extension: {e}")
                
        print("✅ Database schema fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database_schema())
    sys.exit(0 if success else 1)
