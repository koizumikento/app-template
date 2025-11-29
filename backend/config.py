from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション全体で参照する設定値。"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    env: Literal["local", "gcp"] = Field(default="local", alias="ENV")

    redis_url: AnyUrl = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    database_url: str = Field(
        default="postgresql+asyncpg://app:app@postgres:5432/app", alias="DATABASE_URL"
    )

    gcs_endpoint: Optional[str] = Field(
        default="http://fake-gcs:4443", alias="GCS_ENDPOINT"
    )
    gcs_bucket: str = Field(default="app-bucket", alias="GCS_BUCKET")
    gcs_credentials_file: Optional[str] = Field(
        default=None, alias="GCS_CREDENTIALS_FILE"
    )

    arq_queue_name: str = Field(default="app-queue", alias="ARQ_QUEUE_NAME")


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンを返却する。"""
    return Settings()


settings = get_settings()
