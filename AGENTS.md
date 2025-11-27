# Repository Guidelines

## Project Structure & Module Organization
- backend/: FastAPI app (`main.py`), configs (`config.py`, `database.py`), domain layers (`models/`, `schemas/`, `repositories/`, `services/`), queue abstraction (`task_queue/`), and async handlers (`tasks/`).
- Tests live in backend/tests with api (router) and unit (services/schemas) suites sharing fixtures in conftest.py.
- docs/: PlantUML diagrams; frontend/: placeholder Dockerfile. docker-compose.yaml wires backend, worker, Postgres, Redis, and fake GCS for local dev.

## Build, Test, and Development Commands
- Install deps: `cd backend && uv sync --dev`.
- Run API locally: `cd backend && uv run uvicorn main:app --reload --port 8000` (Gunicorn via `./start.sh` in containers).
- Run worker: `cd backend && uv run arq tasks.worker.WorkerSettings` (mirrors `./start_worker.sh`).
- Full stack: from repo root `docker-compose up --build` to start API, worker, Postgres, Redis, fake-gcs.
- Tests: `cd backend && uv run pytest` (asyncio auto mode). Target a file: `uv run pytest tests/api/test_tasks.py -k scenario`.
- Lint: `cd backend && uv run ruff check .`.

## Coding Style & Naming Conventions
- Python 3.12 with 4-space indentation and full type hints. snake_case for functions/vars, PascalCase for classes/enums.
- Pydantic v2 models in schemas/ for I/O; SQLModel defines tables; prefer `.model_dump()`/`.model_validate()` helpers.
- Follow service -> repository -> queue/DB layering; use TaskQueue interface for enqueuing and inject AsyncSession via FastAPI dependencies.
- Configuration comes from env via config.Settings (ENV, DATABASE_URL, REDIS_URL, GCS_*, ARQ_QUEUE_NAME); avoid ad-hoc os.environ reads elsewhere.

## Testing Guidelines
- pytest with pytest-asyncio auto mode; rely on AsyncMock/monkeypatch fixtures (mock_session, mock_task_queue, client) from tests/conftest.py.
- Name tests `test_*.py` and assert call order/async awaits as done in tests/unit/services/test_task_service.py.
- Cover new routes, services, and queue behaviors; include happy/edge cases and failure paths.

## Commit & Pull Request Guidelines
- Commit history is minimal; use concise imperative messages (e.g., "Add task retry logic").
- PRs should explain behavior changes, list test commands run, note env var or migration impacts, and include screenshots for API docs/UI if relevant.

## Security & Configuration Tips
- Keep secrets in a local .env; never commit credentials. Verify DATABASE_URL/REDIS_URL targets before running migrations or wiping data.
- Fake GCS is for local use only; point GCS_* env vars to real buckets in controlled environments and rotate credentials responsibly.