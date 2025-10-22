"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator


# ============= Job Schemas =============

class JobBase(BaseModel):
    """Base job schema"""
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    description: str = Field(..., min_length=10)
    skills: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = Field(None, max_length=50)
    experience_level: Optional[str] = Field(None, max_length=50)
    remote: bool = False
    url: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field("manual", max_length=100)


class JobCreate(JobBase):
    """Schema for creating a job"""
    pass


class JobIngest(JobBase):
    """Schema for ingesting jobs from external sources"""
    external_id: Optional[str] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobWithScore(JobResponse):
    """Job response with similarity score"""
    similarity_score: float = Field(..., ge=0, le=1, description="Cosine similarity score")


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6, max_length=100)  # Required, min 6 chars
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    preferred_job_type: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    resume_text: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    preferred_job_type: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    resume_text: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    preferred_job_type: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Recommendation Schemas =============

class RecommendationQuery(BaseModel):
    """Schema for recommendation request"""
    query: Optional[str] = Field(None, description="Text query for job search")
    user_id: Optional[UUID] = Field(None, description="User ID for personalized recommendations")
    limit: int = Field(10, ge=1, le=100, description="Number of recommendations")
    min_score: float = Field(0.5, ge=0, le=1, description="Minimum similarity score")
    job_type: Optional[str] = None
    location: Optional[str] = None
    remote_only: bool = False
    
    @validator('query', 'user_id')
    def check_query_or_user(cls, v, values):
        """Ensure at least query or user_id is provided"""
        if 'query' in values and not values.get('query') and not v:
            raise ValueError('Either query or user_id must be provided')
        return v


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    jobs: List[JobWithScore]
    total: int
    query_used: Optional[str] = None


# ============= Authentication Schemas =============

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload schema"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


# ============= Health Check Schema =============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    ml_model: str
    timestamp: datetime
