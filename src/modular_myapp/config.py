"""应用配置。

使用 pydantic-settings 从环境变量或 .env 文件读取配置。
对应用其他部分暴露类型化的全局 settings 对象。
"""

from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SQLSettings(BaseSettings):
    """SQLAlchemy 数据库配置。"""

    model_config = SettingsConfigDict(
        env_prefix="SQL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sqlalchemy_database_uri: str | None = None
    dialect: str = "postgresql"
    driver: str | None = "asyncpg"
    host: str = "127.0.0.1"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "myapp"
    echo: bool = False
    pool_pre_ping: bool = True
    pool_recycle: int = 1800
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    sqlite_enable_wal: bool = True
    sqlite_busy_timeout_ms: int = 5000

    @computed_field
    @property
    def uri(self) -> str:
        """返回最终使用的 SQLAlchemy 连接串。"""
        if self.sqlalchemy_database_uri:
            return self.sqlalchemy_database_uri

        if self.dialect == "sqlite":
            if self.database == ":memory:":
                return "sqlite+aiosqlite:///:memory:"
            return f"sqlite+aiosqlite:///{self.database}"

        driver_part = f"+{self.driver}" if self.driver else ""
        encoded_password = quote_plus(self.password)
        return (
            f"{self.dialect}{driver_part}://"
            f"{self.user}:{encoded_password}@{self.host}:{self.port}/{self.database}"
        )


class LoggingSettings(BaseSettings):
    """日志配置。"""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dir: str = "logs"
    file: str = "myapp.log"
    level: str = "INFO"
    logger_name: str = "modular_myapp"
    rotate_every_days: int = 10
    backup_count: int = 12


class MediaSettings(BaseSettings):
    """媒体文件配置。"""

    model_config = SettingsConfigDict(
        env_prefix="MEDIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dir: str = "media"
    url_prefix: str = "/media"
    public_base_url: str | None = None


class RedisSettings(BaseSettings):
    """Redis 配置。"""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = "redis://127.0.0.1:6379/0"
    decode_responses: bool = True
    max_connections: int = 100
    socket_timeout: float | None = 5.0
    socket_connect_timeout: float | None = 5.0
    health_check_interval: int = 30


class MQSettings(BaseSettings):
    """RabbitMQ 配置。"""

    model_config = SettingsConfigDict(
        env_prefix="MQ_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = "amqp://guest:guest@127.0.0.1:5672/"
    default_exchange: str = ""
    default_routing_key: str = ""


class HTTPClientSettings(BaseSettings):
    """基础 HTTP 客户端配置。"""

    model_config = SettingsConfigDict(
        env_prefix="HTTP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    timeout: float = 10.0
    max_connections: int = 100
    max_keepalive_connections: int = 20
    verify_ssl: bool = True
    follow_redirects: bool = False


class OpenAISettings(BaseSettings):
    """OpenAI SDK 配置。"""

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str | None = None
    base_url: str | None = None
    organization: str | None = None
    project: str | None = None


class Settings(BaseSettings):
    """应用总配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "myapp"
    sql: SQLSettings = SQLSettings()
    logging: LoggingSettings = LoggingSettings()
    media: MediaSettings = MediaSettings()
    redis: RedisSettings = RedisSettings()
    mq: MQSettings = MQSettings()
    http: HTTPClientSettings = HTTPClientSettings()
    openai: OpenAISettings = OpenAISettings()


settings = Settings()
