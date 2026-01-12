"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://genai_user:genai_password@localhost:5432/genai_stack"
    
    # OpenAI
    openai_api_key: str = ""
    
    # SerpAPI
    serpapi_api_key: str = ""
    
    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"
    
    # Application
    app_env: str = "development"
    debug: bool = True
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:80"
    ]
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
