"""
Application settings loaded from environment variables.
"""

import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any


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

    # We use Any here to prevent pydantic-settings from trying to parse JSON automatically.
    # Our field_validator handles both comma-separated strings and JSON arrays.
    APP_CORS_ORIGINS: Any = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("APP_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            # If it looks like a JSON array, try loading it
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            # Otherwise, split by comma
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
