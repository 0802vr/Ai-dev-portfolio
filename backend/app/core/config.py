from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "AI Developer Portfolio API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"
    database_url: str = "postgresql+asyncpg://portfolio:portfolio@postgres:5432/portfolio"
    cors_origins: str = "http://localhost:3000"
    log_file: str = "logs/api.log"

    ai_provider: str = "gemini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-flash-latest"
    ai_timeout_seconds: float = 8.0

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_from_email: str = "noreply@example.com"
    owner_email: str = "owner@example.com"

    metrics_api_key: str = Field(default="change-me", min_length=8)
    rate_limit_requests: int = 5
    rate_limit_window_seconds: int = 900
    trust_proxy_headers: bool = False

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.lower() == "production":
            if self.metrics_api_key == "change-me":
                raise ValueError("METRICS_API_KEY must be changed in production")
            if not self.allowed_origins or "*" in self.allowed_origins:
                raise ValueError("CORS_ORIGINS must contain explicit origins in production")
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def ai_configured(self) -> bool:
        return self.ai_provider == "gemini" and bool(self.gemini_api_key)

    def client_ip(self, direct_ip: str, forwarded_for: str | None) -> str:
        if self.trust_proxy_headers and forwarded_for:
            return forwarded_for.split(",", maxsplit=1)[0].strip()
        return direct_ip


@lru_cache
def get_settings() -> Settings:
    return Settings()
