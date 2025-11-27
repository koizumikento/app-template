import asyncio
from typing import Any, Mapping

from database import async_session_factory
from repositories.task_repository import TaskRepository


async def process_simple_task(ctx: dict[str, Any], payload: Mapping[str, Any]) -> None:
    """サンプル非同期タスク。sleep 後に結果を保存する。"""

    task_id = payload["task_id"]
    sleep_seconds = float(payload.get("sleep_seconds", 1))
    echo_data = payload.get("data", {})

    async with async_session_factory() as session:
        try:
            await TaskRepository.mark_running(session, task_id)
            await asyncio.sleep(sleep_seconds)
            await TaskRepository.mark_succeeded(
                session,
                task_id,
                {"echo": echo_data, "sleep_seconds": sleep_seconds},
            )
        except Exception as exc:  # pragma: no cover - 例外経路
            await TaskRepository.mark_failed(session, task_id, str(exc))
            raise
