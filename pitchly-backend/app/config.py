from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Responsibility: Provide typed environment settings and application constants.
    # ── AI ────────────────────────────────────────
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_storage_bucket: str = Field(
        default="pitchly-videos",
        alias="SUPABASE_STORAGE_BUCKET",
    )
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    cors_origins: str | None = Field(default=None, alias="CORS_ORIGINS")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # ── AI models ─────────────────────────────────
    whisper_model: str = Field(default="small", alias="WHISPER_MODEL")

    # ── Business limits ───────────────────────────
    max_upload_size_bytes: int = Field(default=52_428_800, alias="MAX_UPLOAD_SIZE_BYTES")
    max_session_duration_s: int = Field(default=300, alias="MAX_SESSION_DURATION_S")
    min_confidence_score: int = Field(default=40, alias="MIN_CONFIDENCE_SCORE")
    signed_url_ttl_s: int = Field(default=3600, alias="SIGNED_URL_TTL_S")

    # ── Rate limiting ─────────────────────────────
    auth_rate_limit: str = Field(default="10/minute", alias="AUTH_RATE_LIMIT")
    api_rate_limit: str = Field(default="20/minute", alias="API_RATE_LIMIT")
    polling_interval_ms: int = Field(default=2000, alias="POLLING_INTERVAL_MS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        if self.cors_origins:
            return [
                origin.strip()
                for origin in self.cors_origins.split(",")
                if origin.strip()
            ]
        return [self.frontend_url]


@lru_cache
def get_settings() -> Settings:
    return Settings()
