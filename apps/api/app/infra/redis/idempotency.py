from __future__ import annotations

import json
from typing import Any, Optional, Tuple

from redis import Redis


class IdempotencyStore:
    def __init__(self, redis: Redis, prefix: str, ttl_sec: int):
        self.redis = redis
        self.prefix = prefix
        self.ttl = ttl_sec

    def _key(self, tenant_id: str, idem_key: str) -> str:
        return f"{self.prefix}:{tenant_id}:{idem_key}"

    def get_response(self, tenant_id: str, idem_key: str) -> Optional[Tuple[int, Any]]:
        raw = self.redis.get(self._key(tenant_id, idem_key))
        if not raw:
            return None
        data = json.loads(raw)
        return int(data["status"]), data["body"]

    def set_response(self, tenant_id: str, idem_key: str, status: int, body: Any) -> None:
        payload = json.dumps({"status": status, "body": body}, ensure_ascii=False)
        self.redis.set(self._key(tenant_id, idem_key), payload, ex=self.ttl)

    def lock(self, tenant_id: str, idem_key: str) -> bool:
        # SETNX lock to avoid double work; short TTL lock
        lk = self._key(tenant_id, idem_key) + ":lock"
        return bool(self.redis.set(lk, "1", nx=True, ex=30))
