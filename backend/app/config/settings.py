"""
SatQuery AI - Application Configuration
Reads all settings from environment variables.
"""
from functools import lru_cache
from typing import List, Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "SatQuery AI"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    gemini_vision_model: str = "gemini-3.6-flash"

    # Database — default to SQLite for local development
    database_url: str = "sqlite+aiosqlite:///./satquery_dev.db"
    sync_database_url: str = "sqlite:///./satquery_dev.db"

    # File limits
    max_file_size_mb: int = 2048

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Storage
    upload_dir: str = "./data/uploads"
    processed_dir: str = "./data/processed"
    results_dir: str = "./data/results"
    model_cache_dir: str = "./models/checkpoints"

    # Limits
    max_upload_size: int = 2_147_483_648  # 2 GB
    max_image_dimension: int = 65536

    # Compute
    device: Literal["auto", "cuda", "cpu"] = "auto"

    # Auth
    secret_key: str = "change_me_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # HuggingFace
    hf_token: str = ""
    hf_home: str = "./models/checkpoints"


@lru_cache
def get_settings() -> Settings:
    return Settings()
