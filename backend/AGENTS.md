# Repository Guidelines

## Project Structure & Module Organization
- `backend/` FastAPI entrypoint `main.py`; configs in `config.py` and `database.py`.
- Domain layers: `models/` (SQLModel tables), `schemas/` (Pydantic v2 I/O), `repositories/`, `services/`.
- `task_queue/` abstraction for enqueuing; async handlers in `tasks/`.
- Tests live in `backend/tests` split into `api/` and `unit/`, sharing fixtures in `conftest.py`.
- `docs/` holds PlantUML diagrams; `frontend/` is a placeholder Dockerfile; `docker-compose.yaml` wires API, worker, Postgres, Redis, and fake GCS.

## Build, Test, and Development Commands
- `cd backend && uv sync --dev` install dependencies.
- `cd backend && uv run uvicorn main:app --reload --port 8000` start the API locally.
- `cd backend && uv run arq tasks.worker.WorkerSettings` run the worker to process queued tasks.
- `docker-compose up --build` (repo root) brings up API, worker, Postgres, Redis, and fake GCS.
- `cd backend && uv run pytest` run all tests; target a subset with `uv run pytest tests/api/test_tasks.py -k scenario`.
- `cd backend && uv run ruff check .` lint the codebase.

## Coding Style & Naming Conventions
- Python 3.12, 4-space indentation, full type hints; snake_case for functions/vars, PascalCase for classes/enums.
- Use Pydantic v2 schemas for I/O; prefer `.model_dump()` and `.model_validate()` helpers.
- Follow service -> repository -> queue/DB layering; inject `AsyncSession` via FastAPI dependencies; enqueue through the TaskQueue interface.

## Testing Guidelines
- pytest with pytest-asyncio auto mode; fixtures `mock_session`, `mock_task_queue`, and `client` in `tests/conftest.py`.
- Name tests `test_*.py`; cover routes, services, and queue behaviors including edge/failure paths.
- Assert async call order/awaits similar to `tests/unit/services/test_task_service.py`.

## Commit & Pull Request Guidelines
- Commit messages are concise and imperative (e.g., "Add task retry logic").
- PRs should explain behavior changes, list test commands run, note env var or migration impacts, and include screenshots for API docs/UI when useful.

## Security & Configuration Tips
- Keep secrets in a local `.env`; configuration comes from env via `config.Settings` (ENV, DATABASE_URL, REDIS_URL, GCS_*, ARQ_QUEUE_NAME).
- Verify DB/Redis targets before running migrations or destructive actions; fake GCS is for local use only; point real buckets carefully and rotate credentials.
