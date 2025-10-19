"""
RapidAPI Integration Service
Fetches jobs and internships from RapidAPI endpoints
"""
import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class RapidAPIService:
    """Service for fetching jobs and internships from RapidAPI"""
    
    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.api_host = settings.RAPIDAPI_HOST
        self.jobs_url = settings.RAPIDAPI_JOBS_URL
        self.internships_url = settings.RAPIDAPI_INTERNSHIPS_URL
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }
    
    def is_configured(self) -> bool:
        """Check if RapidAPI is properly configured"""
        return self.api_key is not None and self.api_key != ""
    
    async def fetch_jobs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch jobs from RapidAPI
        
        Args:
            limit: Maximum number of jobs to fetch (optional)
            
        Returns:
            List of job dictionaries
        """
        if not self.is_configured():
            logger.warning("RapidAPI is not configured. Skipping job fetch.")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching jobs from RapidAPI: {self.jobs_url}")
                response = await client.get(
                    self.jobs_url,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract jobs from response
                jobs = self._parse_rapidapi_response(data, job_type="full-time")
                
                if limit:
                    jobs = jobs[:limit]
                
                logger.info(f"Successfully fetched {len(jobs)} jobs from RapidAPI")
                return jobs
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching jobs from RapidAPI: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching jobs from RapidAPI: {str(e)}")
            return []
    
    async def fetch_internships(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch internships from RapidAPI
        
        Args:
            limit: Maximum number of internships to fetch (optional)
            
        Returns:
            List of internship dictionaries
        """
        if not self.is_configured():
            logger.warning("RapidAPI is not configured. Skipping internship fetch.")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching internships from RapidAPI: {self.internships_url}")
                response = await client.get(
                    self.internships_url,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract internships from response
                internships = self._parse_rapidapi_response(data, job_type="internship")
                
                if limit:
                    internships = internships[:limit]
                
                logger.info(f"Successfully fetched {len(internships)} internships from RapidAPI")
                return internships
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching internships from RapidAPI: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching internships from RapidAPI: {str(e)}")
            return []
    
    async def fetch_all(self, jobs_limit: Optional[int] = None, 
                       internships_limit: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch both jobs and internships
        
        Args:
            jobs_limit: Maximum number of jobs to fetch
            internships_limit: Maximum number of internships to fetch
            
        Returns:
            Dictionary with 'jobs' and 'internships' keys
        """
        jobs = await self.fetch_jobs(limit=jobs_limit)
        internships = await self.fetch_internships(limit=internships_limit)
        
        return {
            "jobs": jobs,
            "internships": internships,
            "total": len(jobs) + len(internships)
        }
    
    def _parse_rapidapi_response(self, data: Any, job_type: str = "full-time") -> List[Dict[str, Any]]:
        """
        Parse RapidAPI response and convert to our job schema
        
        Args:
            data: Raw response from RapidAPI
            job_type: Type of job (full-time, internship, etc.)
            
        Returns:
            List of normalized job dictionaries
        """
        jobs = []
        
        # Handle different response formats
        if isinstance(data, list):
            raw_jobs = data
        elif isinstance(data, dict):
            # Try common response keys
            raw_jobs = (
                data.get("jobs") or 
                data.get("data") or 
                data.get("results") or 
                data.get("items") or
                []
            )
        else:
            logger.warning(f"Unexpected RapidAPI response format: {type(data)}")
            return []
        
        for raw_job in raw_jobs:
            try:
                # Normalize job data to match our schema
                normalized_job = {
                    "title": raw_job.get("title") or raw_job.get("job_title") or raw_job.get("position"),
                    "company": raw_job.get("company") or raw_job.get("company_name") or raw_job.get("employer"),
                    "location": raw_job.get("location") or raw_job.get("city") or "Remote",
                    "description": raw_job.get("description") or raw_job.get("job_description") or "",
                    "skills": self._extract_skills(raw_job),
                    "salary_min": raw_job.get("salary_min") or raw_job.get("min_salary"),
                    "salary_max": raw_job.get("salary_max") or raw_job.get("max_salary"),
                    "job_type": job_type,
                    "experience_level": raw_job.get("experience_level") or raw_job.get("experience") or "entry",
                    "remote": self._is_remote(raw_job),
                    "url": raw_job.get("url") or raw_job.get("job_url") or raw_job.get("apply_link"),
                    "source": "rapidapi"
                }
                
                # Only add if we have minimum required fields
                if normalized_job["title"] and normalized_job["company"]:
                    jobs.append(normalized_job)
                else:
                    logger.debug(f"Skipping job with missing required fields: {raw_job}")
                    
            except Exception as e:
                logger.warning(f"Error parsing job from RapidAPI: {str(e)}")
                continue
        
        return jobs
    
    def _extract_skills(self, raw_job: Dict[str, Any]) -> List[str]:
        """Extract skills from job data"""
        skills = []
        
        # Try different field names
        if "skills" in raw_job:
            skills_data = raw_job["skills"]
            if isinstance(skills_data, list):
                skills = skills_data
            elif isinstance(skills_data, str):
                skills = [s.strip() for s in skills_data.split(",")]
        elif "required_skills" in raw_job:
            skills_data = raw_job["required_skills"]
            if isinstance(skills_data, list):
                skills = skills_data
            elif isinstance(skills_data, str):
                skills = [s.strip() for s in skills_data.split(",")]
        elif "technologies" in raw_job:
            skills = raw_job["technologies"]
        
        return skills[:10]  # Limit to 10 skills
    
    def _is_remote(self, raw_job: Dict[str, Any]) -> bool:
        """Determine if job is remote"""
        location = str(raw_job.get("location", "")).lower()
        remote_field = raw_job.get("remote", False)
        work_type = str(raw_job.get("work_type", "")).lower()
        
        return (
            remote_field or
            "remote" in location or
            "work from home" in location or
            "wfh" in location or
            "remote" in work_type
        )


# Global instance
rapidapi_service = RapidAPIService()
