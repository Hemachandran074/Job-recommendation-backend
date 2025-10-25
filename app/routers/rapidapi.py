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

# RapidAPI Job Search API Configuration
RAPIDAPI_BASE_URL = "https://job-search-api1.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
    "X-RapidAPI-Host": "job-search-api1.p.rapidapi.com"
}


async def fetch_jobs_from_rapidapi(
    title_filter: str = "software engineer",
    location_filter: str = "India",
    remote: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
    date_filter: Optional[str] = None,
    include_ai: bool = True,
    ai_work_arrangement_filter: Optional[str] = None,
    description_type: str = "text"
) -> List[dict]:
    """
    Fetch jobs from RapidAPI Job Search API
    
    Parameters (as per official documentation):
    - title_filter: Search/filter jobs by title (Google-like syntax)
    - location_filter: Filter by location (city/state/country)
    - remote: true/false/None - filter remote-only, non-remote, or both
    - limit: Number of jobs to return (max 10 per request)
    - offset: Pagination offset
    - date_filter: Filter jobs after date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    - include_ai: Include AI-enriched fields (salary, skills, etc.)
    - ai_work_arrangement_filter: On-site, Hybrid, Remote OK, Remote Solely
    - description_type: 'text' or 'html'
    """
    try:
        # Build query parameters according to official API docs
        params = {
            "title_filter": title_filter,
            "location_filter": location_filter,
            "limit": min(limit, 10),  # Max 10 per request
            "offset": offset,
            "description_type": description_type,
            "include_ai": str(include_ai).lower(),
        }
        
        # Add optional parameters
        if remote is not None:
            params["remote"] = str(remote).lower()
        
        if date_filter:
            params["date_filter"] = date_filter
        
        if ai_work_arrangement_filter:
            params["ai_work_arrangement_filter"] = ai_work_arrangement_filter
        
        logger.info(f"📡 Fetching jobs from RapidAPI with params: {params}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{RAPIDAPI_BASE_URL}/jobs",
                headers=RAPIDAPI_HEADERS,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get("jobs", [])
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
    title_filter: str = "software engineer",
    location_filter: str = "India",
    remote: Optional[bool] = None,
    total_jobs: int = 50,
    include_ai: bool = True,
    date_filter: Optional[str] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest jobs from RapidAPI Job Search API into database
    
    Parameters:
    - title_filter: Job title to search (e.g., "software engineer", "data scientist")
    - location_filter: Location to search (e.g., "India", "Bangalore India", "United States")
    - remote: Filter for remote jobs (true/false/None for both)
    - total_jobs: Total number of jobs to fetch (will make multiple API calls of 10 each)
    - include_ai: Include AI-enriched data (salary, skills, work arrangement)
    - date_filter: Only jobs posted after this date (YYYY-MM-DD)
    - ai_work_arrangement_filter: Filter by arrangement (On-site, Hybrid, Remote OK, Remote Solely)
    
    Example usage:
    POST /api/v1/rapidapi/ingest/jobs?title_filter=python developer&location_filter=Bangalore India&remote=true&total_jobs=50
    """
    try:
        logger.info(f"🚀 Starting job ingestion: {total_jobs} jobs for '{title_filter}' in '{location_filter}'")
        
        all_jobs = []
        limit_per_request = 10  # API max
        num_requests = (total_jobs + limit_per_request - 1) // limit_per_request
        
        # Make multiple requests to fetch all jobs
        for i in range(num_requests):
            offset = i * limit_per_request
            
            jobs_batch = await fetch_jobs_from_rapidapi(
                title_filter=title_filter,
                location_filter=location_filter,
                remote=remote,
                limit=limit_per_request,
                offset=offset,
                date_filter=date_filter,
                include_ai=include_ai,
                ai_work_arrangement_filter=ai_work_arrangement_filter
            )
            
            all_jobs.extend(jobs_batch)
            
            # Stop if we got fewer jobs than requested (no more available)
            if len(jobs_batch) < limit_per_request:
                break
        
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
                "title_filter": title_filter,
                "location_filter": location_filter,
                "remote": remote,
                "include_ai": include_ai
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
    title_filter: str = "software engineer",
    location_filter: str = "India",
    remote: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
    include_ai: bool = True,
    date_filter: Optional[str] = None,
    ai_work_arrangement_filter: Optional[str] = None
):
    """
    Search jobs from RapidAPI without storing (live search)
    
    Returns raw results from RapidAPI Job Search API
    """
    try:
        jobs = await fetch_jobs_from_rapidapi(
            title_filter=title_filter,
            location_filter=location_filter,
            remote=remote,
            limit=limit,
            offset=offset,
            include_ai=include_ai,
            date_filter=date_filter,
            ai_work_arrangement_filter=ai_work_arrangement_filter
        )
        
        return {
            "status": "success",
            "count": len(jobs),
            "jobs": jobs,
            "search_params": {
                "title_filter": title_filter,
                "location_filter": location_filter,
                "remote": remote,
                "include_ai": include_ai
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
            title_filter="engineer",
            location_filter="India",
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
