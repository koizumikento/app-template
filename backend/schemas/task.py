from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from models import TaskRecord, TaskStatus


class TaskCreateRequest(BaseModel):
    """タスク作成リクエストのスキーマ"""

    sleep_seconds: float = Field(default=1.0, ge=0)
    data: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """タスクレスポンスのスキーマ"""

    id: str
    status: TaskStatus
    payload: Dict[str, Any] | None = None
    result: Dict[str, Any] | None = None
    error: str | None = None
    queued_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_record(cls, record: TaskRecord) -> "TaskResponse":
        return cls.model_validate(record)
