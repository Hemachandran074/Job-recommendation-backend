"""
Manually add a user to the database
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import User
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

async def add_user():
    """Add a user to the database"""
    print("📝 Add New User\n")
    
    # Get user input
    name = input("Name: ")
    email = input("Email: ")
    password = input("Password: ")
    
    # Optional fields
    print("\n📋 Optional fields (press Enter to skip):")
    phone = input("Phone: ") or None
    location = input("Location: ") or None
    bio = input("Bio: ") or None
    
    # Skills
    skills_input = input("Skills (comma-separated): ")
    skills = [s.strip() for s in skills_input.split(",")] if skills_input else []
    
    print(f"\n🔐 Creating user: {email}")
    
    async with AsyncSessionLocal() as db:
        try:
            # Create user
            user = User(
                name=name,
                email=email,
                hashed_password=hash_password(password),
                phone=phone,
                location=location,
                bio=bio,
                skills=skills if skills else None,
                is_active=True,
                is_verified=True  # Auto-verify manual users
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            print(f"\n✅ User created successfully!")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Skills: {user.skills}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(add_user())
