# 🎉 RapidAPI Integration - What's New

## Overview

Your job recommendation backend now supports **automatic job and internship ingestion** from RapidAPI! This means you can populate your database with real, live job data from two separate endpoints.

## 🆕 What Was Added

### 1. New Files Created

#### `app/rapidapi_service.py`
- **RapidAPIService class** that handles all API calls
- Fetches jobs from: `https://internships-api.p.rapidapi.com/active-jb-7d`
- Fetches internships from: `https://internships-api.p.rapidapi.com/active-jb-7d`
- Automatically parses and normalizes data
- Extracts skills, determines remote status
- Handles errors gracefully

#### `app/routers/rapidapi.py`
- **7 new API endpoints** for RapidAPI integration
- Preview data before saving (fetch endpoints)
- Ingest data directly to database (ingest endpoints)
- Batch operations for both jobs and internships
- Comprehensive error handling and reporting

#### `RAPIDAPI_INTEGRATION.md`
- **Complete integration guide** with examples
- All endpoint documentation
- Mobile app integration code
- Troubleshooting section
- Best practices and workflows

#### `test_rapidapi.py`
- **Automated test script** for RapidAPI integration
- Tests all endpoints
- Verifies data ingestion
- Checks ML recommendations
- Beautiful console output

### 2. Updated Files

#### `.env.example`
Added new environment variables:
```env
RAPIDAPI_KEY=your-key-here
RAPIDAPI_HOST=internships-api.p.rapidapi.com
RAPIDAPI_JOBS_URL=https://internships-api.p.rapidapi.com/active-jb-7d
RAPIDAPI_INTERNSHIPS_URL=https://internships-api.p.rapidapi.com/active-jb-7d
```

#### `app/config.py`
Added RapidAPI configuration:
```python
RAPIDAPI_KEY: Optional[str] = None
RAPIDAPI_HOST: str = "internships-api.p.rapidapi.com"
RAPIDAPI_JOBS_URL: str = "https://internships-api.p.rapidapi.com/active-jb-7d"
RAPIDAPI_INTERNSHIPS_URL: str = "https://internships-api.p.rapidapi.com/active-jb-7d"
```

#### `app/main.py`
Added RapidAPI router:
```python
from app.routers import jobs, recommendations, users, rapidapi
app.include_router(rapidapi.router, prefix="/api/v1/rapidapi", tags=["rapidapi"])
```

#### `README.md`
Added RapidAPI endpoints section with link to integration guide

## 🎯 New API Endpoints

### 1. Status Check
```bash
GET /api/v1/rapidapi/status
```
**Purpose**: Check if RapidAPI is configured
**Returns**: Configuration status and URLs

---

### 2. Fetch Jobs (Preview)
```bash
POST /api/v1/rapidapi/fetch/jobs?limit=10
```
**Purpose**: Preview jobs from RapidAPI WITHOUT saving
**Use case**: See what data looks like before ingesting
**Returns**: List of job objects

---

### 3. Fetch Internships (Preview)
```bash
POST /api/v1/rapidapi/fetch/internships?limit=10
```
**Purpose**: Preview internships WITHOUT saving
**Use case**: Test data before ingestion
**Returns**: List of internship objects

---

### 4. Fetch All (Preview)
```bash
POST /api/v1/rapidapi/fetch/all?jobs_limit=20&internships_limit=20
```
**Purpose**: Preview both jobs and internships
**Returns**: Combined results with counts

---

### 5. Ingest Jobs (Save to Database)
```bash
POST /api/v1/rapidapi/ingest/jobs?limit=50
```
**Purpose**: Fetch jobs AND save to database with ML embeddings
**Process**:
1. Fetches jobs from RapidAPI
2. Generates ML embeddings for each job
3. Saves to PostgreSQL with pgvector
4. Returns success/failure summary

**Returns**:
```json
{
  "source": "rapidapi",
  "type": "jobs",
  "fetched": 50,
  "ingested": 48,
  "failed": 2,
  "message": "Successfully ingested 48 jobs, 2 failed"
}
```

---

### 6. Ingest Internships (Save to Database)
```bash
POST /api/v1/rapidapi/ingest/internships?limit=50
```
**Purpose**: Fetch internships AND save to database
**Process**: Same as jobs ingestion

---

### 7. Ingest All (Save Everything)
```bash
POST /api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100
```
**Purpose**: Fetch and ingest BOTH jobs and internships
**Returns**: Comprehensive summary with counts for both

## 🚀 How to Use

### Step 1: Configure RapidAPI

1. Add your API key to `.env`:
```env
RAPIDAPI_KEY=e31355fde5msh6edf6c1b3a0d89ep1ea7d4jsn49e451401c14
```

2. Deploy or restart your server:
```bash
uvicorn app.main:app --reload
```

3. Verify configuration:
```bash
curl http://localhost:8000/api/v1/rapidapi/status
```

### Step 2: Preview Data (Optional)

Before ingesting, preview the data:
```bash
# See what jobs look like
curl -X POST "http://localhost:8000/api/v1/rapidapi/fetch/jobs?limit=5"

# See what internships look like
curl -X POST "http://localhost:8000/api/v1/rapidapi/fetch/internships?limit=5"
```

### Step 3: Ingest Data

Populate your database:
```bash
# Ingest everything at once (recommended for first time)
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"
```

### Step 4: Verify Ingestion

Check that jobs were added:
```bash
# Get total count
curl http://localhost:8000/api/v1/jobs/count/total

# View some jobs
curl http://localhost:8000/api/v1/jobs?limit=5
```

### Step 5: Test Recommendations

Now test ML recommendations with the ingested data:
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python developer machine learning",
    "limit": 10
  }'
```

## 🔄 Automated Testing

Run the test script to verify everything works:

```bash
# Make sure server is running first
uvicorn app.main:app --reload

# In another terminal, run the test
python test_rapidapi.py
```

**The test will:**
✅ Check RapidAPI configuration  
✅ Fetch and display sample jobs  
✅ Fetch and display sample internships  
✅ Ingest jobs to database  
✅ Ingest internships to database  
✅ Verify database has the data  
✅ Test ML recommendations  

## 🎨 Mobile App Integration

### React Native Example

```javascript
// services/rapidapi.js
const API_BASE_URL = 'https://your-api.railway.app';

// Ingest jobs and internships (run on app start)
export const initializeJobData = async () => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100`,
      { method: 'POST' }
    );
    const result = await response.json();
    console.log(`✅ Ingested ${result.total_ingested} jobs/internships`);
    return result;
  } catch (error) {
    console.error('Error initializing job data:', error);
    throw error;
  }
};

// Get recommendations (use this in your search)
export const searchJobs = async (query, type = null) => {
  try {
    const body = { query, limit: 20 };
    if (type) body.job_type = type; // 'full-time' or 'internship'
    
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
    console.error('Error searching jobs:', error);
    throw error;
  }
};
```

### Usage in Component

```javascript
import { initializeJobData, searchJobs } from './services/rapidapi';

const JobSearchScreen = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);

  // Initialize data on app launch (once)
  useEffect(() => {
    initializeData();
  }, []);

  const initializeData = async () => {
    try {
      await initializeJobData();
      console.log('✅ Job database initialized');
    } catch (error) {
      console.error('Failed to initialize job data');
    }
  };

  const handleSearch = async (searchQuery) => {
    setLoading(true);
    try {
      const result = await searchJobs(searchQuery, 'full-time');
      setJobs(result.recommendations);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      <SearchBar onSearch={handleSearch} />
      {loading ? (
        <ActivityIndicator />
      ) : (
        <FlatList
          data={jobs}
          renderItem={({ item }) => (
            <JobCard
              title={item.title}
              company={item.company}
              location={item.location}
              similarity={item.similarity_score}
            />
          )}
        />
      )}
    </View>
  );
};
```

## ⏰ Scheduled Updates

### Keep Data Fresh

Set up automatic data refresh (optional):

**Option 1: Cron Job (Linux/Mac)**
```bash
# Add to crontab (crontab -e)
0 */6 * * * curl -X POST "https://your-api.railway.app/api/v1/rapidapi/ingest/all?jobs_limit=50&internships_limit=50"
```

**Option 2: Railway Scheduled Task**
```bash
# In Railway dashboard, add scheduled task
curl -X POST "$API_URL/api/v1/rapidapi/ingest/all?jobs_limit=50&internships_limit=50"
```

**Option 3: Mobile App Background Refresh**
```javascript
// Run weekly in background
import BackgroundFetch from 'react-native-background-fetch';

BackgroundFetch.configure({
  minimumFetchInterval: 15 * 60, // 15 minutes (iOS minimum)
}, async (taskId) => {
  console.log('[BackgroundFetch] Refreshing job data...');
  try {
    await initializeJobData();
    console.log('[BackgroundFetch] Success!');
  } catch (error) {
    console.error('[BackgroundFetch] Error:', error);
  }
  BackgroundFetch.finish(taskId);
});
```

## 📊 Data Flow

### Before (Manual Only)
```
Developer → Create Jobs Manually → Database
```

### After (Automated!)
```
RapidAPI → Fetch Jobs/Internships → Generate Embeddings → Database → Recommendations
```

## 🎯 Key Features

### Intelligent Data Parsing
- Extracts skills from various field names
- Detects remote jobs automatically
- Normalizes data to consistent format
- Handles missing fields gracefully

### Error Resilience
- Continues processing if some jobs fail
- Returns detailed error reports
- Logs all errors for debugging
- No data loss on partial failures

### Performance
- Async operations (fast!)
- Batch embedding generation
- Efficient database inserts
- Minimal memory footprint

### Flexibility
- Preview before ingesting
- Control batch sizes with `limit` parameter
- Separate or combined ingestion
- Filter by job type in recommendations

## 📈 Monitoring

### Check Ingestion Status

```bash
# Total jobs in database
curl http://localhost:8000/api/v1/jobs/count/total

# View latest jobs
curl http://localhost:8000/api/v1/jobs?limit=10

# Check by type
curl "http://localhost:8000/api/v1/jobs?job_type=internship&limit=10"
```

### View Logs

```bash
# Railway
railway logs

# Render
# Check dashboard

# Local
# Console output
```

## 🔧 Troubleshooting

### Issue: "RapidAPI is not configured"
**Solution**: Set `RAPIDAPI_KEY` in your `.env` file

### Issue: "No jobs found"
**Solution**: Check your API key, test manually:
```bash
curl -X GET "https://internships-api.p.rapidapi.com/active-jb-7d" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: internships-api.p.rapidapi.com"
```

### Issue: Some jobs fail to ingest
**This is normal!** Some jobs may have:
- Missing required fields
- Invalid formats
- Encoding issues

The system handles this gracefully and continues processing.

## ✅ Success Checklist

- [ ] Added `RAPIDAPI_KEY` to `.env`
- [ ] Server is running
- [ ] `/api/v1/rapidapi/status` returns configured: true
- [ ] Can fetch jobs successfully
- [ ] Can fetch internships successfully
- [ ] Jobs are being saved to database
- [ ] Recommendations work with ingested data
- [ ] Mobile app can search jobs
- [ ] (Optional) Scheduled updates configured

## 🎉 You're All Set!

Your backend now supports:
- ✅ Two separate RapidAPI endpoints (jobs & internships)
- ✅ Automatic data ingestion
- ✅ ML embedding generation
- ✅ Vector similarity search
- ✅ Preview before saving
- ✅ Comprehensive error handling
- ✅ Mobile app integration ready

**Start ingesting data:**
```bash
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"
```

**Then search from your mobile app:**
```javascript
searchJobs("python developer", "full-time");
searchJobs("software engineering intern", "internship");
```

---

**📖 For more details, see:**
- [RAPIDAPI_INTEGRATION.md](RAPIDAPI_INTEGRATION.md) - Complete guide
- [README.md](README.md) - System overview
- [QUICKSTART.md](QUICKSTART.md) - Deployment guide
