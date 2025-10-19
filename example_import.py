"""
Example script to bulk import jobs from various sources
"""
import asyncio
import httpx
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Your deployed API URL
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")


async def ingest_job(client: httpx.AsyncClient, job_data: Dict) -> Dict:
    """Ingest a single job"""
    try:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/jobs/ingest",
            json=job_data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error ingesting job {job_data.get('title')}: {e}")
        return None


async def bulk_import_sample_jobs():
    """Import sample jobs for testing"""
    
    sample_jobs = [
        {
            "title": "Senior Python Developer",
            "company": "Tech Innovations Inc",
            "location": "San Francisco, CA",
            "description": "We're looking for an experienced Python developer with expertise in FastAPI, PostgreSQL, and machine learning. You'll work on building scalable backend systems and ML-powered features.",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Machine Learning", "Docker", "AWS"],
            "salary_min": 130000,
            "salary_max": 180000,
            "job_type": "full-time",
            "experience_level": "senior",
            "remote": True,
            "source": "sample_data"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Solutions Corp",
            "location": "New York, NY",
            "description": "Join our AI team to build cutting-edge machine learning models. Experience with PyTorch, TensorFlow, and production ML systems required.",
            "skills": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "MLOps", "Kubernetes"],
            "salary_min": 140000,
            "salary_max": 200000,
            "job_type": "full-time",
            "experience_level": "senior",
            "remote": False,
            "source": "sample_data"
        },
        {
            "title": "Full Stack Developer",
            "company": "StartUp Labs",
            "location": "Remote",
            "description": "Looking for a versatile full-stack developer comfortable with React, Node.js, and Python. You'll work on our customer-facing web application.",
            "skills": ["JavaScript", "React", "Node.js", "Python", "MongoDB", "REST API"],
            "salary_min": 100000,
            "salary_max": 140000,
            "job_type": "full-time",
            "experience_level": "mid",
            "remote": True,
            "source": "sample_data"
        },
        {
            "title": "Data Science Intern",
            "company": "Analytics Pro",
            "location": "Boston, MA",
            "description": "Summer internship opportunity for students interested in data science. Work with real-world datasets and learn from experienced data scientists.",
            "skills": ["Python", "Pandas", "NumPy", "SQL", "Data Visualization", "Statistics"],
            "salary_min": 25000,
            "salary_max": 35000,
            "job_type": "internship",
            "experience_level": "entry",
            "remote": False,
            "source": "sample_data"
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Systems Inc",
            "location": "Seattle, WA",
            "description": "Manage and optimize our cloud infrastructure. Experience with AWS, Kubernetes, and CI/CD pipelines essential.",
            "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "Jenkins", "Python"],
            "salary_min": 120000,
            "salary_max": 160000,
            "job_type": "full-time",
            "experience_level": "mid",
            "remote": True,
            "source": "sample_data"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        print(f"Importing {len(sample_jobs)} sample jobs...")
        
        tasks = [ingest_job(client, job) for job in sample_jobs]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r is not None)
        print(f"\n✅ Successfully imported {success_count}/{len(sample_jobs)} jobs")
        
        return results


async def test_recommendations():
    """Test the recommendations endpoint"""
    test_queries = [
        "python developer with machine learning experience",
        "full stack web developer",
        "data science internship",
        "cloud engineer with kubernetes",
    ]
    
    async with httpx.AsyncClient() as client:
        print("\n🔍 Testing recommendations...")
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            try:
                response = await client.post(
                    f"{API_BASE_URL}/api/v1/recommendations",
                    json={"query": query, "limit": 3},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                print(f"Found {data['total']} recommendations:")
                for job in data['jobs'][:3]:
                    print(f"  - {job['title']} at {job['company']} (Score: {job['similarity_score']:.2f})")
            
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main function"""
    print("=" * 60)
    print("Job Recommendation API - Sample Data Import")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}\n")
    
    # Check health
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=10.0)
            response.raise_for_status()
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"✅ Database: {health['database']}")
            print(f"✅ ML Model: {health['ml_model']}\n")
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        print("Please ensure the API is running and API_URL is correct")
        return
    
    # Import jobs
    await bulk_import_sample_jobs()
    
    # Test recommendations
    await test_recommendations()
    
    print("\n" + "=" * 60)
    print("✨ Done! Visit {}/docs to explore the API".format(API_BASE_URL))
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
