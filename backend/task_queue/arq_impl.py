from typing import Any, Mapping, Optional

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from config import settings
from task_queue.interface import TaskQueue


class ARQTaskQueue(TaskQueue):
    """ARQ を利用した TaskQueue 実装。"""

    def __init__(self, redis_dsn: Optional[str] = None, queue_name: Optional[str] = None) -> None:
        redis_url = redis_dsn or str(settings.redis_url)

        self._redis_settings = RedisSettings.from_dsn(redis_url)
        if queue_name or settings.arq_queue_name:
            self._redis_settings.queue_name = queue_name or settings.arq_queue_name

        self._pool: ArqRedis | None = None

    async def _get_pool(self) -> ArqRedis:
        if self._pool is None:
            self._pool = await create_pool(self._redis_settings)
        return self._pool

    async def enqueue(
        self,
        task_name: str,
        payload: Mapping[str, Any],
        *,
        job_id: Optional[str] = None,
    ) -> str:
        redis = await self._get_pool()
        job = await redis.enqueue_job(task_name, payload=payload, _job_id=job_id)
        return job.job_id

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
