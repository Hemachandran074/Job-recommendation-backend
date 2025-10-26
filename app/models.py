"""
SQLAlchemy database models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from app.database import Base
from app.config import settings


class Job(Base):
    """Job listing model with vector embeddings"""
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    skills = Column(JSON, nullable=True)  # List of required skills
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    job_type = Column(String(50), nullable=True)  # full-time, part-time, internship
    experience_level = Column(String(50), nullable=True)  # entry, mid, senior
    remote = Column(Boolean, default=False)
    url = Column(String(500), nullable=True)
    source = Column(String(100), nullable=True)  # rapidapi, manual, dummy, etc.
    
    # Vector embedding for semantic search (nullable for now - generate later if needed)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}')>"


class User(Base):
    """User model with profile and resume embeddings"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Optional for now
    
    # Profile information
    skills = Column(JSON, nullable=True)  # List of user skills (e.g., ["Python", "Machine Learning"])
    preferred_job_titles = Column(JSON, nullable=True)  # Job titles user wants (e.g., ["Software Engineer", "ML Engineer"])
    experience_years = Column(Integer, nullable=True)
    experience_level = Column(String(50), nullable=True)  # Entry, Mid, Senior
    preferred_job_type = Column(String(50), nullable=True)  # Full Time, Part Time, etc.
    preferred_locations = Column(JSON, nullable=True)  # Cities user wants (e.g., ["Bangalore", "Chennai"])
    resume_text = Column(Text, nullable=True)
    
    # Additional profile fields
    location = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    linkedin = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)
    portfolio = Column(String(255), nullable=True)
    
    # Vector embedding for user profile/resume
    resume_embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    
    # Authentication
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"


class JobApplication(Base):
    """Track user job applications"""
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    status = Column(String(50), default="applied")  # applied, interviewing, rejected, accepted
    notes = Column(Text, nullable=True)
    
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<JobApplication(user_id='{self.user_id}', job_id='{self.job_id}')>"
