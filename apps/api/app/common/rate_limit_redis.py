from __future__ import annotations

import time
from redis import Redis


class RateLimiter:
    def __init__(self, redis: Redis, prefix: str, per_minute: int):
        self.redis = redis
        self.prefix = prefix
        self.per_minute = per_minute

    def check(self, tenant_id: str) -> None:
        # fixed window per minute
        now = int(time.time())
        bucket = now // 60
        key = f"{self.prefix}:{tenant_id}:{bucket}"
        p = self.redis.pipeline()
        p.incr(key, 1)
        p.expire(key, 70)
        count, _ = p.execute()
        if int(count) > self.per_minute:
            raise RuntimeError("rate_limited")
