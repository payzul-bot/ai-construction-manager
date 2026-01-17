from __future__ import annotations

from typing import List

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- APP ---
    app_name: str = "AI Construction Platform API"
    log_level: str = "INFO"
    max_body_bytes: int = 2_000_000  # 2 MB
    cors: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
        validation_alias=AliasChoices("CORS", "CORS_ORIGINS"),
    )

    # --- AUTH ---
    jwt_secret: str = "dev-secret"
    api_keys: str = "devkey=11111111-1111-1111-1111-111111111111"
    allow_tenant_header_fallback: bool = False
    default_tenant_id: str = "demo"

    # --- DB ---
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    # --- REDIS ---
    redis_url: str = "redis://localhost:6379/0"

    def cors_list(self) -> List[str]:
        items = []
        for x in (self.cors or "").split(","):
            x = x.strip()
            if x:
                items.append(x)
        return items


settings = Settings()
