from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TaskRecord, TaskStatus


class TaskRepository:
    """TaskRecord を操作するリポジトリ。"""

    @staticmethod
    async def create(
        session: AsyncSession, task_id: str, payload: dict[str, Any]
    ) -> TaskRecord:
        record = TaskRecord(id=task_id, payload=payload, status=TaskStatus.QUEUED)
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def mark_running(session: AsyncSession, task_id: str) -> TaskRecord:
        record = await TaskRepository._get(session, task_id)
        record.status = TaskStatus.RUNNING
        record.started_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def mark_succeeded(
        session: AsyncSession, task_id: str, result: dict[str, Any]
    ) -> TaskRecord:
        record = await TaskRepository._get(session, task_id)
        record.status = TaskStatus.SUCCEEDED
        record.result = result
        record.error = None
        record.finished_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def mark_failed(
        session: AsyncSession, task_id: str, error: str
    ) -> TaskRecord:
        record = await TaskRepository._get(session, task_id)
        record.status = TaskStatus.FAILED
        record.error = error
        record.finished_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def get(session: AsyncSession, task_id: str) -> Optional[TaskRecord]:
        statement = select(TaskRecord).where(TaskRecord.id == task_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def _get(session: AsyncSession, task_id: str) -> TaskRecord:
        record = await TaskRepository.get(session, task_id)
        if record is None:
            raise ValueError(f"Task '{task_id}' not found")
        return record
