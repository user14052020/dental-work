from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILES = (
    str(PROJECT_ROOT_DIR / ".env"),
    str(BACKEND_DIR / ".env"),
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Dental Lab Platform"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"

    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    database_url: str
    postgres_host: str = "localhost"
    postgres_port: int = 5433

    redis_url: str
    elasticsearch_url: str
    elasticsearch_clients_index: str = "dental_clients"
    elasticsearch_doctors_index: str = "dental_doctors"
    elasticsearch_executors_index: str = "dental_executors"
    elasticsearch_materials_index: str = "dental_materials"
    elasticsearch_operations_index: str = "dental_operations"
    elasticsearch_work_catalog_index: str = "dental_work_catalog"
    elasticsearch_works_index: str = "dental_works"
    cors_origins: str = "http://localhost:3100,http://127.0.0.1:3100"
    background_jobs_enabled: bool = True
    background_job_startup_delay_seconds: int = 15
    background_job_lock_ttl_seconds: int = 600
    search_reindex_interval_seconds: int = 3600
    search_reindex_batch_size: int = 200
    dashboard_cache_refresh_interval_seconds: int = 300
    dashboard_cache_windows: str = "all,7d,30d"

    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    attachments_storage_dir: str = str(PROJECT_ROOT_DIR / "storage" / "work_attachments")
    attachments_public_base_url: str = ""
    attachments_max_size_bytes: int = 2 * 1024 * 1024

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def parsed_dashboard_cache_windows(self) -> list[str]:
        return [window.strip() for window in self.dashboard_cache_windows.split(",") if window.strip()]

    @property
    def attachments_storage_path(self) -> Path:
        return Path(self.attachments_storage_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
