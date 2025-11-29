from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from config import settings

# モデルをインポートしてメタデータに登録
import models  # noqa: F401


def _create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )


engine: AsyncEngine = _create_engine()
async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db() -> None:
    """SQLModel のテーブルを作成する。"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI の依存性として利用するセッションファクトリ。"""
    async with async_session_factory() as session:
        yield session
