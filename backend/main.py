from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from routes import tasks_router
from task_queue import ARQTaskQueue


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup: TaskQueueを初期化してapp.stateに保存
    task_queue = ARQTaskQueue()
    app.state.task_queue = task_queue
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
    return {"status": "ok"}
