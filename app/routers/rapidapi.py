"""
RapidAPI Router
Endpoints for fetching and ingesting jobs/internships from RapidAPI
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.database import get_db
from app.schemas import JobResponse, JobIngest
from app.crud import create_job
from app.rapidapi_service import rapidapi_service
from app.ml_service import ml_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def get_rapidapi_status():
    """
    Check if RapidAPI is configured and available
    """
    is_configured = rapidapi_service.is_configured()
    
    return {
        "configured": is_configured,
        "jobs_url": rapidapi_service.jobs_url if is_configured else None,
        "internships_url": rapidapi_service.internships_url if is_configured else None,
        "message": "RapidAPI is configured and ready" if is_configured else "RapidAPI key not configured"
    }


@router.post("/fetch/jobs")
async def fetch_jobs_from_rapidapi(
    limit: Optional[int] = None,
    title_filter: Optional[str] = None,
    advanced_title_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    description_filter: Optional[str] = None,
    description_type: Optional[str] = None,
    remote: Optional[bool] = None,
    agency: Optional[bool] = None,
    offset: Optional[int] = None,
    date_filter: Optional[str] = None,
    include_ai: Optional[bool] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch jobs from RapidAPI and return them (without saving to database)
    
    Query Parameters:
    - **limit**: Maximum number of jobs to fetch (optional)
    - **title_filter**: Filter by job title
    - **advanced_title_filter**: Advanced title filtering
    - **location_filter**: Filter by location
    - **description_filter**: Filter by description
    - **description_type**: Type of description
    - **remote**: Filter for remote jobs (true/false)
    - **agency**: Filter for agency jobs (true/false)
    - **offset**: Pagination offset
    - **date_filter**: Filter by date
    - **include_ai**: Include AI jobs (true/false)
    - **ai_work_arrangement_filter**: AI work arrangement filter
    """
    if not rapidapi_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="RapidAPI is not configured. Please set RAPIDAPI_KEY in environment variables."
        )
    
    jobs = await rapidapi_service.fetch_jobs(
        limit=limit,
        title_filter=title_filter,
        advanced_title_filter=advanced_title_filter,
        location_filter=location_filter,
        description_filter=description_filter,
        description_type=description_type,
        remote=remote,
        agency=agency,
        offset=offset,
        date_filter=date_filter,
        include_ai=include_ai,
        ai_work_arrangement_filter=ai_work_arrangement_filter,
    )
    
    return {
        "source": "rapidapi",
        "type": "jobs",
        "count": len(jobs),
        "jobs": jobs
    }


@router.post("/fetch/internships")
async def fetch_internships_from_rapidapi(
    limit: Optional[int] = None,
    title_filter: Optional[str] = None,
    advanced_title_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    description_filter: Optional[str] = None,
    description_type: Optional[str] = None,
    remote: Optional[bool] = None,
    agency: Optional[bool] = None,
    offset: Optional[int] = None,
    date_filter: Optional[str] = None,
    include_ai: Optional[bool] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch internships from RapidAPI and return them (without saving to database)
    
    Query Parameters:
    - **limit**: Maximum number of internships to fetch (optional)
    - **title_filter**: Filter by internship title
    - **advanced_title_filter**: Advanced title filtering
    - **location_filter**: Filter by location
    - **description_filter**: Filter by description
    - **description_type**: Type of description
    - **remote**: Filter for remote internships (true/false)
    - **agency**: Filter for agency internships (true/false)
    - **offset**: Pagination offset
    - **date_filter**: Filter by date
    - **include_ai**: Include AI internships (true/false)
    - **ai_work_arrangement_filter**: AI work arrangement filter
    """
    if not rapidapi_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="RapidAPI is not configured. Please set RAPIDAPI_KEY in environment variables."
        )
    
    internships = await rapidapi_service.fetch_internships(
        limit=limit,
        title_filter=title_filter,
        advanced_title_filter=advanced_title_filter,
        location_filter=location_filter,
        description_filter=description_filter,
        description_type=description_type,
        remote=remote,
        agency=agency,
        offset=offset,
        date_filter=date_filter,
        include_ai=include_ai,
        ai_work_arrangement_filter=ai_work_arrangement_filter,
    )
    
    return {
        "source": "rapidapi",
        "type": "internships",
        "count": len(internships),
        "internships": internships
    }


@router.post("/fetch/all")
async def fetch_all_from_rapidapi(
    jobs_limit: Optional[int] = None,
    internships_limit: Optional[int] = None,
    title_filter: Optional[str] = None,
    advanced_title_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    description_filter: Optional[str] = None,
    description_type: Optional[str] = None,
    remote: Optional[bool] = None,
    agency: Optional[bool] = None,
    offset: Optional[int] = None,
    date_filter: Optional[str] = None,
    include_ai: Optional[bool] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch both jobs and internships from RapidAPI with optional filtering
    
    Query Parameters:
    - **jobs_limit**: Maximum number of jobs to fetch
    - **internships_limit**: Maximum number of internships to fetch
    - **title_filter**: Filter by title
    - **advanced_title_filter**: Advanced title filtering
    - **location_filter**: Filter by location
    - **description_filter**: Filter by description
    - **description_type**: Type of description
    - **remote**: Filter for remote positions (true/false)
    - **agency**: Filter for agency positions (true/false)
    - **offset**: Pagination offset
    - **date_filter**: Filter by date
    - **include_ai**: Include AI positions (true/false)
    - **ai_work_arrangement_filter**: AI work arrangement filter
    """
    if not rapidapi_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="RapidAPI is not configured. Please set RAPIDAPI_KEY in environment variables."
        )
    
    result = await rapidapi_service.fetch_all(
        jobs_limit=jobs_limit,
        internships_limit=internships_limit,
        title_filter=title_filter,
        advanced_title_filter=advanced_title_filter,
        location_filter=location_filter,
        description_filter=description_filter,
        description_type=description_type,
        remote=remote,
        agency=agency,
        offset=offset,
        date_filter=date_filter,
        include_ai=include_ai,
        ai_work_arrangement_filter=ai_work_arrangement_filter,
    )
    
    return {
        "source": "rapidapi",
        "jobs_count": len(result["jobs"]),
        "internships_count": len(result["internships"]),
        "total_count": result["total"],
        "jobs": result["jobs"],
        "internships": result["internships"]
    }


@router.post("/ingest/jobs", response_model=dict)
async def ingest_jobs_from_rapidapi(
    limit: Optional[int] = None,
    title_filter: Optional[str] = None,
    advanced_title_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    description_filter: Optional[str] = None,
    description_type: Optional[str] = None,
    remote: Optional[bool] = None,
    agency: Optional[bool] = None,
    offset: Optional[int] = None,
    date_filter: Optional[str] = None,
    include_ai: Optional[bool] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch jobs from RapidAPI and save them to the database with embeddings
    
    Query Parameters:
    - **limit**: Maximum number of jobs to ingest
    - **title_filter**: Filter by job title
    - **advanced_title_filter**: Advanced title filtering
    - **location_filter**: Filter by location
    - **description_filter**: Filter by description
    - **description_type**: Type of description
    - **remote**: Filter for remote jobs (true/false)
    - **agency**: Filter for agency jobs (true/false)
    - **offset**: Pagination offset
    - **date_filter**: Filter by date
    - **include_ai**: Include AI jobs (true/false)
    - **ai_work_arrangement_filter**: AI work arrangement filter
    
    Returns summary of ingestion process
    """
    if not rapidapi_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="RapidAPI is not configured. Please set RAPIDAPI_KEY in environment variables."
        )
    
    # Fetch jobs with filters
    jobs = await rapidapi_service.fetch_jobs(
        limit=limit,
        title_filter=title_filter,
        advanced_title_filter=advanced_title_filter,
        location_filter=location_filter,
        description_filter=description_filter,
        description_type=description_type,
        remote=remote,
        agency=agency,
        offset=offset,
        date_filter=date_filter,
        include_ai=include_ai,
        ai_work_arrangement_filter=ai_work_arrangement_filter,
    )
    
    if not jobs:
        return {
            "source": "rapidapi",
            "type": "jobs",
            "fetched": 0,
            "ingested": 0,
            "failed": 0,
            "message": "No jobs found from RapidAPI with given filters"
        }
    
    # Ingest jobs to database
    ingested = 0
    failed = 0
    errors = []
    
    for job_data in jobs:
        try:
            # Create JobIngest schema
            job_ingest = JobIngest(**job_data)
            
            # Create job with embedding
            await create_job(db, job_ingest)
            ingested += 1
            
        except Exception as e:
            failed += 1
            error_msg = f"Failed to ingest job '{job_data.get('title')}': {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    return {
        "source": "rapidapi",
        "type": "jobs",
        "fetched": len(jobs),
        "ingested": ingested,
        "failed": failed,
        "errors": errors[:5] if errors else None,  # Return first 5 errors
        "message": f"Successfully ingested {ingested} jobs, {failed} failed"
    }


@router.post("/ingest/internships", response_model=dict)
async def ingest_internships_from_rapidapi(
    limit: Optional[int] = None,
    title_filter: Optional[str] = None,
    advanced_title_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    description_filter: Optional[str] = None,
    description_type: Optional[str] = None,
    remote: Optional[bool] = None,
    agency: Optional[bool] = None,
    offset: Optional[int] = None,
    date_filter: Optional[str] = None,
    include_ai: Optional[bool] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch internships from RapidAPI and save them to the database with embeddings
    
    Query Parameters:
    - **limit**: Maximum number of internships to ingest
    - **title_filter**: Filter by internship title
    - **advanced_title_filter**: Advanced title filtering
    - **location_filter**: Filter by location
    - **description_filter**: Filter by description
    - **description_type**: Type of description
    - **remote**: Filter for remote internships (true/false)
    - **agency**: Filter for agency internships (true/false)
    - **offset**: Pagination offset
    - **date_filter**: Filter by date
    - **include_ai**: Include AI internships (true/false)
    - **ai_work_arrangement_filter**: AI work arrangement filter
    
    Returns summary of ingestion process
    """
    if not rapidapi_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="RapidAPI is not configured. Please set RAPIDAPI_KEY in environment variables."
        )
    
    # Fetch internships with filters
    internships = await rapidapi_service.fetch_internships(
        limit=limit,
        title_filter=title_filter,
        advanced_title_filter=advanced_title_filter,
        location_filter=location_filter,
        description_filter=description_filter,
        description_type=description_type,
        remote=remote,
        agency=agency,
        offset=offset,
        date_filter=date_filter,
        include_ai=include_ai,
        ai_work_arrangement_filter=ai_work_arrangement_filter,
    )
    
    if not internships:
        return {
            "source": "rapidapi",
            "type": "internships",
            "fetched": 0,
            "ingested": 0,
            "failed": 0,
            "message": "No internships found from RapidAPI with given filters"
        }
    
    # Ingest internships to database
    ingested = 0
    failed = 0
    errors = []
    
    for internship_data in internships:
        try:
            # Create JobIngest schema
            internship_ingest = JobIngest(**internship_data)
            
            # Create internship with embedding
            await create_job(db, internship_ingest)
            ingested += 1
            
        except Exception as e:
            failed += 1
            error_msg = f"Failed to ingest internship '{internship_data.get('title')}': {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    return {
        "source": "rapidapi",
        "type": "internships",
        "fetched": len(internships),
        "ingested": ingested,
        "failed": failed,
        "errors": errors[:5] if errors else None,
        "message": f"Successfully ingested {ingested} internships, {failed} failed"
    }


@router.post("/ingest/all", response_model=dict)
async def ingest_all_from_rapidapi(
    jobs_limit: Optional[int] = None,
    internships_limit: Optional[int] = None,
    title_filter: Optional[str] = None,
    advanced_title_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    description_filter: Optional[str] = None,
    description_type: Optional[str] = None,
    remote: Optional[bool] = None,
    agency: Optional[bool] = None,
    offset: Optional[int] = None,
    date_filter: Optional[str] = None,
    include_ai: Optional[bool] = None,
    ai_work_arrangement_filter: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch and ingest both jobs and internships from RapidAPI with optional filtering
    
    Query Parameters:
    - **jobs_limit**: Maximum number of jobs to ingest
    - **internships_limit**: Maximum number of internships to ingest
    - **title_filter**: Filter by title
    - **advanced_title_filter**: Advanced title filtering
    - **location_filter**: Filter by location
    - **description_filter**: Filter by description
    - **description_type**: Type of description
    - **remote**: Filter for remote positions (true/false)
    - **agency**: Filter for agency positions (true/false)
    - **offset**: Pagination offset
    - **date_filter**: Filter by date
    - **include_ai**: Include AI positions (true/false)
    - **ai_work_arrangement_filter**: AI work arrangement filter
    
    Returns summary of entire ingestion process
    """
    if not rapidapi_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="RapidAPI is not configured. Please set RAPIDAPI_KEY in environment variables."
        )
    
    # Fetch all data with filters
    result = await rapidapi_service.fetch_all(
        jobs_limit=jobs_limit,
        internships_limit=internships_limit,
        title_filter=title_filter,
        advanced_title_filter=advanced_title_filter,
        location_filter=location_filter,
        description_filter=description_filter,
        description_type=description_type,
        remote=remote,
        agency=agency,
        offset=offset,
        date_filter=date_filter,
        include_ai=include_ai,
        ai_work_arrangement_filter=ai_work_arrangement_filter,
    )
    
    # Ingest jobs
    jobs_ingested = 0
    jobs_failed = 0
    for job_data in result["jobs"]:
        try:
            job_ingest = JobIngest(**job_data)
            await create_job(db, job_ingest)
            jobs_ingested += 1
        except Exception as e:
            jobs_failed += 1
            logger.error(f"Failed to ingest job: {str(e)}")
    
    # Ingest internships
    internships_ingested = 0
    internships_failed = 0
    for internship_data in result["internships"]:
        try:
            internship_ingest = JobIngest(**internship_data)
            await create_job(db, internship_ingest)
            internships_ingested += 1
        except Exception as e:
            internships_failed += 1
            logger.error(f"Failed to ingest internship: {str(e)}")
    
    return {
        "source": "rapidapi",
        "jobs": {
            "fetched": len(result["jobs"]),
            "ingested": jobs_ingested,
            "failed": jobs_failed
        },
        "internships": {
            "fetched": len(result["internships"]),
            "ingested": internships_ingested,
            "failed": internships_failed
        },
        "total_ingested": jobs_ingested + internships_ingested,
        "total_failed": jobs_failed + internships_failed,
        "message": f"Ingested {jobs_ingested} jobs and {internships_ingested} internships"
    }
