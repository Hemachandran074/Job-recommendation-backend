"""
RapidAPI Router
Endpoints for fetching and ingesting jobs/internships from RapidAPI
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import httpx
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Job
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# RapidAPI Configuration - Using Internships API
RAPIDAPI_BASE_URL = "https://internships-api.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
    "X-RapidAPI-Host": "internships-api.p.rapidapi.com"
}


async def fetch_jobs_from_rapidapi(
    query: str = "software",
    location: str = "India",
    limit: int = 20
) -> List[dict]:
    """
    Fetch jobs/internships from RapidAPI Internships API
    
    Parameters:
    - query: Search query for job/internship title
    - location: Location filter
    - limit: Number of results to return (default 20)
    """
    try:
        # Build query parameters for Internships API
        params = {
            "query": query,
            "location": location,
            "limit": str(limit)
        }
        
        logger.info(f"📡 Fetching jobs from RapidAPI Internships API with params: {params}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try the active-jb-7d endpoint (active jobs in last 7 days)
            response = await client.get(
                f"{RAPIDAPI_BASE_URL}/active-jb-7d",
                headers=RAPIDAPI_HEADERS,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # The API returns a list directly or wrapped in a data field
            if isinstance(data, list):
                jobs = data
            elif isinstance(data, dict):
                jobs = data.get("data", []) or data.get("jobs", []) or data.get("internships", [])
            else:
                jobs = []
            
            logger.info(f"✅ Fetched {len(jobs)} jobs from RapidAPI")
            
            return jobs
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ RapidAPI HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"RapidAPI error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"❌ Error fetching from RapidAPI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch jobs: {str(e)}"
        )


def transform_rapidapi_job(api_job: dict) -> dict:
    """
    Transform RapidAPI job data to our database schema
    """
    return {
        "title": api_job.get("title", ""),
        "company": api_job.get("company", "Unknown Company"),
        "location": api_job.get("location", ""),
        "job_type": api_job.get("employment_type", "Full Time"),
        "remote": api_job.get("remote", False),
        "description": api_job.get("description", ""),
        "skills": api_job.get("required_skills", []) or [],
        "url": api_job.get("url", ""),
        "salary_min": api_job.get("salary_min"),
        "salary_max": api_job.get("salary_max"),
        "experience_required": api_job.get("experience_required"),
        # AI-enriched fields (if include_ai=true)
        "ai_salary": api_job.get("ai_salary"),
        "ai_skills": api_job.get("ai_skills", []),
        "ai_work_arrangement": api_job.get("ai_work_arrangement"),
    }


@router.post("/ingest/jobs")
async def ingest_jobs(
    background_tasks: BackgroundTasks,
    query: str = "software engineer",
    location: str = "India",
    total_jobs: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest jobs/internships from RapidAPI Internships API into database
    
    Parameters:
    - query: Search query (e.g., "software engineer", "data scientist", "python")
    - location: Location to search (e.g., "India", "Bangalore", "Mumbai")
    - total_jobs: Total number of jobs to fetch (default 50)
    
    Example usage:
    POST /api/v1/rapidapi/ingest/jobs?query=python developer&location=Bangalore&total_jobs=50
    """
    try:
        logger.info(f"🚀 Starting job ingestion: {total_jobs} jobs for '{query}' in '{location}'")
        
        # Fetch jobs from RapidAPI
        all_jobs = await fetch_jobs_from_rapidapi(
            query=query,
            location=location,
            limit=total_jobs
        )
        
        logger.info(f"📦 Fetched total of {len(all_jobs)} jobs from RapidAPI")
        
        # Transform and store jobs
        stored_count = 0
        duplicate_count = 0
        
        for api_job in all_jobs:
            try:
                job_data = transform_rapidapi_job(api_job)
                
                # Check if job already exists (by URL or title+company)
                from sqlalchemy import select, or_
                result = await db.execute(
                    select(Job).where(
                        or_(
                            Job.url == job_data["url"],
                            (Job.title == job_data["title"]) & (Job.company == job_data["company"])
                        )
                    )
                )
                existing_job = result.scalar_one_or_none()
                
                if existing_job:
                    duplicate_count += 1
                    continue
                
                # Create new job
                new_job = Job(**job_data)
                db.add(new_job)
                stored_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to store job: {e}")
                continue
        
        await db.commit()
        
        logger.info(f"✅ Ingestion complete: {stored_count} new jobs stored, {duplicate_count} duplicates skipped")
        
        return {
            "status": "success",
            "total_fetched": len(all_jobs),
            "stored": stored_count,
            "duplicates": duplicate_count,
            "search_params": {
                "query": query,
                "location": location
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Job ingestion failed: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Job ingestion failed: {str(e)}"
        )


@router.get("/search/jobs")
async def search_jobs(
    query: str = "software engineer",
    location: str = "India",
    limit: int = 10
):
    """
    Search jobs from RapidAPI without storing (live search)
    
    Returns raw results from RapidAPI Internships API
    """
    try:
        jobs = await fetch_jobs_from_rapidapi(
            query=query,
            location=location,
            limit=limit
        )
        
        return {
            "status": "success",
            "count": len(jobs),
            "jobs": jobs,
            "search_params": {
                "query": query,
                "location": location
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Job search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Job search failed: {str(e)}"
        )


@router.get("/test")
async def test_rapidapi_connection():
    """
    Test RapidAPI connection and credentials
    """
    try:
        # Try fetching just 1 job to test connection
        jobs = await fetch_jobs_from_rapidapi(
            query="engineer",
            location="India",
            limit=1
        )
        
        return {
            "status": "success",
            "message": "RapidAPI connection working",
            "api_key_valid": True,
            "sample_job_count": len(jobs),
            "sample_job": jobs[0] if jobs else None
        }
        
    except Exception as e:
        logger.error(f"❌ RapidAPI test failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "api_key_valid": False
        }
