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
    CLERK_ISSUER_URL: str = ""
    CLERK_WEBHOOK_SECRET: str = ""
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_KEY: str = ""

    # --- Redis ---
    REDIS_ENABLED: bool = True
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- App ---
    APP_ENV: str = "development"
    APP_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
