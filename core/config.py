"""Core configuration management."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/crypto_etl",
        description="PostgreSQL connection string",
        validation_alias="DATABASE_URL"
    )
    
    # Render.com support - use PORT env variable if available
    PORT: int = Field(default=8000, description="Server port")
    
    # API Keys (Both CoinPaprika and CoinGecko free tiers don't require keys)
    coinpaprika_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # ETL Configuration
    etl_schedule_minutes: int = 30
    enable_etl_on_startup: bool = True
    
    # Rate Limiting (requests per minute)
    coinpaprika_rate_limit: int = 10
    coingecko_rate_limit: int = 50
    csv_batch_size: int = 100
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Feature Flags
    enable_schema_drift_detection: bool = True
    enable_failure_injection: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
