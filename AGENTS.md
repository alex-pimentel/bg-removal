# AGENTS.md — bg-removal

> Monorepo: FastAPI backend + Celery worker + React/Vite frontend.

## Structure

```
apps/api/          — FastAPI app (Python 3.11, pyproject.toml)
worker/            — Celery worker (Python 3.11, pyproject.toml)
apps/web/          — React 19 + Vite + Tailwind v4 (package.json)
docker/            — docker-compose.yml (dev), docker-compose.prod.yml, nginx/
```

Each component has its own dependency file and Dockerfile. Work inside each directory separately.

## Dev commands

```bash
make dev           # docker compose -f docker/docker-compose.yml up
make dev-build     # rebuild + up
make dev-down      # down
make test          # exec api pytest
make lint          # exec api ruff check src/
make clean         # down -v + prune
```

## Architecture

```
POST /api/remove-bg/ → API sends Celery task → Redis broker
                                           → Worker runs rembg, stores result at `result:{task_id}` in Redis
GET  /api/tasks/{id}/status  → reads Celery AsyncResult state
GET  /api/tasks/{id}/result  → reads `result:{task_id}` from Redis, returns image/png
GET  /health                → {"status":"ok"}
```

- API uses `celery_app.send_task("remove_bg", args=[image_bytes])` (producer only, no task definition)
- Worker defines `@celery_app.task(name="remove_bg")` in `worker/src/tasks/remove_bg.py`
- Worker loads task via Celery's `include=["src.tasks.remove_bg"]` parameter, NOT autodiscovery
- Results stored directly in Redis by the worker via `Redis.from_url()`, TTL 1h
- Redis is the only shared state between API and worker

## Celery quirks

- Worker Celery app is in `worker/src/worker.py` with hardcoded `redis://redis:6379/0`
- API Celery app is in `apps/api/src/core/celery_app.py` reading from env
- Both share the same broker/backend URL but are independent app instances
- The worker's `include` parameter is what registers the task — editing `src/tasks/` requires ensuring it's in `include`

## Tailwind v4 (not PostCSS)

- Uses `@tailwindcss/vite` plugin in `vite.config.ts`, no `tailwind.config.js` or `postcss.config.js`
- Stylesheet is one line: `@import "tailwindcss"` in `src/index.css`
- Shadcn UI is NOT yet installed. Run `npx shadcn@latest init` (pick Radix, Slate, CSS variables yes) then `npx shadcn@latest add <component>` inside `apps/web/`

## Linting & types

- Ruff: `line-length=100`, selects `E,F,I,N,W,UP`
- mypy: `strict=true`, `ignore_missing_imports=true`
- Commands: `ruff check src/`, `mypy src/` — must run from `apps/api/` directory

## Tests

- Pytest with `TestClient` in `apps/api/tests/test_api.py`
- Tests run against the FastAPI app directly (no Docker/Redis needed for unit tests)
- Invoke via `make test` or `docker compose ... exec api pytest`

## Performance note

First `rembg` invocation downloads a ~176MB U²-Net model (~55s). Subsequent calls take ~1.6s. The model caches inside the container.

## Docker compose file location

Compose files are in `docker/`, not project root. Context paths use `../` references.

```bash
docker compose -f docker/docker-compose.yml up --build
```

Dev compose mounts source as volumes (hot reload). Prod compose does not.

## API config

All settings via `pydantic-settings` from `apps/api/.env`:
- `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- `MAX_FILE_SIZE` = 10MB
- `CORS_ORIGINS` = localhost:5173, 3000, 8000
- `DEBUG` bool

No authentication layer exists yet. CORS allows any origin in the list.

## Production deploy

- **EasyPanel (VM)**: Deploy API + Worker as separate services. Redis as built-in.
- **CloudFlare Pages**: Frontend builds from `apps/web/`, output `dist/`, env `VITE_API_URL`.
- Frontend reads `import.meta.env.VITE_API_URL || "/api"`. Dev proxy (`/api` → `http://api:8000`) works only in Docker Compose.
- Frontend Dockerfiles: `Dockerfile` (Vite dev), `Dockerfile.prod` (nginx static).
- API `.dockerignore` excludes `.env` — settings come from runtime env vars.
- All compose context paths use `../` relative to `docker/`.

## Common gotchas

- `tests/` volume is mounted in dev compose for `make test` to work.
- Build fails if `COPY .env ./` is in Dockerfile but `.env` is in `.dockerignore`.
- Pip dev deps (`.[dev]`) not in image — install at runtime for lint/test runs.
