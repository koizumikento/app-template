from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional


class TaskQueue(ABC):
    """非同期タスクを投入するための抽象インターフェース。"""

    @abstractmethod
    async def enqueue(
        self,
        task_name: str,
        payload: Mapping[str, Any],
        *,
        job_id: Optional[str] = None,
    ) -> str:
        """タスクをキューに追加し、タスクIDを返す。"""

    @abstractmethod
    async def close(self) -> None:
        """リソースの開放。"""
