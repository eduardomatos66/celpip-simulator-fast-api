"""
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- TiDB ---
    TIDB_HOST: str = "localhost"
    TIDB_PORT: int = 4000
    TIDB_USER: str = "root"
    TIDB_PASSWORD: str = ""
    TIDB_DATABASE: str = "celpip"
    TIDB_SSL_CA: str = ""

    # --- Clerk ---
    CLERK_JWKS_URL: str = ""
    CLERK_AUDIENCE: str = ""

    # --- App ---
    APP_ENV: str = "development"
    APP_CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
