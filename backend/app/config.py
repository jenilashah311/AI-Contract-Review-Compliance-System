"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    database_url: str = "postgresql://contract_user:contract_pass@localhost:5432/contract_compliance"
    upload_dir: str = "./uploads"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    similarity_threshold: float = 0.60
    keyword_match_bonus: float = 0.05  # Keyword overlap bonus
    missing_weight: int = 10
    conflict_weight: int = 5
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
