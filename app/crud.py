"""
CRUD operations for database
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Job, User, JobApplication
from app.schemas import JobCreate, UserCreate, UserUpdate
from app.ml_service import ml_service
import logging

logger = logging.getLogger(__name__)


# ============= Job CRUD =============

async def create_job(db: AsyncSession, job_data: JobCreate) -> Job:
    """
    Create a new job with embedding
    
    Args:
        db: Database session
        job_data: Job creation data
        
    Returns:
        Created job object
    """
    # Generate embedding for the job
    job_dict = job_data.model_dump()
    job_text = ml_service.create_job_text(job_dict)
    embedding = ml_service.generate_embedding(job_text)
    
    # Create job object
    db_job = Job(**job_dict, embedding=embedding)
    
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    logger.info(f"Created job: {db_job.id} - {db_job.title}")
    return db_job


async def get_job(db: AsyncSession, job_id: UUID) -> Optional[Job]:
    """Get a job by ID"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def get_jobs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    remote_only: bool = False
) -> List[Job]:
    """Get list of jobs with filters"""
    query = select(Job)
    
    if job_type:
        query = query.where(Job.job_type == job_type)
    
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    
    if remote_only:
        query = query.where(Job.remote == True)
    
    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def search_jobs_by_similarity(
    db: AsyncSession,
    query_embedding: List[float],
    limit: int = 10,
    min_score: float = 0.5,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    remote_only: bool = False
) -> List[tuple[Job, float]]:
    """
    Search jobs using vector similarity
    
    Args:
        db: Database session
        query_embedding: Query vector embedding
        limit: Maximum number of results
        min_score: Minimum similarity score (0-1)
        job_type: Filter by job type
        location: Filter by location
        remote_only: Filter remote jobs only
        
    Returns:
        List of (Job, similarity_score) tuples
    """
    # Convert embedding to string format for SQL
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    # Build the query
    sql_query = """
        SELECT 
            jobs.*,
            1 - (jobs.embedding <=> :embedding::vector) as similarity
        FROM jobs
        WHERE 1 - (jobs.embedding <=> :embedding::vector) >= :min_score
    """
    
    params = {
        "embedding": embedding_str,
        "min_score": min_score
    }
    
    # Add filters
    if job_type:
        sql_query += " AND jobs.job_type = :job_type"
        params["job_type"] = job_type
    
    if location:
        sql_query += " AND jobs.location ILIKE :location"
        params["location"] = f"%{location}%"
    
    if remote_only:
        sql_query += " AND jobs.remote = TRUE"
    
    sql_query += " ORDER BY similarity DESC LIMIT :limit"
    params["limit"] = limit
    
    result = await db.execute(text(sql_query), params)
    rows = result.fetchall()
    
    # Convert to Job objects with scores
    jobs_with_scores = []
    for row in rows:
        job = Job(
            id=row.id,
            title=row.title,
            company=row.company,
            location=row.location,
            description=row.description,
            skills=row.skills,
            salary_min=row.salary_min,
            salary_max=row.salary_max,
            job_type=row.job_type,
            experience_level=row.experience_level,
            remote=row.remote,
            url=row.url,
            source=row.source,
            embedding=row.embedding,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        jobs_with_scores.append((job, float(row.similarity)))
    
    return jobs_with_scores


async def get_job_count(db: AsyncSession) -> int:
    """Get total number of jobs"""
    result = await db.execute(select(func.count(Job.id)))
    return result.scalar()


# ============= User CRUD =============

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user with profile embedding
    
    Args:
        db: Database session
        user_data: User creation data
        
    Returns:
        Created user object
    """
    user_dict = user_data.model_dump(exclude={"password"})
    
    # Generate embedding if profile data exists
    resume_embedding = None
    if any([user_data.skills, user_data.resume_text, user_data.preferred_job_type]):
        profile_text = ml_service.create_user_profile_text(user_dict)
        resume_embedding = ml_service.generate_embedding(profile_text)
    
    # Hash password if provided
    hashed_password = None
    if user_data.password:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(user_data.password)
    
    # Create user object
    db_user = User(
        **user_dict,
        hashed_password=hashed_password,
        resume_embedding=resume_embedding
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    logger.info(f"Created user: {db_user.id} - {db_user.email}")
    return db_user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
    """Update user profile"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Regenerate embedding if profile changed
    if any(field in update_data for field in ['skills', 'resume_text', 'preferred_job_type', 'preferred_locations']):
        user_dict = {
            'skills': user.skills,
            'resume_text': user.resume_text,
            'preferred_job_type': user.preferred_job_type,
            'preferred_locations': user.preferred_locations,
            'experience_years': user.experience_years
        }
        profile_text = ml_service.create_user_profile_text(user_dict)
        user.resume_embedding = ml_service.generate_embedding(profile_text)
    
    await db.commit()
    await db.refresh(user)
    
    return user


# ============= Job Application CRUD =============

async def create_application(db: AsyncSession, user_id: UUID, job_id: UUID) -> JobApplication:
    """Create a job application"""
    application = JobApplication(user_id=user_id, job_id=job_id)
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def get_user_applications(db: AsyncSession, user_id: UUID) -> List[JobApplication]:
    """Get all applications for a user"""
    result = await db.execute(
        select(JobApplication).where(JobApplication.user_id == user_id)
    )
    return result.scalars().all()
