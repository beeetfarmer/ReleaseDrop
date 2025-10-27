"""
Application configuration using pydantic-settings for environment variable management.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Spotify API Configuration
    spotify_client_id: str
    spotify_client_secret: str

    # Gotify Notification Service
    gotify_url: str = ""
    gotify_token: str = ""

    # Ntfy Notification Service
    ntfy_url: str = ""
    ntfy_topic: str = ""
    ntfy_username: str = ""
    ntfy_password: str = ""

    # Database Configuration
    database_url: str = "sqlite:///./releasedrop.db"

    # Last.fm Integration (Phase 2)
    lastfm_api_key: str = ""
    lastfm_username: str = ""

    # Jellyfin Integration (Phase 2)
    jellyfin_url: str = ""
    jellyfin_api_key: str = ""

    # Plex Integration
    plex_url: str = ""
    plex_token: str = ""

    # Application Settings
    release_check_time: str = "09:00"
    timezone: str = "UTC"
    release_months_back: int = 3

    class Config:
        # In Docker, environment variables are passed via docker-compose
        # For local development, .env is loaded from parent directory
        env_file = "../.env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
