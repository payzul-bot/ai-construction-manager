from __future__ import annotations

from typing import Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None)

    app_env: str = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(alias="DATABASE_URL")

    cors_origins: str = Field(default="", alias="CORS_ORIGINS")
    max_body_bytes: int = Field(default=1_000_000, alias="MAX_BODY_BYTES")

    redis_url: str = Field(alias="REDIS_URL")
    rate_limit_per_minute: int = Field(default=120, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_prefix: str = Field(default="rl", alias="RATE_LIMIT_PREFIX")

    idempotency_prefix: str = Field(default="idem", alias="IDEMPOTENCY_PREFIX")
    idempotency_ttl_sec: int = Field(default=86400, alias="IDEMPOTENCY_TTL_SEC")
    require_idempotency: bool = Field(default=True, alias="REQUIRE_IDEMPOTENCY")

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_issuer: str = Field(default="ai-construction", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="ai-construction-web", alias="JWT_AUDIENCE")

    api_keys: str = Field(default="", alias="API_KEYS")  # "key=tenant_uuid,key2=tenant_uuid2"
    allow_tenant_header_fallback: bool = Field(default=False, alias="ALLOW_TENANT_HEADER_FALLBACK")

    def cors_list(self) -> List[str]:
        if not self.cors_origins.strip():
            return []
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    def api_key_map(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        s = (self.api_keys or "").strip()
        if not s:
            return out
        # "devkey=uuid,another=uuid"
        for pair in s.split(","):
            pair = pair.strip()
            if not pair or "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            out[k.strip()] = v.strip()
        return out


settings = Settings()
