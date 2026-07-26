from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./conference_hub.db"
    redis_url: str = "redis://localhost:6379/0"
    public_base_url: str = "http://localhost:3000"
    newsletter_from_email: str = "radar@example.org"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
