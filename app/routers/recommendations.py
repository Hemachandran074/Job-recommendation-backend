"""
Job recommendation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import RecommendationQuery, RecommendationResponse, JobWithScore
from app.ml_service import ml_service
from app import crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    query: RecommendationQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Get job recommendations based on query or user profile
    
    This is the core recommendation endpoint that:
    1. Takes either a text query or user_id
    2. Generates embedding from query or retrieves user's profile embedding
    3. Performs vector similarity search in database
    4. Returns top N most similar jobs
    
    Parameters:
    - query: Text query for job search (optional if user_id provided)
    - user_id: User ID for personalized recommendations (optional if query provided)
    - limit: Number of recommendations to return (default: 10, max: 100)
    - min_score: Minimum similarity score threshold (0-1, default: 0.5)
    - job_type: Filter by job type
    - location: Filter by location
    - remote_only: Only return remote jobs
    
    Returns:
    - jobs: List of jobs with similarity scores
    - total: Number of results returned
    - query_used: The text query that was used for search
    """
    try:
        query_embedding = None
        query_text = None
        
        # Case 1: Text query provided
        if query.query:
            logger.info(f"Generating recommendations for query: {query.query}")
            query_text = query.query
            query_embedding = ml_service.generate_embedding(query.query)
        
        # Case 2: User ID provided
        elif query.user_id:
            logger.info(f"Generating recommendations for user: {query.user_id}")
            user = await crud.get_user_by_id(db, query.user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if not user.resume_embedding:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User has no profile embedding. Please update user profile first."
                )
            
            query_embedding = user.resume_embedding
            
            # Create query text for display
            query_text = ml_service.create_user_profile_text({
                'skills': user.skills,
                'experience_years': user.experience_years,
                'preferred_job_type': user.preferred_job_type,
                'preferred_locations': user.preferred_locations
            })
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'query' or 'user_id' must be provided"
            )
        
        # Perform vector similarity search
        jobs_with_scores = await crud.search_jobs_by_similarity(
            db=db,
            query_embedding=query_embedding,
            limit=query.limit,
            min_score=query.min_score,
            job_type=query.job_type,
            location=query.location,
            remote_only=query.remote_only
        )
        
        # Convert to response format
        job_responses = []
        for job, score in jobs_with_scores:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "skills": job.skills,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "job_type": job.job_type,
                "experience_level": job.experience_level,
                "remote": job.remote,
                "url": job.url,
                "source": job.source,
                "created_at": job.created_at,
                "updated_at": job.updated_at,
                "similarity_score": score
            }
            job_responses.append(JobWithScore(**job_dict))
        
        logger.info(f"Found {len(job_responses)} recommendations")
        
        return RecommendationResponse(
            jobs=job_responses,
            total=len(job_responses),
            query_used=query_text[:100] if query_text else None  # Truncate for response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/test")
async def test_recommendation_endpoint():
    """Test endpoint to verify recommendations router is working"""
    return {
        "status": "ok",
        "message": "Recommendations endpoint is working",
        "endpoints": [
            "POST /api/v1/recommendations - Get job recommendations"
        ]
    }
