"""
Reset database - Drop and recreate all tables
WARNING: This will delete all data!
Use this when changing embedding dimensions or schema
"""
import asyncio
from sqlalchemy import text
from app.database import engine, init_db

async def reset_database():
    """Drop all tables and recreate them"""
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print("📝 This is needed when changing embedding dimensions (384 → 768)")
    response = input("Type 'yes' to continue: ")
    
    if response.lower() != 'yes':
        print("❌ Aborted")
        return
    
    print("\n🗑️  Dropping all tables...")
    async with engine.begin() as conn:
        # Drop all tables
        await conn.execute(text("DROP TABLE IF EXISTS job_applications CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS jobs CASCADE"))
        print("✅ Tables dropped")
    
    print("\n📦 Creating tables with new schema (768 dimensions)...")
    await init_db()
    print("✅ Database reset complete!")
    print("\n💡 Next: Run the backend and ingest jobs from RapidAPI")

if __name__ == "__main__":
    asyncio.run(reset_database())
