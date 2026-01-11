# AI Construction Manager Platform (v1.0)

Production-grade skeleton:
- Clean architecture: contracts / usecases / infra / api
- Multi-tenant runtime tables (tenant_id)
- Concurrency-safe versioning (SELECT FOR UPDATE + current_version_no)
- Redis-backed rate limiting (multi-instance safe)
- Redis-backed idempotency (multi-instance safe, TTL)
- JWT auth (Bearer), with optional API-key fallback
- Unit-of-work transactions (commit/rollback per request)
- Request ID via contextvars, structured logs
- Body size limit
- CI: ruff + mypy + pytest

## Run
```bash
docker-compose up --build
