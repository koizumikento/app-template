#!/bin/bash
set -e

echo "=== Running migration check ==="

# Alembic が初期化されていれば upgrade、なければ SQLModel で create_all
if [ -f "alembic.ini" ]; then
    echo "Alembic detected. Running migrations..."
    alembic upgrade head
else
    echo "Alembic not initialized. Creating tables via SQLModel..."
    python -c "
import asyncio
from database import engine, init_db
asyncio.run(init_db())
print('Tables created.')
"
fi

echo "=== Starting API server ==="

exec gunicorn main:app \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-2} \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile -
