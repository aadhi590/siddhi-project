from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_PLACES_API_KEY: str
    GOOGLE_VISION_API_KEY: str
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: Literal["gemini", "openai"] = "gemini"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    API_KEY: str = ""
    SCAN_RADIUS_METERS: int = 5000
    MAX_RESULTS_PER_SCAN: int = 20
    GOOGLE_PLACES_BASE_URL: str = "https://maps.googleapis.com/maps/api/place"
    GOOGLE_VISION_BASE_URL: str = "https://vision.googleapis.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Returns the cached settings instance."""
    return Settings()
