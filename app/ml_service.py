"""
Machine Learning service for generating embeddings using Google Generative AI
"""
from typing import List, Union
import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Service for generating text embeddings using Google's API"""
    
    def __init__(self):
        """Initialize the ML service"""
        self.model = None
        self.model_name = settings.MODEL_NAME
        self.embedding_dim = settings.EMBEDDING_DIMENSION
        self.api_configured = False
        
    def load_model(self):
        """Configure Google Generative AI API"""
        if not self.api_configured:
            logger.info(f"Configuring Google Generative AI API")
            try:
                # Configure the API key
                if not settings.EMBEDDING_API:
                    raise ValueError("EMBEDDING_API key not found in settings")
                
                genai.configure(api_key=settings.EMBEDDING_API)
                self.api_configured = True
                self.model = "models/text-embedding-004"  # Google's latest embedding model (768 dims)
                
                logger.info(f"✅ Google AI API configured. Using model: {self.model}")
                logger.info(f"Embedding dimension: {self.embedding_dim}")
            except Exception as e:
                logger.error(f"Failed to configure Google AI API: {e}")
                raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Google's API
        
        Args:
            text: Input text
            
        Returns:
            List of float values representing the embedding
        """
        if not self.api_configured:
            self.load_model()
        
        try:
            # Generate embedding using Google's API
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"  # For storing/indexing
            )
            
            embedding = result['embedding']
            
            # Ensure correct dimension
            if len(embedding) != self.embedding_dim:
                logger.warning(f"Embedding dimension mismatch: got {len(embedding)}, expected {self.embedding_dim}")
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        if not self.api_configured:
            self.load_model()
        
        try:
            # Google's API supports batch embedding
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 10  # Adjust based on API limits
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                for text in batch:
                    result = genai.embed_content(
                        model=self.model,
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(result['embedding'])
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def create_job_text(self, job_data: dict) -> str:
        """
        Create a comprehensive text representation of a job for embedding
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Combined text string
        """
        parts = []
        
        # Title (weight it by including twice)
        if job_data.get('title'):
            parts.append(job_data['title'])
            parts.append(job_data['title'])
        
        # Company
        if job_data.get('company'):
            parts.append(f"Company: {job_data['company']}")
        
        # Location
        if job_data.get('location'):
            parts.append(f"Location: {job_data['location']}")
        
        # Description
        if job_data.get('description'):
            # Take first 500 characters of description
            desc = job_data['description'][:500]
            parts.append(desc)
        
        # Skills
        if job_data.get('skills'):
            skills = job_data['skills']
            if isinstance(skills, list):
                parts.append(f"Required skills: {', '.join(skills)}")
        
        # Job type
        if job_data.get('job_type'):
            parts.append(f"Job type: {job_data['job_type']}")
        
        # Experience level
        if job_data.get('experience_level'):
            parts.append(f"Experience: {job_data['experience_level']}")
        
        # Remote
        if job_data.get('remote'):
            parts.append("Remote work available")
        
        return " ".join(parts)
    
    def create_user_profile_text(self, user_data: dict) -> str:
        """
        Create a text representation of user profile for embedding
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Combined text string
        """
        parts = []
        
        # Skills
        if user_data.get('skills'):
            skills = user_data['skills']
            if isinstance(skills, list):
                parts.append(f"Skills: {', '.join(skills)}")
        
        # Experience
        if user_data.get('experience_years'):
            parts.append(f"Experience: {user_data['experience_years']} years")
        
        # Preferred job type
        if user_data.get('preferred_job_type'):
            parts.append(f"Looking for: {user_data['preferred_job_type']}")
        
        # Preferred locations
        if user_data.get('preferred_locations'):
            locs = user_data['preferred_locations']
            if isinstance(locs, list):
                parts.append(f"Preferred locations: {', '.join(locs)}")
        
        # Resume text
        if user_data.get('resume_text'):
            # Take first 1000 characters
            parts.append(user_data['resume_text'][:1000])
        
        return " ".join(parts)


# Global ML service instance
ml_service = MLService()
