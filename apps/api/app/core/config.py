from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(value: str) -> str:
    """Select psycopg v3 for Render-style PostgreSQL connection strings."""
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


class Settings(BaseSettings):
    database_url: str = "sqlite:///./conference_hub.db"
    redis_url: str = "redis://localhost:6379/0"
    public_base_url: str = "http://localhost:3000"
    newsletter_from_email: str = "radar@example.org"
    seed_on_startup: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_database_url(value)
        return value


settings = Settings()
