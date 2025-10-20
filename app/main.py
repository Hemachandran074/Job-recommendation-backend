"""
FastAPI Application - Main Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from sqlalchemy import text

from app.config import settings
from app.database import init_db, close_db
from app.ml_service import ml_service
from app.routers import jobs, recommendations, users, rapidapi
from app.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Job Recommendation API...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized")
        
        # Load ML model
        logger.info("🤖 Loading ML model...")
        ml_service.load_model()
        logger.info("✅ ML model loaded")
        
        logger.info("✨ Application startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")
    await close_db()
    logger.info("✅ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router)
app.include_router(recommendations.router)
app.include_router(users.router)
app.include_router(rapidapi.router, prefix="/api/v1/rapidapi", tags=["rapidapi"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 Job Recommendation API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of:
    - API server
    - Database connection
    - ML model
    """
    try:
        # Check database
        from app.database import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"error: {str(e)}"
    
    # Check ML model
    try:
        if ml_service.model is not None:
            ml_status = f"loaded ({settings.MODEL_NAME})"
        else:
            ml_status = "not loaded"
    except Exception as e:
        ml_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.API_VERSION,
        database=db_status,
        ml_model=ml_status,
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )
