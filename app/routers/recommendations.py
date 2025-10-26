"""
Recommendations Router
Endpoints for getting personalized job recommendations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Job
from app.ml_service import ml_service
from app.schemas import RecommendationQuery

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("")
async def get_recommendations(
    query: RecommendationQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized job recommendations based on user profile
    
    Matches jobs based on:
    1. User's skills (Python, ML, etc.)
    2. Preferred job titles (Software Engineer, etc.)
    3. Preferred locations (Bangalore, Chennai, etc.)
    4. Experience level
    5. Job recency
    """
    try:
        # Require user_id
        if not query.user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        user_id = str(query.user_id)
        
        # Get user profile
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"🔍 Getting recommendations for: {user.email}")
        
        # Extract user preferences
        user_skills = [s.lower().strip() for s in (user.skills or [])]
        user_job_titles = [t.lower().strip() for t in (user.preferred_job_titles or [])]
        user_locations = [loc.lower().strip() for loc in (user.preferred_locations or [])]
        user_experience_level = (user.experience_level or "").lower()
        
        logger.info(f"   Skills: {user_skills}")
        logger.info(f"   Job Titles: {user_job_titles}")
        logger.info(f"   Locations: {user_locations}")
        logger.info(f"   Experience: {user_experience_level}")
        
        # Check if user has completed profile
        if not user_skills and not user_job_titles and not user_locations:
            return {
                "user_id": user_id,
                "user_profile": {
                    "skills": [],
                    "job_titles": [],
                    "locations": []
                },
                "recommendations": [],
                "total_matches": 0,
                "message": "Please complete your profile with skills, job titles, and preferred locations."
            }
        
        # Get recent jobs (last 60 days)
        cutoff_date = datetime.utcnow() - timedelta(days=60)
        result = await db.execute(
            select(Job)
            .where(Job.created_at >= cutoff_date)
            .order_by(Job.created_at.desc())
            .limit(500)  # Get top 500 recent jobs
        )
        all_jobs = result.scalars().all()
        
        logger.info(f"📊 Analyzing {len(all_jobs)} recent jobs...")
        
        if not all_jobs:
            return {
                "user_id": user_id,
                "user_profile": {
                    "skills": user_skills,
                    "job_titles": user_job_titles,
                    "locations": user_locations
                },
                "recommendations": [],
                "total_matches": 0,
                "message": "No jobs available. Database needs to be populated."
            }
        
        # Score each job based on user preferences
        recommendations = []
        
        for job in all_jobs:
            score = 0
            match_reasons = []
            
            # 1. SKILL MATCHING (Highest Priority - 25 points per skill)
            job_skills_lower = [s.lower().strip() for s in (job.skills or [])]
            job_title_lower = job.title.lower()
            job_description_lower = job.description.lower() if job.description else ""
            
            # Check skills in job skills list
            matching_skills = set(user_skills) & set(job_skills_lower)
            
            # Also check if user skills appear in job title or description
            skills_in_title = [skill for skill in user_skills if skill in job_title_lower]
            skills_in_description = [skill for skill in user_skills if skill in job_description_lower and skill not in matching_skills]
            
            if matching_skills:
                skill_score = len(matching_skills) * 25
                score += skill_score
                match_reasons.append(
                    f"✓ Matches {len(matching_skills)} skills: {', '.join(list(matching_skills)[:3])}"
                )
            
            if skills_in_title:
                score += len(skills_in_title) * 15
                match_reasons.append(
                    f"✓ Skills in job title: {', '.join(skills_in_title[:2])}"
                )
            
            if skills_in_description and len(match_reasons) < 2:
                score += len(skills_in_description) * 5
                match_reasons.append(
                    f"✓ Skills in description: {', '.join(skills_in_description[:2])}"
                )
            
            # 2. JOB TITLE MATCHING (30 points per title match)
            if user_job_titles:
                for user_title in user_job_titles:
                    if user_title in job_title_lower:
                        score += 30
                        match_reasons.append(f"✓ Job title match: {user_title.title()}")
                        break  # Only count once
            
            # 3. LOCATION MATCHING (20 points per location)
            job_location_lower = job.location.lower() if job.location else ""
            
            if user_locations:
                for user_loc in user_locations:
                    if user_loc in job_location_lower:
                        score += 20
                        match_reasons.append(f"✓ Location: {user_loc.title()}")
                        break  # Only count once
            
            # 4. EXPERIENCE LEVEL MATCHING (15 points)
            if user_experience_level and job.experience_level:
                job_exp_lower = job.experience_level.lower()
                if user_experience_level in job_exp_lower or job_exp_lower in user_experience_level:
                    score += 15
                    match_reasons.append(f"✓ Experience level: {job.experience_level}")
            
            # 5. RECENCY BONUS (10 points for <7 days, 5 for <14 days)
            if job.created_at:
                days_old = (datetime.utcnow() - job.created_at).days
                if days_old <= 7:
                    score += 10
                    match_reasons.append(f"✓ Posted {days_old} day{'s' if days_old != 1 else ''} ago")
                elif days_old <= 14:
                    score += 5
            
            # 6. REMOTE WORK BONUS (8 points)
            if job.remote:
                score += 8
                match_reasons.append("✓ Remote work available")
            
            # Only include jobs with meaningful matches (score > 10)
            if score >= 10:
                recommendations.append({
                    "job": {
                        "id": str(job.id),
                        "_id": str(job.id),
                        "title": job.title,
                        "company": job.company,
                        "company_name": job.company,
                        "location": job.location or "Remote",
                        "type": job.job_type or "Full Time",
                        "job_type": job.job_type or "Full Time",
                        "remote": job.remote or False,
                        "description": (job.description[:250] + "...") if job.description and len(job.description) > 250 else (job.description or "No description available"),
                        "skills": job.skills or [],
                        "experience_level": job.experience_level or "",
                        "salary": f"${job.salary_min}K-${job.salary_max}K" if job.salary_min and job.salary_max else "Competitive salary",
                        "url": job.url or "",
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                        "period": f"{(datetime.utcnow() - job.created_at).days} days ago" if job.created_at else "Recently posted"
                    },
                    "match_score": score,
                    "match_percentage": min(int((score / 150) * 100), 100),  # Max 150 points = 100%
                    "match_reasons": match_reasons[:4]  # Top 4 reasons
                })
        
        # Sort by match score (highest first)
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Limit to requested number
        recommendations = recommendations[:query.limit]
        
        logger.info(f"✅ Returning {len(recommendations)} personalized recommendations")
        if recommendations:
            logger.info(f"   Top match score: {recommendations[0]['match_score']}")
        
        return {
            "user_id": user_id,
            "user_profile": {
                "skills": user_skills,
                "job_titles": user_job_titles,
                "locations": user_locations,
                "experience_level": user_experience_level
            },
            "recommendations": recommendations,
            "total_matches": len(recommendations),
            "message": f"Found {len(recommendations)} jobs matching your profile" if recommendations else "No matching jobs found. Try updating your preferences."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Recommendation error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {str(e)}"
        )
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
            top_recommendations = scored_jobs[:query.limit]
            
            logger.info(f"✅ Generated {len(top_recommendations)} recommendations for user {user_id}")
            
            return {
                "user_id": user_id,
                "user_skills": user.skills,
                "recommendations": top_recommendations,
                "total_matches": len(scored_jobs)
            }
        
        # If query text provided, search for matching jobs
        elif query.query:
            # TODO: Implement text-based search using ML embeddings
            logger.warning("Text-based search not yet implemented")
            return {
                "query": query.query,
                "recommendations": [],
                "message": "Text-based search coming soon"
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Either user_id or query must be provided"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


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
