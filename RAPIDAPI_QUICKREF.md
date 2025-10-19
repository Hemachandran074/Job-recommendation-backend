# 🚀 RapidAPI Quick Reference

## 📋 One-Page Cheat Sheet

### ⚙️ Configuration
```env
RAPIDAPI_KEY=your-key-here
RAPIDAPI_JOBS_URL=https://internships-api.p.rapidapi.com/active-jb-7d
RAPIDAPI_INTERNSHIPS_URL=https://internships-api.p.rapidapi.com/active-jb-7d
```

### 🎯 7 New API Endpoints

| Endpoint | Purpose | Query Params |
|----------|---------|--------------|
| `GET /api/v1/rapidapi/status` | Check config | - |
| `POST /api/v1/rapidapi/fetch/jobs` | Preview jobs | `?limit=10` |
| `POST /api/v1/rapidapi/fetch/internships` | Preview internships | `?limit=10` |
| `POST /api/v1/rapidapi/fetch/all` | Preview both | `?jobs_limit=10&internships_limit=10` |
| `POST /api/v1/rapidapi/ingest/jobs` | Fetch + save jobs | `?limit=50` |
| `POST /api/v1/rapidapi/ingest/internships` | Fetch + save internships | `?limit=50` |
| `POST /api/v1/rapidapi/ingest/all` | Fetch + save everything | `?jobs_limit=100&internships_limit=100` |

### 🔧 Quick Commands

```bash
# Check configuration
curl http://localhost:8000/api/v1/rapidapi/status

# Ingest initial data
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"

# Test recommendations
curl -X POST "http://localhost:8000/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"query": "python developer", "limit": 10}'

# Check total jobs
curl http://localhost:8000/api/v1/jobs/count/total

# Run test script
python test_rapidapi.py
```

### 📱 Mobile App Integration

```javascript
// Initialize database (run once on app start)
await fetch('https://your-api.railway.app/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100', {
  method: 'POST'
});

// Search jobs (use this in your UI)
const response = await fetch('https://your-api.railway.app/api/v1/recommendations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: searchText,
    limit: 20,
    job_type: 'full-time' // or 'internship'
  })
});
const data = await response.json();
// data.recommendations contains job results with similarity scores
```

### 📁 New Files
- ✅ `app/rapidapi_service.py` - Core service
- ✅ `app/routers/rapidapi.py` - API endpoints
- ✅ `test_rapidapi.py` - Test script
- ✅ `RAPIDAPI_INTEGRATION.md` - Full guide
- ✅ `RAPIDAPI_WHATS_NEW.md` - Change summary
- ✅ `RAPIDAPI_COMPLETE_SUMMARY.md` - Complete overview

### 🔄 Updated Files
- ✅ `.env.example` - Added RapidAPI config
- ✅ `app/config.py` - Added RapidAPI settings
- ✅ `app/main.py` - Added RapidAPI router
- ✅ `README.md` - Added RapidAPI section

### 🎯 Workflow

```
1. Configure → Set RAPIDAPI_KEY in .env
2. Deploy → railway up or render deploy
3. Check → GET /api/v1/rapidapi/status
4. Ingest → POST /api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100
5. Test → POST /api/v1/recommendations with query
6. Connect → Use in mobile app
7. Schedule → Set up cron job for daily updates (optional)
```

### ✅ Success Criteria
- [ ] Status shows `configured: true`
- [ ] Can fetch jobs successfully
- [ ] Jobs appear in database
- [ ] Recommendations return results
- [ ] Mobile app can search

### 📚 Documentation
1. **RAPIDAPI_COMPLETE_SUMMARY.md** - Complete overview (start here!)
2. **RAPIDAPI_INTEGRATION.md** - Detailed guide with examples
3. **QUICKSTART.md** - Deployment guide
4. **README.md** - System overview

### 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "RapidAPI is not configured" | Set `RAPIDAPI_KEY` in `.env` |
| "No jobs found" | Check API key, test manually with curl |
| Some jobs fail | Normal! System continues with valid jobs |
| Slow ingestion | Use smaller `limit` values (50 instead of 500) |

### 🎉 You're Ready!

**Quick Start**:
```bash
# 1. Configure
echo "RAPIDAPI_KEY=your-key" >> .env

# 2. Start server
uvicorn app.main:app --reload

# 3. Ingest data
curl -X POST "http://localhost:8000/api/v1/rapidapi/ingest/all?jobs_limit=100&internships_limit=100"

# 4. Test
python test_rapidapi.py
```

---

**Built with ❤️ - Your complete ML-powered job recommendation system is ready!**
