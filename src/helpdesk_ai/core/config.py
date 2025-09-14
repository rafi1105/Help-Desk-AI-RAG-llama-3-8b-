"""
Configuration module for Help Desk AI RAG system.
"""
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config(BaseModel):
    """Configuration settings for the Help Desk AI system."""
    
    # Model Configuration
    huggingface_token: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")
    model_name: str = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Database and Storage
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    
    # Generation Parameters
    max_tokens: int = int(os.getenv("MAX_TOKENS", "512"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    
    # System Settings
    device: str = "cuda" if os.getenv("DEVICE") == "cuda" else "cpu"
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    class Config:
        env_file = ".env"

# Global configuration instance
config = Config()