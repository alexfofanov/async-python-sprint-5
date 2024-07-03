import logging
from logging import config as logging_config

from pydantic import ConfigDict, IPvAnyAddress
from pydantic_settings import BaseSettings

from src.core.logger import LOGGING


class AppSettings(BaseSettings):
    app_title: str
    project_host: IPvAnyAddress
    project_port: int
    token_size: int
    secret_key: str
    access_token_expire_seconds: int

    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: IPvAnyAddress | str
    db_port: int
    postgres_test_db: str

    minio_root_user: str
    minio_root_password: str
    minio_host: IPvAnyAddress | str
    mino_port: int
    minio_bucket_name: str
    minio_test_bucket_name: str
    minio_url_expires_sec: int
    minio_part_size_byte: int

    redis_host: IPvAnyAddress | str
    redis_port: int

    model_config = ConfigDict(env_file='.env')

    @property
    def dsn(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:'
            f'{self.postgres_password}@{self.db_host}:'
            f'{self.db_port}/{self.postgres_db}'
        )

    @property
    def dsn_test(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:'
            f'{self.postgres_password}@{self.db_host}:'
            f'{self.db_port}/{self.postgres_test_db}'
        )

    @property
    def redis_url(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'

    @property
    def minio_endpoint(self) -> str:
        return f'{self.minio_host}:{self.mino_port}'


app_settings = AppSettings()
logging_config.dictConfig(LOGGING)
logger = logging.getLogger(app_settings.app_title)
