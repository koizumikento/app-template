from datetime import datetime
from types import SimpleNamespace

from fastapi import status
from unittest.mock import AsyncMock

from models import TaskRecord, TaskStatus


def _build_task_record(task_id: str = "task-1") -> TaskRecord:
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    return TaskRecord(
        id=task_id,
        status=TaskStatus.QUEUED,
        payload={"task_id": task_id},
        result=None,
        error=None,
        queued_at=base_time,
        started_at=None,
        finished_at=None,
    )


def test_enqueue_task_returns_accepted(client, mock_session, monkeypatch) -> None:
    record = _build_task_record()
    fake_service = SimpleNamespace(
        enqueue_simple_task=AsyncMock(return_value=record),
    )
    monkeypatch.setattr("routes.tasks.task_service", fake_service)

    response = client.post("/tasks/", json={"sleep_seconds": 1.5, "data": {"a": 1}})

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "id": "task-1",
        "status": "queued",
        "payload": {"task_id": "task-1"},
        "result": None,
        "error": None,
        "queued_at": record.queued_at.isoformat(),
        "started_at": None,
        "finished_at": None,
    }
    fake_service.enqueue_simple_task.assert_awaited_once_with(
        mock_session,
        {"sleep_seconds": 1.5, "data": {"a": 1}},
    )


def test_get_task_returns_task_response(client, mock_session, monkeypatch) -> None:
    record = _build_task_record("task-42")
    fake_service = SimpleNamespace(get_task=AsyncMock(return_value=record))
    monkeypatch.setattr("routes.tasks.task_service", fake_service)

    response = client.get("/tasks/task-42")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "task-42"
    fake_service.get_task.assert_awaited_once_with(mock_session, "task-42")


def test_get_task_not_found_returns_404(client, mock_session, monkeypatch) -> None:
    fake_service = SimpleNamespace(get_task=AsyncMock(return_value=None))
    monkeypatch.setattr("routes.tasks.task_service", fake_service)

    response = client.get("/tasks/missing")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task not found"}
    fake_service.get_task.assert_awaited_once_with(mock_session, "missing")

