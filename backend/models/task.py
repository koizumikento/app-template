from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    """タスクのステータス。"""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskRecord(SQLModel, table=True):
    """タスクの状態と結果を保持するテーブル。"""

    __tablename__ = "task_record"

    id: str = Field(primary_key=True, index=True)
    status: TaskStatus = Field(default=TaskStatus.QUEUED, index=True)
    payload: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    result: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    error: Optional[str] = None

    queued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

