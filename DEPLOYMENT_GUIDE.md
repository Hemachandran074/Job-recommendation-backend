# 🚀 Complete Deployment Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Database Setup (Supabase)](#database-setup-supabase)
3. [Deploy to Railway](#deploy-to-railway)
4. [Deploy to Render](#deploy-to-render)
5. [Deploy to Fly.io](#deploy-to-flyio)
6. [Testing Your API](#testing-your-api)
7. [Troubleshooting](#troubleshooting)

---

## 🏠 Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (with pgvector extension)
- Git

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd job-recommendation-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux

# Edit .env file with your settings
# Minimum required:
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/job_recommendation
# SECRET_KEY=your-secret-key-here
```

### Step 3: Setup Local PostgreSQL (Optional)

```bash
# Install PostgreSQL 15+
# Then create database
psql -U postgres
CREATE DATABASE job_recommendation;
\c job_recommendation
CREATE EXTENSION vector;
\q
```

### Step 4: Run Locally

```bash
# Start the server
uvicorn app.main:app --reload

# Or use Python directly
python -m app.main
```

Visit: `http://localhost:8000/docs` for interactive API documentation

---

## 📊 Database Setup (Supabase) - **RECOMMENDED FREE OPTION**

### Why Supabase?
- ✅ Free tier (500MB database, 2GB bandwidth)
- ✅ PostgreSQL with pgvector support
- ✅ Automatic backups
- ✅ No credit card required
- ✅ Dashboard included

### Step-by-Step Setup

#### 1. Create Supabase Account

```bash
# Go to https://supabase.com
# Click "Start your project"
# Sign up with GitHub (free)
```

#### 2. Create New Project

```
Project Name: job-recommendation
Database Password: [Create a strong password]
Region: Choose closest to your users
Plan: Free tier
```

#### 3. Enable pgvector Extension

```sql
-- Go to SQL Editor in Supabase dashboard
-- Run this SQL:

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation:
SELECT * FROM pg_extension WHERE extname = 'vector';
```

#### 4. Get Connection String

```
1. Go to Project Settings → Database
2. Copy "Connection string" under "Connection parameters"
3. Format: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

4. Convert to asyncpg format:
   postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

#### 5. Update .env

```env
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

---

## 🚂 Deploy to Railway - **EASIEST FREE DEPLOYMENT**

### Why Railway?
- ✅ 500 hours free per month
- ✅ Automatic PostgreSQL setup
- ✅ One-click deployment
- ✅ Automatic HTTPS
- ✅ GitHub integration

### Step-by-Step Deployment

#### 1. Install Railway CLI

```bash
# Install
npm i -g @railway/cli

# Login
railway login
```

#### 2. Initialize Project

```bash
# In your project directory
cd job-recommendation-backend

# Initialize Railway project
railway init

# Project name: job-recommendation-backend
```

#### 3. Add PostgreSQL Database

```bash
# Add PostgreSQL service
railway add -d postgresql

# This automatically creates:
# - PostgreSQL instance
# - DATABASE_URL environment variable
```

#### 4. Enable pgvector Extension

```bash
# Connect to Railway PostgreSQL
railway run psql $DATABASE_URL

# In psql:
CREATE EXTENSION vector;
\q
```

#### 5. Set Environment Variables

```bash
# Set required variables
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set API_TITLE="Job Recommendation API"
railway variables set CORS_ORIGINS="*"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="False"

# View all variables
railway variables
```

#### 6. Deploy

```bash
# Deploy to Railway
railway up

# Get deployment URL
railway domain

# View logs
railway logs
```

#### 7. Access Your API

```
Your API will be available at:
https://your-app-name.up.railway.app

API Docs: https://your-app-name.up.railway.app/docs
Health Check: https://your-app-name.up.railway.app/health
```

### Railway Dashboard

```
Visit: https://railway.app/dashboard

You can:
- View logs
- Monitor CPU/Memory
- Scale resources
- Manage environment variables
- View database metrics
```

---

## 🎨 Deploy to Render - **FREE ALTERNATIVE**

### Why Render?
- ✅ Free tier available
- ✅ PostgreSQL included
- ✅ Automatic deployments
- ✅ Custom domains

### Step-by-Step Deployment

#### 1. Create Render Account

```
1. Go to https://render.com
2. Sign up with GitHub
```

#### 2. Create PostgreSQL Database

```
1. Click "New +" → "PostgreSQL"
2. Name: job-recommendation-db
3. Plan: Free
4. Create Database
5. Copy "Internal Database URL"
```

#### 3. Create Web Service

```
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - Name: job-recommendation-api
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 4. Set Environment Variables

```
In Render Dashboard → Environment:

DATABASE_URL: [Paste Internal Database URL, change postgresql:// to postgresql+asyncpg://]
SECRET_KEY: [Generate with: openssl rand -hex 32]
API_TITLE: Job Recommendation API
CORS_ORIGINS: *
ENVIRONMENT: production
DEBUG: False
```

#### 5. Deploy

```
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes first time)
3. Access at: https://your-app-name.onrender.com
```

#### 6. Enable pgvector

```bash
# Connect to database
# In Render Dashboard → PostgreSQL → Connect

psql [YOUR_DATABASE_URL]
CREATE EXTENSION vector;
\q
```

---

## ✈️ Deploy to Fly.io - **ADVANCED OPTION**

### Step-by-Step

#### 1. Install flyctl

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. Login

```bash
fly auth login
```

#### 3. Launch Application

```bash
cd job-recommendation-backend

fly launch
# Follow prompts:
# - Name: job-recommendation
# - Region: Choose closest
# - PostgreSQL: Yes
# - Redis: No
```

#### 4. Configure Database

```bash
# Attach database
fly postgres attach [postgres-app-name]

# Connect and enable pgvector
fly postgres connect
CREATE EXTENSION vector;
\q
```

#### 5. Set Secrets

```bash
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
fly secrets set CORS_ORIGINS="*"
```

#### 6. Deploy

```bash
fly deploy
```

---

## 🧪 Testing Your Deployed API

### 1. Health Check

```bash
# Replace with your deployment URL
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ml_model": "loaded (sentence-transformers/all-MiniLM-L6-v2)",
  "timestamp": "2025-01-20T12:00:00"
}
```

### 2. Create a Test Job

```bash
curl -X POST "https://your-app.railway.app/api/v1/jobs/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "description": "Looking for experienced Python developer with FastAPI and PostgreSQL skills",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Machine Learning"],
    "salary_min": 120000,
    "salary_max": 180000,
    "job_type": "full-time",
    "experience_level": "senior",
    "remote": true,
    "source": "manual"
  }'
```

### 3. Get Recommendations

```bash
curl -X POST "https://your-app.railway.app/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python developer with machine learning experience",
    "limit": 5
  }'
```

### 4. Interactive Testing

```
Visit: https://your-app.railway.app/docs

- Test all endpoints interactively
- View request/response formats
- Download OpenAPI specification
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# For deployment, check build logs
railway logs  # Railway
# or visit Render dashboard for logs
```

### Issue: Database connection fails

```bash
# Check DATABASE_URL format
# Should be: postgresql+asyncpg://user:pass@host:5432/dbname

# Test connection
railway run psql $DATABASE_URL  # Railway
```

### Issue: pgvector not found

```sql
-- Connect to database and run
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Issue: ML model loading slow

```
First startup takes 2-5 minutes to download model.
Subsequent starts are faster (model is cached).

Railway/Render free tier may be slower.
Consider upgrading for production.
```

### Issue: CORS errors

```bash
# Check CORS_ORIGINS in environment
railway variables set CORS_ORIGINS="https://your-frontend.com,https://another-domain.com"

# Or allow all (development only)
railway variables set CORS_ORIGINS="*"
```

---

## 📝 Environment Variables Checklist

Required:
- ✅ DATABASE_URL
- ✅ SECRET_KEY

Recommended:
- ✅ API_TITLE
- ✅ CORS_ORIGINS
- ✅ ENVIRONMENT
- ✅ DEBUG

Optional:
- ⬜ RAPIDAPI_KEY (for job ingestion)
- ⬜ MODEL_NAME (if using different model)

---

## 🎉 Success Checklist

- [ ] API accessible at deployment URL
- [ ] `/health` endpoint returns "healthy"
- [ ] `/docs` shows interactive documentation
- [ ] Can create jobs via `/api/v1/jobs/ingest`
- [ ] Can get recommendations via `/api/v1/recommendations`
- [ ] Database has pgvector extension enabled
- [ ] ML model loads successfully

---

## 🆘 Need Help?

1. Check logs:
   - Railway: `railway logs`
   - Render: Dashboard → Logs
   - Fly.io: `fly logs`

2. Check environment variables:
   - Railway: `railway variables`
   - Render: Dashboard → Environment
   - Fly.io: `fly secrets list`

3. Test locally first:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Common commands:
   ```bash
   # Railway
   railway up           # Deploy
   railway logs         # View logs
   railway run [cmd]    # Run command
   railway link         # Link to project
   
   # Render
   # Use dashboard at render.com
   
   # Fly.io
   fly deploy           # Deploy
   fly logs             # View logs
   fly ssh console      # SSH access
   ```

---

## 🚀 Next Steps

1. ✅ Deploy successfully
2. ⬜ Add authentication (JWT already configured)
3. ⬜ Integrate with RapidAPI for job ingestion
4. ⬜ Connect to your mobile app
5. ⬜ Add monitoring (Sentry, LogRocket)
6. ⬜ Set up CI/CD (GitHub Actions)
7. ⬜ Add rate limiting
8. ⬜ Implement caching (Redis)

---

## 💰 Cost Estimation

### Free Tier Limits:

**Railway:**
- 500 execution hours/month
- 512MB RAM
- 1GB disk
- Free PostgreSQL
- Perfect for: MVP, small projects

**Render:**
- 750 hours/month
- 512MB RAM
- Free PostgreSQL (90 days inactive deletion)
- Perfect for: Testing, small projects

**Supabase:**
- 500MB database
- 2GB bandwidth
- Unlimited API requests
- Perfect for: Database only

### Paid Upgrade (~$5-20/month):
- More RAM/CPU
- Always-on (no cold starts)
- Better performance
- Multiple environments
