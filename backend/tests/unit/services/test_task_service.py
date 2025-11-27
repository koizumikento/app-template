from datetime import datetime
from uuid import UUID

import pytest
from unittest.mock import AsyncMock

from models import TaskRecord, TaskStatus
from services.task_service import TaskService


@pytest.mark.asyncio
async def test_enqueue_simple_task(monkeypatch, mock_session, mock_task_queue) -> None:
    service = TaskService(mock_task_queue)
    payload = {"sleep_seconds": 0.5, "data": {"key": "value"}}
    expected_uuid = UUID("12345678-1234-5678-1234-567812345678")
    base_time = datetime(2024, 1, 1, 12, 0, 0)

    record = TaskRecord(
        id=str(expected_uuid),
        status=TaskStatus.QUEUED,
        payload={"task_id": str(expected_uuid), **payload},
        queued_at=base_time,
    )

    call_order: list[str] = []

    async def create_stub(*args, **kwargs):
        call_order.append("create")
        return record

    async def enqueue_stub(*args, **kwargs):
        call_order.append("enqueue")
        return str(expected_uuid)

    create_mock = AsyncMock(side_effect=create_stub)
    monkeypatch.setattr("services.task_service.uuid4", lambda: expected_uuid)
    monkeypatch.setattr("services.task_service.TaskRepository.create", create_mock)
    mock_task_queue.enqueue.side_effect = enqueue_stub

    result = await service.enqueue_simple_task(mock_session, payload)

    mock_task_queue.enqueue.assert_awaited_once_with(
        "process_simple_task",
        {"task_id": str(expected_uuid), **payload},
        job_id=str(expected_uuid),
    )
    create_mock.assert_awaited_once_with(mock_session, str(expected_uuid), {"task_id": str(expected_uuid), **payload})
    assert call_order == ["create", "enqueue"]
    assert result is record


@pytest.mark.asyncio
async def test_get_task(monkeypatch, mock_session, mock_task_queue) -> None:
    service = TaskService(mock_task_queue)
    expected = TaskRecord(id="task-123", status=TaskStatus.QUEUED)
    get_mock = AsyncMock(return_value=expected)
    monkeypatch.setattr("services.task_service.TaskRepository.get", get_mock)

    result = await service.get_task(mock_session, "task-123")

    get_mock.assert_awaited_once_with(mock_session, "task-123")
    assert result is expected


@pytest.mark.asyncio
async def test_enqueue_simple_task_queue_failure(monkeypatch, mock_session, mock_task_queue) -> None:
    service = TaskService(mock_task_queue)
    payload = {"sleep_seconds": 0.5, "data": {"key": "value"}}
    expected_uuid = UUID("87654321-4321-6789-4321-678987654321")
    record = TaskRecord(
        id=str(expected_uuid),
        status=TaskStatus.QUEUED,
        payload={"task_id": str(expected_uuid), **payload},
    )

    create_mock = AsyncMock(return_value=record)
    mark_failed_mock = AsyncMock(return_value=record)
    monkeypatch.setattr("services.task_service.uuid4", lambda: expected_uuid)
    monkeypatch.setattr("services.task_service.TaskRepository.create", create_mock)
    monkeypatch.setattr("services.task_service.TaskRepository.mark_failed", mark_failed_mock)
    mock_task_queue.enqueue.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await service.enqueue_simple_task(mock_session, payload)

    create_mock.assert_awaited_once_with(mock_session, str(expected_uuid), {"task_id": str(expected_uuid), **payload})
    mock_task_queue.enqueue.assert_awaited_once_with(
        "process_simple_task",
        {"task_id": str(expected_uuid), **payload},
        job_id=str(expected_uuid),
    )
    mark_failed_mock.assert_awaited_once_with(mock_session, str(expected_uuid), "boom")

