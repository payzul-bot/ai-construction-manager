# Web UI (Project Passport + Engine)

## Environment setup

Copy the example environment file and edit values as needed:

```bash
cp .env.local.example .env.local
```

**Required variables**

- `NEXT_PUBLIC_API_BASE` — API base URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_TENANT_ID` — tenant header value (default: `demo`)
- `NEXT_PUBLIC_API_KEY` — optional; required only if the API enforces the Engine V1 key

## Local development (API via Docker)

```bash
cd ../../
docker compose up -d --build

cd apps/web
npm install
npm run dev
```

Open http://localhost:3000

## Local development (API running elsewhere)

```bash
cd apps/web
cp .env.local.example .env.local
# Edit .env.local to point to your API base
npm install
npm run dev
```

## Smoke checks

```bash
cd apps/web
npm run check:api-client
npm run smoke:projects
```
