# 🔌 RapidAPI Integration Guide

## Overview

This guide explains how to integrate and use the RapidAPI endpoints for fetching jobs and internships in your job recommendation system.

## 📋 Prerequisites

1. **RapidAPI Account**: Sign up at [rapidapi.com](https://rapidapi.com)
2. **API Key**: Get your API key from RapidAPI dashboard
3. **Endpoints**: You have two endpoints:
   - **Jobs**: `https://internships-api.p.rapidapi.com/active-jb-7d`
   - **Internships**: `https://internships-api.p.rapidapi.com/active-jb-7d`

## 🔧 Configuration

### 1. Set Environment Variables

Update your `.env` file:

```env
# RapidAPI Configuration
RAPIDAPI_KEY=e31355fde5msh6edf6c1b3a0d89ep1ea7d4jsn49e451401c14
RAPIDAPI_HOST=internships-api.p.rapidapi.com
RAPIDAPI_JOBS_URL=https://internships-api.p.rapidapi.com/active-jb-7d
RAPIDAPI_INTERNSHIPS_URL=https://internships-api.p.rapidapi.com/active-jb-7d
```

### 2. Verify Configuration

Check if RapidAPI is properly configured:

```bash
curl http://localhost:8000/api/v1/rapidapi/status
```

**Expected Response:**
```json
{
  "configured": true,
  "jobs_url": "https://internships-api.p.rapidapi.com/active-jb-7d",
  "internships_url": "https://internships-api.p.rapidapi.com/active-jb-7d",
  "message": "RapidAPI is configured and ready"
}
```

## 🎯 API Endpoints

### 1. Check RapidAPI Status

```http
GET /api/v1/rapidapi/status
```

Checks if RapidAPI is configured and ready to use.

---

### 2. Fetch Jobs (Without Saving)

```http
POST /api/v1/rapidapi/fetch/jobs?limit=10
```

**Query Parameters:**
- `limit` (optional): Maximum number of jobs to fetch

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/fetch/jobs?limit=10"
```

**Response:**
```json
{
  "source": "rapidapi",
  "type": "jobs",
  "count": 10,
  "jobs": [
    {
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "Remote",
      "description": "...",
      "skills": ["Python", "FastAPI", "ML"],
      "job_type": "full-time",
      "remote": true,
      "url": "https://..."
    }
  ]
}
```

---

### 3. Fetch Internships (Without Saving)

```http
POST /api/v1/rapidapi/fetch/internships?limit=10
```

**Query Parameters:**
- `limit` (optional): Maximum number of internships to fetch

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/fetch/internships?limit=10"
```

**Response:**
```json
{
  "source": "rapidapi",
  "type": "internships",
  "count": 10,
  "internships": [
    {
      "title": "ML Engineering Intern",
      "company": "AI Startup",
      "location": "San Francisco",
      "description": "...",
      "skills": ["Python", "TensorFlow"],
      "job_type": "internship",
      "remote": false,
      "url": "https://..."
    }
  ]
}
```

---

### 4. Fetch Both Jobs and Internships

```http
POST /api/v1/rapidapi/fetch/all?jobs_limit=20&internships_limit=20
```

**Query Parameters:**
- `jobs_limit` (optional): Maximum number of jobs
- `internships_limit` (optional): Maximum number of internships

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/fetch/all?jobs_limit=20&internships_limit=20"
```

**Response:**
```json
{
  "source": "rapidapi",
  "jobs_count": 20,
  "internships_count": 20,
  "total_count": 40,
  "jobs": [...],
  "internships": [...]
}
```

---

### 5. Ingest Jobs (Fetch + Save to Database)

```http
POST /api/v1/rapidapi/ingest/jobs?limit=50
```

**What it does:**
1. Fetches jobs from RapidAPI
2. Generates ML embeddings for each job
3. Saves to PostgreSQL database
4. Returns summary of ingestion

**Query Parameters:**
- `limit` (optional): Maximum number of jobs to ingest

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/jobs?limit=50"
```

**Response:**
```json
{
  "source": "rapidapi",
  "type": "jobs",
  "fetched": 50,
  "ingested": 48,
  "failed": 2,
  "errors": ["Failed to ingest job 'Invalid Title': ..."],
  "message": "Successfully ingested 48 jobs, 2 failed"
}
```

---

### 6. Ingest Internships (Fetch + Save to Database)

```http
POST /api/v1/rapidapi/ingest/internships?limit=50
```

**What it does:**
1. Fetches internships from RapidAPI
2. Generates ML embeddings for each internship
3. Saves to PostgreSQL database
4. Returns summary of ingestion

**Query Parameters:**
- `limit` (optional): Maximum number of internships to ingest

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/internships?limit=50"
```

**Response:**
```json
{
  "source": "rapidapi",
  "type": "internships",
  "fetched": 50,
  "ingested": 47,
  "failed": 3,
  "message": "Successfully ingested 47 internships, 3 failed"
}
```

---

### 7. Ingest Everything (Jobs + Internships)

```http
POST /api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100
```

**What it does:**
1. Fetches both jobs and internships
2. Generates embeddings for all
3. Saves everything to database
4. Returns comprehensive summary

**Query Parameters:**
- `jobs_limit` (optional): Maximum jobs to ingest
- `internships_limit` (optional): Maximum internships to ingest

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"
```

**Response:**
```json
{
  "source": "rapidapi",
  "jobs": {
    "fetched": 100,
    "ingested": 95,
    "failed": 5
  },
  "internships": {
    "fetched": 100,
    "ingested": 98,
    "failed": 2
  },
  "total_ingested": 193,
  "total_failed": 7,
  "message": "Ingested 95 jobs and 98 internships"
}
```

## 🔄 Workflow Examples

### Scenario 1: Initial Database Population

**Goal**: Populate your database with jobs and internships for the first time.

```bash
# Step 1: Check configuration
curl http://localhost:8000/api/v1/rapidapi/status

# Step 2: Ingest everything (recommended for first run)
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"

# Step 3: Verify jobs were added
curl http://localhost:8000/api/v1/jobs/count/total
```

---

### Scenario 2: Daily/Hourly Updates

**Goal**: Keep your database fresh with new jobs/internships.

```bash
# Fetch only new jobs (run as cron job)
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/jobs?limit=50"

# Fetch only new internships
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/internships?limit=50"
```

**Cron Job Example** (Linux/Mac):
```cron
# Run every 6 hours
0 */6 * * * curl -X POST "https://your-api.railway.app/api/v1/rapidapi/ingest/all?jobs_limit=50&internships_limit=50"
```

**Windows Task Scheduler** (PowerShell):
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "curl" -Argument "-X POST https://your-api.railway.app/api/v1/rapidapi/ingest/all?jobs_limit=50&internships_limit=50"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "IngestJobs"
```

---

### Scenario 3: Preview Before Ingesting

**Goal**: See what data looks like before saving to database.

```bash
# Step 1: Fetch and preview jobs (doesn't save)
curl -X POST "http://localhost:8000/api/v1/rapidapi/fetch/jobs?limit=5"

# Step 2: If data looks good, ingest to database
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/jobs?limit=100"
```

---

### Scenario 4: Testing Recommendations

**Goal**: Test ML recommendations after ingesting data.

```bash
# Step 1: Ingest jobs
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/jobs?limit=50"

# Step 2: Get recommendations for Python developer
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer machine learning", "limit": 10}'

# Step 3: Filter for internships only
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"query": "software engineering intern", "limit": 10, "job_type": "internship"}'
```

## 🎨 Mobile App Integration

### React Native Example

```javascript
// services/api.js
const API_BASE_URL = 'https://your-api.railway.app';

// Ingest jobs from RapidAPI
export const ingestJobs = async (limit = 50) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/rapidapi/ingest/jobs?limit=${limit}`,
      { method: 'POST' }
    );
    return await response.json();
  } catch (error) {
    console.error('Error ingesting jobs:', error);
    throw error;
  }
};

// Ingest internships from RapidAPI
export const ingestInternships = async (limit = 50) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/rapidapi/ingest/internships?limit=${limit}`,
      { method: 'POST' }
    );
    return await response.json();
  } catch (error) {
    console.error('Error ingesting internships:', error);
    throw error;
  }
};

// Get recommendations (works with ingested data)
export const getRecommendations = async (query, jobType = null) => {
  try {
    const body = { query, limit: 20 };
    if (jobType) body.job_type = jobType;
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/recommendations`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }
    );
    return await response.json();
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};
```

### Usage in Component

```javascript
import { ingestJobs, ingestInternships, getRecommendations } from './services/api';

// In your component
const JobScreen = () => {
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState([]);

  // Initial data load (run once when app opens)
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      // Ingest jobs and internships from RapidAPI
      await Promise.all([
        ingestJobs(100),
        ingestInternships(100)
      ]);
      console.log('✅ Data ingested successfully');
    } catch (error) {
      console.error('❌ Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchJobs = async (query) => {
    setLoading(true);
    try {
      // Get ML-powered recommendations
      const result = await getRecommendations(query, 'full-time');
      setJobs(result.recommendations);
    } catch (error) {
      console.error('Error searching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      <TextInput 
        placeholder="Search jobs..." 
        onChangeText={(text) => searchJobs(text)}
      />
      {loading ? <ActivityIndicator /> : (
        <FlatList
          data={jobs}
          renderItem={({ item }) => (
            <JobCard 
              title={item.title}
              company={item.company}
              similarity={item.similarity_score}
            />
          )}
        />
      )}
    </View>
  );
};
```

## 🔒 Security Best Practices

### 1. Protect Your API Key

**❌ DON'T** expose your RapidAPI key in:
- Mobile app code
- Frontend code
- Public repositories
- Client-side requests

**✅ DO** keep it in:
- Backend environment variables only
- Server-side configuration
- Secret management services

### 2. Rate Limiting

RapidAPI has rate limits. To avoid hitting them:

```python
# Recommended ingestion schedule
# - Initial load: 500-1000 jobs/internships
# - Daily updates: 50-100 each
# - Real-time: Use cached data from database
```

### 3. Error Handling

```javascript
const ingestWithRetry = async (type, limit, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const url = `${API_BASE_URL}/api/v1/rapidapi/ingest/${type}?limit=${limit}`;
      const response = await fetch(url, { method: 'POST' });
      
      if (response.ok) {
        return await response.json();
      }
      
      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));
    } catch (error) {
      if (i === retries - 1) throw error;
    }
  }
};
```

## 📊 Monitoring & Analytics

### Track Ingestion Success

```bash
# Check total jobs in database
curl http://localhost:8000/api/v1/jobs/count/total

# View recent jobs
curl http://localhost:8000/api/v1/jobs?limit=10

# Check RapidAPI status
curl http://localhost:8000/api/v1/rapidapi/status
```

### Logging

The backend automatically logs:
- ✅ Successful ingestions
- ❌ Failed ingestions with reasons
- 📊 Counts and summaries
- ⚠️ API errors

Check logs:
```bash
# Railway
railway logs

# Render
# View in dashboard

# Local
# Check console output
```

## 🐛 Troubleshooting

### Issue: "RapidAPI is not configured"

**Solution:**
```bash
# Check environment variables
railway variables

# Set RAPIDAPI_KEY
railway variables set RAPIDAPI_KEY="your-key-here"
```

---

### Issue: "No jobs found from RapidAPI"

**Possible causes:**
1. API key is invalid or expired
2. RapidAPI endpoint is down
3. Rate limit exceeded

**Solution:**
```bash
# Test API key manually
curl -X GET "https://internships-api.p.rapidapi.com/active-jb-7d" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: internships-api.p.rapidapi.com"

# Check your RapidAPI dashboard for quota/limits
```

---

### Issue: Ingestion fails for some jobs

**This is normal!** Some jobs may have:
- Missing required fields
- Invalid data formats
- Encoding issues

**The API handles this gracefully:**
- Continues processing other jobs
- Returns summary with failed count
- Logs errors for debugging

---

### Issue: Slow ingestion

**Optimization tips:**
1. Use smaller batch sizes (limit=50 instead of 500)
2. Run during off-peak hours
3. Enable background processing
4. Use pagination for large datasets

## 🎯 Best Practices

### 1. Initial Setup
```bash
# Day 1: Seed database with good data
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=200&internships_limit=200"
```

### 2. Regular Updates
```bash
# Daily: Keep data fresh
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=50&internships_limit=50"
```

### 3. Use Recommendations API
```bash
# Don't call RapidAPI from mobile app
# Instead, call recommendations API (uses cached data)
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer", "limit": 20}'
```

## 📈 Performance Tips

1. **Batch Ingestion**: Ingest in batches of 50-100 for optimal performance
2. **Cache Results**: Recommendations use database (fast), not RapidAPI (slow)
3. **Background Jobs**: Run ingestion as background task during off-peak hours
4. **Database Indexes**: Already configured for fast vector search
5. **Async Operations**: All endpoints use async for high throughput

## ✅ Success Checklist

- [ ] RapidAPI key configured in `.env`
- [ ] Status endpoint returns "configured": true
- [ ] Can fetch jobs successfully
- [ ] Can fetch internships successfully
- [ ] Jobs are being saved to database
- [ ] Recommendations work with ingested data
- [ ] Mobile app can call recommendations API
- [ ] Scheduled task for daily updates (optional)
- [ ] Monitoring/logging in place

## 🎉 You're Ready!

Your backend now supports:
- ✅ Fetching jobs from RapidAPI
- ✅ Fetching internships from RapidAPI
- ✅ Automatic ML embedding generation
- ✅ Database storage with pgvector
- ✅ ML-powered recommendations
- ✅ Separate job/internship handling

**Start ingesting:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"
```

Then use recommendations in your mobile app! 🚀
