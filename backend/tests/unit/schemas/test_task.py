from datetime import datetime

import pytest
from pydantic import ValidationError

from models import TaskRecord, TaskStatus
from schemas import TaskCreateRequest, TaskResponse


def test_task_create_request_defaults() -> None:
    request = TaskCreateRequest()

    assert request.sleep_seconds == 1.0
    assert request.data == {}


def test_task_create_request_invalid_sleep_seconds() -> None:
    with pytest.raises(ValidationError):
        TaskCreateRequest(sleep_seconds=-0.1)


def test_task_response_from_record() -> None:
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    record = TaskRecord(
        id="task-1",
        status=TaskStatus.SUCCEEDED,
        payload={"foo": "bar"},
        result={"value": 42},
        error=None,
        queued_at=base_time,
        started_at=base_time,
        finished_at=base_time,
    )

    response = TaskResponse.from_record(record)

    assert response.id == "task-1"
    assert response.status is TaskStatus.SUCCEEDED
    assert response.payload == {"foo": "bar"}
    assert response.result == {"value": 42}
    assert response.error is None
    assert response.queued_at == base_time
    assert response.started_at == base_time
    assert response.finished_at == base_time
