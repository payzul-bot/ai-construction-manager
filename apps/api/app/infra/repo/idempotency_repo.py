class IdempotencyRepo:
    def __init__(self, redis):
        self.redis = redis

    def exists(self, key: str) -> bool:
        return self.redis.exists(key) == 1

    def mark(self, key: str, ttl: int = 60) -> None:
        self.redis.set(name=key, value="1", ex=ttl)
