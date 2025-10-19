# 🚀 Complete Deployment Commands Reference

## Quick Deploy Commands

### Railway (Recommended - Fastest)

```bash
# One-time setup
npm i -g @railway/cli
railway login

# Deploy
cd job-recommendation-backend
railway init
railway add -d postgresql
railway run psql $DATABASE_URL -c "CREATE EXTENSION vector;"
railway variables set SECRET_KEY=$(openssl rand -hex 32) CORS_ORIGINS="*"
railway up
railway domain

# Management
railway logs              # View logs
railway variables         # View environment variables
railway run [command]     # Run command in Railway environment
railway link              # Link to existing project
```

### Render

```bash
# Setup (via Dashboard)
1. Go to render.com
2. New → PostgreSQL (Free)
3. New → Web Service
   - Build: pip install -r requirements.txt
   - Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
4. Set environment variables in dashboard
5. Deploy

# Database Setup
# In Render PostgreSQL dashboard → Connect:
psql [connection-string]
CREATE EXTENSION vector;
```

### Fly.io

```bash
# Setup
curl -L https://fly.io/install.sh | sh  # macOS/Linux
fly auth login

# Deploy
cd job-recommendation-backend
fly launch
fly postgres create
fly postgres attach [postgres-name]
fly postgres connect -a [postgres-name]
  CREATE EXTENSION vector;
  \q
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
fly deploy

# Management
fly logs
fly ssh console
fly status
```

---

## Environment Variables Setup

### Required Variables

```bash
# Railway
railway variables set DATABASE_URL="postgresql+asyncpg://..." \
  SECRET_KEY="your-secret-key" \
  API_TITLE="Job Recommendation API" \
  CORS_ORIGINS="*"

# Fly.io
fly secrets set SECRET_KEY="your-secret-key" \
  CORS_ORIGINS="*"

# Render (use dashboard UI)
DATABASE_URL: postgresql+asyncpg://...
SECRET_KEY: [generate with: openssl rand -hex 32]
CORS_ORIGINS: *
```

### Generate Secure Secret Key

```bash
# Method 1: OpenSSL
openssl rand -hex 32

# Method 2: Python
python -c "import secrets; print(secrets.token_hex(32))"

# Method 3: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## Database Commands

### Enable pgvector Extension

```sql
-- Railway
railway run psql $DATABASE_URL
CREATE EXTENSION IF NOT EXISTS vector;
\q

-- Render
-- Connect via dashboard, then:
CREATE EXTENSION IF NOT EXISTS vector;

-- Fly.io
fly postgres connect -a [postgres-app-name]
CREATE EXTENSION vector;
\q

-- Supabase
-- In SQL Editor:
CREATE EXTENSION IF NOT EXISTS vector;
```

### Verify pgvector Installation

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Should show:
--  extname | extowner | ...
--  vector  | ...
```

### Check Database Connection

```bash
# Railway
railway run psql $DATABASE_URL -c "SELECT 1;"

# Render/Supabase
psql "your-connection-string" -c "SELECT 1;"
```

---

## Testing Commands

### Health Check

```bash
# Local
curl http://localhost:8000/health

# Deployed
curl https://your-app.railway.app/health
```

### Create Test Job

```bash
curl -X POST "https://your-app.railway.app/api/v1/jobs/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "Remote",
    "description": "Python developer with ML experience",
    "skills": ["Python", "ML", "FastAPI"],
    "job_type": "full-time",
    "remote": true
  }'
```

### Get Recommendations

```bash
curl -X POST "https://your-app.railway.app/api/v1/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python machine learning",
    "limit": 5
  }'
```

### Run Example Import Script

```bash
# Local
python example_import.py

# With deployed API
API_URL=https://your-app.railway.app python example_import.py
```

---

## Monitoring & Logs

### View Logs

```bash
# Railway
railway logs
railway logs --tail 100

# Render
# Use dashboard: https://dashboard.render.com

# Fly.io
fly logs
fly logs --tail
```

### View Metrics

```bash
# Railway
railway status

# Fly.io
fly status
fly vm status
```

---

## Troubleshooting Commands

### Debug Connection Issues

```bash
# Test database connection
railway run psql $DATABASE_URL -c "SELECT version();"

# Check environment variables
railway variables

# Test API locally with production database
# In .env, set DATABASE_URL to production
uvicorn app.main:app --reload
```

### Fix Common Issues

```bash
# Issue: pgvector not found
railway run psql $DATABASE_URL
CREATE EXTENSION vector;
\q

# Issue: Module not found
pip install -r requirements.txt
railway up

# Issue: SECRET_KEY not set
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Issue: CORS errors
railway variables set CORS_ORIGINS="*"
```

### Reset Deployment

```bash
# Railway
railway down
railway up

# Fly.io
fly destroy [app-name]
fly launch

# Render
# Delete service in dashboard
# Create new service
```

---

## CI/CD Setup (GitHub Actions)

### Create `.github/workflows/deploy.yml`

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway
        run: npm i -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Get Railway Token

```bash
# Generate token
railway token

# Add to GitHub:
# Settings → Secrets → New repository secret
# Name: RAILWAY_TOKEN
# Value: [paste token]
```

---

## Scaling Commands

### Railway

```bash
# View current resources
railway status

# Upgrade (via dashboard)
# Go to https://railway.app/dashboard
# Select project → Settings → Plan
```

### Fly.io

```bash
# Scale vertically (more resources per instance)
fly scale vm shared-cpu-1x --memory 1024

# Scale horizontally (more instances)
fly scale count 2

# View current scale
fly scale show
```

### Render

```
# Via dashboard:
# Service → Settings → Instance Type
# Upgrade to Starter ($7/mo) or higher
```

---

## Backup & Restore

### Backup Database

```bash
# Railway
railway run pg_dump $DATABASE_URL > backup.sql

# Supabase
pg_dump "postgresql://postgres:...@db.xxx.supabase.co:5432/postgres" > backup.sql
```

### Restore Database

```bash
# Railway
railway run psql $DATABASE_URL < backup.sql

# Supabase
psql "postgresql://postgres:...@db.xxx.supabase.co:5432/postgres" < backup.sql
```

---

## Performance Optimization

### Create Database Indexes

```sql
-- Connect to database
railway run psql $DATABASE_URL

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON jobs 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company);

CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs USING gin(to_tsvector('english', location));

-- Verify indexes
\di
```

### Monitor Query Performance

```sql
-- Enable query timing
\timing

-- Analyze slow queries
EXPLAIN ANALYZE
SELECT *
FROM jobs
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

---

## Update & Redeploy

### Update Code

```bash
# Local changes
git add .
git commit -m "Update feature"
git push origin main

# Railway (auto-deploys from GitHub)
railway link [project-id]
# Will auto-deploy on git push

# Manual deployment
railway up

# Fly.io
fly deploy

# Render
# Auto-deploys from GitHub
# Or manually trigger in dashboard
```

### Update Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Redeploy
railway up  # Railway
fly deploy  # Fly.io
# Render: Auto-deploys on git push
```

---

## Cost Management

### Monitor Usage

```bash
# Railway
# Visit: https://railway.app/account/usage

# Fly.io
fly billing

# Render
# Visit: https://dashboard.render.com/billing
```

### Free Tier Limits

**Railway:**
- 500 execution hours/month
- $5 credit/month
- Sleeps after 30 min inactivity

**Render:**
- 750 hours/month
- Spins down after 15 min inactivity
- PostgreSQL: 90 days data retention

**Supabase:**
- 500MB database
- 2GB bandwidth
- 50MB file storage

---

## Security Best Practices

### Rotate Secrets

```bash
# Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# Update
railway variables set SECRET_KEY=$NEW_SECRET

# Restart
railway restart
```

### Update CORS for Production

```bash
# Development (allow all)
railway variables set CORS_ORIGINS="*"

# Production (specific domains)
railway variables set CORS_ORIGINS="https://yourapp.com,https://api.yourapp.com"
```

### Enable HTTPS Only

```bash
# Railway/Render: HTTPS automatic
# No configuration needed

# For custom domains:
# Add domain in dashboard
# Configure DNS: CNAME to provided URL
```

---

## Cheat Sheet

```bash
# Quick Deploy
railway init && railway add -d postgresql && railway up

# Quick Test
curl https://your-app.railway.app/health

# Quick Logs
railway logs

# Quick Variables
railway variables

# Quick Scale (Fly.io)
fly scale count 2

# Quick Backup
railway run pg_dump $DATABASE_URL > backup.sql

# Quick Import Sample Data
python example_import.py
```

---

## Next Steps After Deployment

1. ✅ Test all endpoints via `/docs`
2. ✅ Import sample data: `python example_import.py`
3. ✅ Set up monitoring (Railway dashboard)
4. ✅ Configure custom domain (optional)
5. ✅ Set up CI/CD (GitHub Actions)
6. ✅ Add API key authentication (if needed)
7. ✅ Connect to your mobile app
8. ✅ Monitor usage and costs

---

## Support Resources

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Fly.io Docs: https://fly.io/docs
- Supabase Docs: https://supabase.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- pgvector Docs: https://github.com/pgvector/pgvector
