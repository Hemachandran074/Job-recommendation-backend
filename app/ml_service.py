"""
Machine Learning service for generating embeddings
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MLService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        """Initialize the ML model"""
        self.model = None
        self.model_name = settings.MODEL_NAME
        self.embedding_dim = settings.EMBEDDING_DIMENSION
        
    def load_model(self):
        """Load the sentence transformer model"""
        if self.model is None:
            logger.info(f"Loading ML model: {self.model_name}")
            try:
                # Set HuggingFace token if available (needed for gated models)
                model_kwargs = {}
                if settings.HUGGINGFACE_TOKEN:
                    logger.info("Using HuggingFace token for authentication")
                    model_kwargs['token'] = settings.HUGGINGFACE_TOKEN
                
                self.model = SentenceTransformer(self.model_name, **model_kwargs)
                logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            List of float values representing the embedding
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Normalize the embedding (important for cosine similarity)
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.tolist()
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
        if self.model is None:
            self.load_model()
        
        try:
            # Generate embeddings in batch
            embeddings = self.model.encode(
                texts,
                batch_size=settings.BATCH_SIZE,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Normalize embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            
            return embeddings.tolist()
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
