#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, get_engine
from app.config import settings
from app.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def test_backend():
    """Test basic backend functionality"""
    print("🧪 Testing Backend Functionality...")
    
    try:
        # Test database connection
        print("1. Testing database connection...")
        await init_db()
        print("✅ Database connection successful")
        
        # Test user creation
        print("2. Testing user creation...")
        engine = get_engine()
        async with AsyncSession(engine) as session:
            # Check if users table exists
            result = await session.execute(select(User).limit(1))
            users = result.scalars().all()
            print(f"✅ Users table accessible, found {len(users)} users")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1)
