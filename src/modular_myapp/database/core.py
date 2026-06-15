"""数据库引擎和元数据配置。

创建 SQLAlchemy 异步 engine、异步 session 工厂，并放置共享的数据库基础对象。
"""

from sqlalchemy import MetaData
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from modular_myapp.config import settings


# 统一数据库约束和索引的自动命名规则。
# 这里管理的不是 ORM 字段名，而是主键、外键、唯一约束、检查约束、索引这些数据库对象的名字。
# 这样做的目的是让 Alembic 迁移结果更稳定、数据库报错更容易看懂，也避免不同环境生成出不可预测的名字。
# 常见缩写含义：
# - ix: index，索引
# - uq: unique constraint，唯一约束
# - ck: check constraint，检查约束
# - fk: foreign key，外键
# - pk: primary key，主键
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类。"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


connect_args: dict[str, object] = {}
if settings.sql.dialect == "sqlite":
    connect_args["check_same_thread"] = False

engine: AsyncEngine = create_async_engine(
    settings.sql.uri,
    echo=settings.sql.echo,
    pool_pre_ping=settings.sql.pool_pre_ping,
    pool_recycle=settings.sql.pool_recycle,
    pool_size=settings.sql.pool_size,
    max_overflow=settings.sql.max_overflow,
    pool_timeout=settings.sql.pool_timeout,
    connect_args=connect_args,
)


if settings.sql.dialect == "sqlite":
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, connection_record) -> None:
        """在 SQLite 新连接建立时设置 PRAGMA。"""
        cursor = dbapi_connection.cursor()
        try:
            if settings.sql.sqlite_enable_wal:
                cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute(f"PRAGMA busy_timeout={settings.sql.sqlite_busy_timeout_ms};")
        finally:
            cursor.close()

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

DbSession = AsyncSession


async def close_database() -> None:
    """关闭数据库连接池。"""
    await engine.dispose()
