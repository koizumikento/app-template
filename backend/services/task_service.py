from typing import Any, Mapping, Optional
from uuid import uuid4

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from models import TaskRecord
from repositories.task_repository import TaskRepository
from task_queue import TaskQueue


class TaskService:
    def __init__(self, queue: TaskQueue) -> None:
        self._queue = queue

    async def enqueue_simple_task(
        self,
        session: AsyncSession,
        payload: Mapping[str, Any],
    ) -> TaskRecord:
        task_id = str(uuid4())
        task_payload = {"task_id": task_id, **payload}

        # 1. 先にDBへキュー投入済みとして登録し整合性を担保する
        record = await TaskRepository.create(session, task_id, dict(task_payload))

        # 2. キュー投入中に例外が発生した場合はFAILEDへ更新して再送出する
        try:
            await self._queue.enqueue(
                "process_simple_task", task_payload, job_id=task_id
            )
        except Exception as exc:
            await TaskRepository.mark_failed(session, task_id, str(exc))
            raise

        return record

    async def get_task(
        self, session: AsyncSession, task_id: str
    ) -> Optional[TaskRecord]:
        return await TaskRepository.get(session, task_id)


def get_task_service(request: Request) -> TaskService:
    """TaskServiceの依存性を提供する。app.stateからTaskQueueを取得。"""
    task_queue: TaskQueue = request.app.state.task_queue
    return TaskService(task_queue)
