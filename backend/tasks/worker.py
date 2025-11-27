from typing import Any

from arq.connections import RedisSettings

from config import settings
from database import async_session_factory, init_db
from tasks.handlers import process_simple_task


async def startup(ctx: dict[str, Any]) -> None:
    ctx["session_factory"] = async_session_factory
    await init_db()


async def shutdown(ctx: dict[str, Any]) -> None:
    ctx.pop("session_factory", None)


class WorkerSettings:
    functions = [process_simple_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(str(settings.redis_url))
    queue_name = settings.arq_queue_name
