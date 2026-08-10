import os
from functools import lru_cache
from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Typed application settings loaded from environment variables and local .env file.
    """
    app_name: str = "DataPilot-AI"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    secret_key: str = Field(default="datapilot-secret-key-change-in-production", alias="SECRET_KEY")
    
    # Database
    database_url: str = Field(default="sqlite:///./datapilot.db", alias="DATABASE_URL")
    
    # File Storage
    storage_dir: str = Field(default="./storage", alias="STORAGE_DIR")
    max_upload_size_mb: int = Field(default=500, alias="MAX_UPLOAD_SIZE_MB")
    
    # CORS
    cors_origins: Union[List[str], str] = Field(default=["*"], alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins if passed as a comma-separated string."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return self.cors_origins


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached singleton Settings instance."""
    return Settings()
