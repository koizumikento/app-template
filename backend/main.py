from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from config import settings
from routes import task_queue, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup: 特になし（start.shでマイグレーション済み）
    yield
    # shutdown: リソース解放
    await task_queue.close()


app = FastAPI(
    title="App Template Backend",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(tasks_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "env": settings.env}
