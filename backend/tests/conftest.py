from collections.abc import AsyncIterator
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from database import get_session
from main import app
from services.task_service import TaskService
from task_queue import TaskQueue


@pytest.fixture
def mock_session() -> MagicMock:
    """AsyncSession を模したモック。"""

    session = MagicMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_task_queue() -> MagicMock:
    """TaskQueue のモック。"""

    queue = MagicMock(spec=TaskQueue)
    queue.enqueue = AsyncMock()
    queue.close = AsyncMock()
    return queue


@pytest.fixture
def task_service(mock_task_queue: MagicMock) -> TaskService:
    """モックキューを注入した TaskService。"""

    return TaskService(mock_task_queue)  # type: ignore[arg-type]


@pytest.fixture
def client(
    mock_session: MagicMock, mock_task_queue: MagicMock
) -> Generator[TestClient, None, None]:
    """依存関係をモック化した TestClient。"""

    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        yield mock_session  # type: ignore[misc]

    # app.state.task_queue をモックで設定
    app.state.task_queue = mock_task_queue

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)
