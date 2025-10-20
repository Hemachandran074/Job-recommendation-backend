"""
FastAPI Application - Main Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy import text
import logging

from app.config import settings
from app.database import init_db, close_db, get_engine
from app.ml_service import ml_service

# Import routers
from app.routers import jobs, recommendations, users, rapidapi  # ✅ Make sure users is imported

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Job Recommendation API...")
    logger.info("📊 Initializing database...")
    
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    logger.info("🤖 Loading ML model...")
    try:
        ml_service.load_model()
        logger.info("✅ ML model loaded")
    except Exception as e:
        logger.error(f"❌ ML model loading failed: {e}")
        raise
    
    logger.info("✅ Application ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    try:
        await close_db()
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - ✅ MAKE SURE THIS LINE EXISTS
app.include_router(users.router, prefix="/api/v1", tags=["Users"])  # ✅ CRITICAL!
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(rapidapi.router, prefix="/api/v1", tags=["RapidAPI"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Job Recommendation API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Check database
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # Check ML model
    try:
        if ml_service.model is not None:
            status["ml_model"] = f"loaded ({settings.MODEL_NAME})"
        else:
            status["ml_model"] = "not loaded"
            status["status"] = "degraded"
    except Exception as e:
        logger.error(f"ML model health check failed: {e}")
        status["ml_model"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
