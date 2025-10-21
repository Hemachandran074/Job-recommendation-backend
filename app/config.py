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
    
    # ML Model Configuration
    # ML Model Options:
    # - Google text-embedding-004 (768 dims, via API - RECOMMENDED)
    # - BAAI/bge-m3 (1024 dims, 567MB, multilingual, no approval needed)
    # - sentence-transformers/all-mpnet-base-v2 (768 dims, 420MB, no approval needed)
    # - sentence-transformers/all-MiniLM-L6-v2 (384 dims, 22MB, no approval needed)
    # - google/embeddinggemma-300m (768 dims, 300MB, requires HuggingFace approval)
    MODEL_NAME: str = "text-embedding-004"  # Google's embedding model via API
    EMBEDDING_DIMENSION: int = 768  # Google's model uses 768 dimensions
    BATCH_SIZE: int = 32
    EMBEDDING_API: Optional[str] = None  # Google Generative AI API Key
    HUGGINGFACE_TOKEN: Optional[str] = None
    
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
