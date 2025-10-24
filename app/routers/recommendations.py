"""
Recommendations Router
Endpoints for getting personalized job recommendations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Job
from app.ml_service import ml_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{user_id}")
async def get_recommendations_for_user(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized job recommendations for a user based on their skills
    """
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.skills or len(user.skills) == 0:
            # No skills, return empty recommendations
            return {
                "user_id": user_id,
                "recommendations": [],
                "message": "No skills found. Please complete your profile."
            }
        
        # Get all jobs
        result = await db.execute(select(Job))
        all_jobs = result.scalars().all()
        
        if not all_jobs:
            return {
                "user_id": user_id,
                "recommendations": [],
                "message": "No jobs available in database"
            }
        
        # Score and rank jobs
        scored_jobs = []
        user_skills_lower = [s.lower() for s in user.skills]
        user_location = user.location.lower() if user.location else ""
        
        for job in all_jobs:
            score = 0
            match_reasons = []
            
            # Skill matching (most important)
            job_skills_lower = [s.lower() for s in (job.skills or [])]
            matching_skills = set(user_skills_lower) & set(job_skills_lower)
            
            if matching_skills:
                score += len(matching_skills) * 20
                match_reasons.append(f"Matches your skills: {', '.join(matching_skills)}")
            
            # Location matching
            if user_location and job.location:
                if user_location in job.location.lower():
                    score += 30
                    match_reasons.append(f"Location match: {job.location}")
            
            # Recent jobs bonus
            if job.posted_date:
                days_old = (datetime.utcnow() - job.posted_date).days
                if days_old <= 7:
                    score += 10
                    match_reasons.append("Recently posted")
            
            # Remote jobs bonus
            if job.remote:
                score += 5
                match_reasons.append("Remote position")
            
            if score > 0:
                scored_jobs.append({
                    "job": {
                        "id": str(job.id),
                        "title": job.title,
                        "company": job.company,
                        "location": job.location,
                        "job_type": job.job_type,
                        "remote": job.remote,
                        "description": job.description,
                        "skills": job.skills,
                        "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                    },
                    "match_score": score,
                    "match_reasons": match_reasons
                })
        
        # Sort by score and return top N
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        top_recommendations = scored_jobs[:limit]
        
        logger.info(f"✅ Generated {len(top_recommendations)} recommendations for user {user_id}")
        
        return {
            "user_id": user_id,
            "user_skills": user.skills,
            "recommendations": top_recommendations,
            "total_matches": len(scored_jobs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
