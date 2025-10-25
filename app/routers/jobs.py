"""
Jobs Router
Endpoints for job listings and searches
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Job
from app.schemas import JobResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    job_type: Optional[str] = None,
    remote: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all jobs with optional filters and pagination
    
    Parameters:
    - skip: Number of jobs to skip (for pagination)
    - limit: Maximum number of jobs to return (1-100)
    - job_type: Filter by job type (e.g., 'full-time', 'internship')
    - remote: Filter by remote status (true/false)
    """
    try:
        # Build query
        query = select(Job).order_by(desc(Job.created_at))
        
        # Apply filters
        if job_type:
            query = query.where(Job.job_type == job_type)
        
        if remote is not None:
            query = query.where(Job.remote == remote)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        logger.info(f"✅ Found {len(jobs)} jobs (skip={skip}, limit={limit})")
        
        return [{
            "_id": str(job.id),  # Dashboard expects _id
            "id": str(job.id),
            "title": job.title,
            "company_name": job.company,
            "company": job.company,
            "location": job.location,
            "type": job.job_type or "Full Time",
            "job_type": job.job_type,
            "remote": job.remote,
            "salary": f"${job.salary_min or 0}-${job.salary_max or 0}" if job.salary_min else "Competitive",
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "skills": job.skills or [],
            "period": f"{(datetime.utcnow() - job.posted_date).days} days ago" if job.posted_date else "Recently",
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "created_at": job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
            "url": job.url,
        } for job in jobs]
        
    except Exception as e:
        logger.error(f"❌ Error fetching jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch jobs: {str(e)}"
        )


@router.get("/recent")
async def get_recent_jobs(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recently posted jobs (last N days)
    
    Parameters:
    - limit: Maximum number of jobs to return (1-100)
    - days: Number of days to look back (1-30, default: 7)
    """
    try:
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query recent jobs
        result = await db.execute(
            select(Job)
            .where(Job.created_at >= cutoff_date)
            .order_by(desc(Job.created_at))
            .limit(limit)
        )
        jobs = result.scalars().all()
        
        logger.info(f"✅ Found {len(jobs)} recent jobs (last {days} days)")
        
        return [{
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "remote": job.remote,
            "description": job.description,
            "skills": job.skills,
            "posted_date": job.created_at.isoformat() if job.created_at else None,
            "url": job.url,
        } for job in jobs]
        
    except Exception as e:
        logger.error(f"❌ Error fetching recent jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent jobs: {str(e)}"
        )


@router.get("/all")
async def get_all_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all jobs with pagination
    """
    try:
        result = await db.execute(
            select(Job)
            .order_by(desc(Job.posted_date))
            .offset(skip)
            .limit(limit)
        )
        jobs = result.scalars().all()
        
        return [{
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "remote": job.remote,
            "description": job.description,
            "skills": job.skills,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
        } for job in jobs]
        
    except Exception as e:
        logger.error(f"❌ Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}")
async def get_job_by_id(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific job by ID
    """
    try:
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "remote": job.remote,
            "description": job.description,
            "skills": job.skills,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "url": job.url,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
