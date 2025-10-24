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
            .where(Job.posted_date >= cutoff_date)
            .order_by(desc(Job.posted_date))
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
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
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
