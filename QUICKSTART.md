# 🎯 Quick Start Guide

Get your job recommendation API up and running in 10 minutes!

## Prerequisites
- Python 3.11+
- Git
- Account on Railway/Render/Supabase (all free)

## Option 1: Local Development (5 minutes)

```bash
# 1. Setup environment
cd job-recommendation-backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure database (use Supabase)
# Go to supabase.com → Create project → Enable vector extension
# Copy connection string

# 3. Setup environment
copy .env.example .env
# Edit .env:
# DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
# SECRET_KEY=your-random-secret-key

# 4. Run
uvicorn app.main:app --reload

# 5. Test
# Visit: http://localhost:8000/docs
```

## Option 2: Deploy to Railway (10 minutes)

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login & deploy
railway login
cd job-recommendation-backend
railway init
railway add -d postgresql
railway up

# 3. Enable pgvector
railway run psql $DATABASE_URL
CREATE EXTENSION vector;
\q

# 4. Set variables
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set CORS_ORIGINS="*"

# 5. Get URL
railway domain

# Done! Visit: https://your-app.up.railway.app/docs
```

## Option 3: Deploy to Render (15 minutes)

1. **Create PostgreSQL Database**
   - Go to render.com → New → PostgreSQL
   - Free tier → Create

2. **Create Web Service**
   - New → Web Service
   - Connect GitHub repo
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   DATABASE_URL: [From PostgreSQL, change to postgresql+asyncpg://...]
   SECRET_KEY: [Generate: openssl rand -hex 32]
   CORS_ORIGINS: *
   ```

4. **Enable pgvector**
   - Connect to DB → Run: `CREATE EXTENSION vector;`

5. **Deploy**
   - Click "Create Web Service"
   - Visit: https://your-app.onrender.com/docs

## Test Your API

### 1. Check Health
```bash
curl https://your-api-url/health
```

### 2. Create a Job
```bash
curl -X POST "https://your-api-url/api/v1/jobs/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "Remote",
    "description": "Looking for Python developer with ML experience",
    "skills": ["Python", "Machine Learning", "FastAPI"],
    "job_type": "full-time",
    "remote": true
  }'
```

### 3. Get Recommendations
```bash
curl -X POST "https://your-api-url/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python developer with machine learning",
    "limit": 5
  }'
```

## What You Get

✅ **Complete REST API** with:
- `/api/v1/jobs/ingest` - Add jobs
- `/api/v1/recommendations` - Get recommendations
- `/api/v1/users/register` - User management
- `/health` - Health check
- `/docs` - Interactive API documentation

✅ **ML-Powered Search** using:
- sentence-transformers (all-MiniLM-L6-v2)
- pgvector for similarity search
- Semantic job matching

✅ **Production Ready**:
- Async database operations
- CORS enabled
- Error handling
- Logging
- Authentication ready (JWT)

## Next Steps

1. **Connect Your Mobile App**
   - Use base URL: `https://your-api-url`
   - Add endpoints to your app's API client
   - See API docs at `/docs`

2. **Add More Jobs**
   - Manual: Use `/api/v1/jobs/ingest`
   - Automated: Integrate RapidAPI
   - Batch: Create script using API

3. **Customize**
   - Adjust similarity threshold (`min_score`)
   - Add filters (location, job_type, remote)
   - Tune ML model (change `MODEL_NAME` in config)

## Troubleshooting

**API not responding?**
- Check logs: `railway logs` or Render dashboard
- Verify DATABASE_URL format
- Ensure pgvector extension enabled

**Slow first request?**
- ML model downloads on first startup (2-3 minutes)
- Subsequent requests are fast
- Consider paid tier for no cold starts

**CORS errors?**
- Check CORS_ORIGINS environment variable
- Set to `*` for development
- Set specific domains for production

## Architecture

```
Mobile App
    ↓
FastAPI Server (Railway/Render)
    ↓
PostgreSQL + pgvector (Supabase/Railway)
    ↓
ML Model (sentence-transformers)
```

## Cost

**Free Tier:**
- Railway: 500 hours/month
- Render: 750 hours/month
- Supabase: 500MB database
- Perfect for MVP and small projects

**Upgrade (~$5-20/month):**
- More resources
- No cold starts
- Multiple environments

## Support

- 📚 Full Documentation: See README.md
- 🚀 Deployment Guide: See DEPLOYMENT_GUIDE.md
- 💬 Issues: Open GitHub issue
- 📧 Questions: Check /docs endpoint for API reference

---

**You're all set!** 🎉

Your ML-powered job recommendation API is ready to use!
