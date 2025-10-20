"""
Configuration management using Pydantic Settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # API
    API_TITLE: str = "Job Recommendation API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "ML-powered job recommendation system"
    CORS_ORIGINS: str = "*"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model
    MODEL_NAME: str = "google/embeddinggemma-300m"
    EMBEDDING_DIMENSION: int = 768
    BATCH_SIZE: int = 32
    
    # RapidAPI (Optional)
    RAPIDAPI_KEY: Optional[str] = None
    RAPIDAPI_HOST: str = "internships-api.p.rapidapi.com"
    RAPIDAPI_JOBS_URL: str = "https://internships-api.p.rapidapi.com/active-jb-7d"
    RAPIDAPI_INTERNSHIPS_URL: str = "https://internships-api.p.rapidapi.com/active-jb-7d"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    LOG_LEVEL: str = "info"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
