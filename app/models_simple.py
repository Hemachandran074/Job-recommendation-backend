"""
Simplified User model that matches the actual database schema
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class User(Base):
    """Simplified User model matching actual database schema"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)
    
    # Basic profile fields that exist in the database
    skills = Column(Text, nullable=True)  # Store as JSON string
    experience_years = Column(Integer, nullable=True)
    preferred_job_type = Column(String(50), nullable=True)
    preferred_locations = Column(Text, nullable=True)  # Store as JSON string
    resume_text = Column(Text, nullable=True)
    
    # Authentication
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"
