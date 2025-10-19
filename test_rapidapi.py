"""
Test script for RapidAPI integration
Run this after starting your server to test RapidAPI functionality
"""
import httpx
import asyncio
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


async def test_rapidapi_integration():
    """Test all RapidAPI endpoints"""
    
    print("🧪 Testing RapidAPI Integration\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Test 1: Check RapidAPI status
        print("\n1️⃣ Testing RapidAPI Status")
        print("-" * 60)
        try:
            response = await client.get(f"{API_BASE_URL}/api/v1/rapidapi/status")
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Configured: {result.get('configured')}")
            print(f"Message: {result.get('message')}")
            
            if not result.get('configured'):
                print("\n⚠️  RapidAPI is not configured!")
                print("Please set RAPIDAPI_KEY in your .env file")
                return
            
            print("✅ RapidAPI is configured and ready!")
            
        except Exception as e:
            print(f"❌ Error checking status: {str(e)}")
            return
        
        # Test 2: Fetch jobs (without saving)
        print("\n2️⃣ Testing Fetch Jobs (Preview)")
        print("-" * 60)
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/rapidapi/fetch/jobs?limit=5"
            )
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Jobs fetched: {result.get('count')}")
            
            if result.get('count') > 0:
                print("\n📋 Sample Job:")
                sample_job = result['jobs'][0]
                print(f"  Title: {sample_job.get('title')}")
                print(f"  Company: {sample_job.get('company')}")
                print(f"  Location: {sample_job.get('location')}")
                print(f"  Type: {sample_job.get('job_type')}")
                print(f"  Remote: {sample_job.get('remote')}")
                print("✅ Jobs fetched successfully!")
            else:
                print("⚠️  No jobs found")
                
        except Exception as e:
            print(f"❌ Error fetching jobs: {str(e)}")
        
        # Test 3: Fetch internships (without saving)
        print("\n3️⃣ Testing Fetch Internships (Preview)")
        print("-" * 60)
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/rapidapi/fetch/internships?limit=5"
            )
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Internships fetched: {result.get('count')}")
            
            if result.get('count') > 0:
                print("\n📋 Sample Internship:")
                sample_internship = result['internships'][0]
                print(f"  Title: {sample_internship.get('title')}")
                print(f"  Company: {sample_internship.get('company')}")
                print(f"  Location: {sample_internship.get('location')}")
                print(f"  Type: {sample_internship.get('job_type')}")
                print("✅ Internships fetched successfully!")
            else:
                print("⚠️  No internships found")
                
        except Exception as e:
            print(f"❌ Error fetching internships: {str(e)}")
        
        # Test 4: Ingest jobs (save to database)
        print("\n4️⃣ Testing Ingest Jobs (Save to Database)")
        print("-" * 60)
        print("⏳ This may take a minute...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/rapidapi/ingest/jobs?limit=10"
            )
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Jobs fetched: {result.get('fetched')}")
            print(f"Jobs ingested: {result.get('ingested')}")
            print(f"Jobs failed: {result.get('failed')}")
            print(f"Message: {result.get('message')}")
            
            if result.get('ingested', 0) > 0:
                print("✅ Jobs successfully ingested to database!")
            else:
                print("⚠️  No jobs were ingested")
                
        except Exception as e:
            print(f"❌ Error ingesting jobs: {str(e)}")
        
        # Test 5: Ingest internships (save to database)
        print("\n5️⃣ Testing Ingest Internships (Save to Database)")
        print("-" * 60)
        print("⏳ This may take a minute...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/rapidapi/ingest/internships?limit=10"
            )
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Internships fetched: {result.get('fetched')}")
            print(f"Internships ingested: {result.get('ingested')}")
            print(f"Internships failed: {result.get('failed')}")
            print(f"Message: {result.get('message')}")
            
            if result.get('ingested', 0) > 0:
                print("✅ Internships successfully ingested to database!")
            else:
                print("⚠️  No internships were ingested")
                
        except Exception as e:
            print(f"❌ Error ingesting internships: {str(e)}")
        
        # Test 6: Verify data in database
        print("\n6️⃣ Testing Database Verification")
        print("-" * 60)
        try:
            # Get total jobs count
            response = await client.get(f"{API_BASE_URL}/api/v1/jobs/count/total")
            total = response.json()
            print(f"Total jobs in database: {total.get('total_jobs')}")
            
            # Get some jobs
            response = await client.get(f"{API_BASE_URL}/api/v1/jobs?limit=3")
            jobs = response.json()
            print(f"Sample jobs retrieved: {len(jobs)}")
            
            if jobs:
                print("\n📋 Sample from database:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job.get('title')}")
                    print(f"    Company: {job.get('company')}")
                    print(f"    Type: {job.get('job_type')}")
                    print(f"    Source: {job.get('source')}")
                print("\n✅ Database verification successful!")
            else:
                print("⚠️  No jobs found in database")
                
        except Exception as e:
            print(f"❌ Error verifying database: {str(e)}")
        
        # Test 7: Test recommendations with ingested data
        print("\n7️⃣ Testing ML Recommendations")
        print("-" * 60)
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/recommendations",
                json={
                    "query": "python developer machine learning",
                    "limit": 5
                }
            )
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Recommendations found: {len(result.get('recommendations', []))}")
            
            if result.get('recommendations'):
                print("\n🎯 Top Recommendations:")
                for i, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"\n  {i}. {rec.get('title')} at {rec.get('company')}")
                    print(f"     Similarity: {rec.get('similarity_score', 0):.2%}")
                    print(f"     Type: {rec.get('job_type')}")
                print("\n✅ Recommendations working perfectly!")
            else:
                print("⚠️  No recommendations found")
                print("Try ingesting more jobs first")
                
        except Exception as e:
            print(f"❌ Error testing recommendations: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 RapidAPI Integration Test Complete!")
    print("=" * 60)
    print("\n📚 Next Steps:")
    print("1. Ingest more data: POST /api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100")
    print("2. Set up scheduled ingestion (cron job)")
    print("3. Connect your mobile app to /api/v1/recommendations")
    print("4. Check RAPIDAPI_INTEGRATION.md for detailed guide")
    print("\n✨ Your ML-powered job recommendation system is ready!")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║         RapidAPI Integration Test Script                 ║
║                                                           ║
║  Make sure your server is running:                       ║
║  uvicorn app.main:app --reload                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(test_rapidapi_integration())
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
