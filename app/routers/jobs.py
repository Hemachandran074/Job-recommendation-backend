"""
Job management endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import JobCreate, JobResponse, JobIngest
from app import crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/ingest", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def ingest_job(
    job_data: JobIngest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a job from external sources (RapidAPI, manual upload, etc.)
    
    This endpoint:
    1. Accepts job data
    2. Generates ML embedding from job description
    3. Stores job with embedding in database
    
    Returns the created job with its ID
    """
    try:
        # Convert to JobCreate (removes external_id)
        job_create = JobCreate(**job_data.model_dump(exclude={"external_id"}))
        
        # Create job with embedding
        job = await crud.create_job(db, job_create)
        
        return job
    except Exception as e:
        logger.error(f"Error ingesting job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest job: {str(e)}"
        )


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job listing
    
    Similar to /ingest but for manual job creation
    """
    try:
        job = await crud.create_job(db, job_data)
        return job
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job by ID"""
    job = await crud.get_job(db, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    job_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    remote_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    List jobs with optional filters
    
    Query parameters:
    - skip: Number of jobs to skip (pagination)
    - limit: Maximum number of jobs to return
    - job_type: Filter by job type (full-time, part-time, internship)
    - location: Filter by location (partial match)
    - remote_only: Only return remote jobs
    """
    jobs = await crud.get_jobs(
        db,
        skip=skip,
        limit=limit,
        job_type=job_type,
        location=location,
        remote_only=remote_only
    )
    
    return jobs


@router.get("/count/total")
async def get_job_count(db: AsyncSession = Depends(get_db)):
    """Get total number of jobs in database"""
    count = await crud.get_job_count(db)
    return {"total_jobs": count}
