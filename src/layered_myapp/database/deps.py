"""请求处理中的数据库依赖。

提供 FastAPI dependency 函数，为每个请求提供数据库会话。
"""

from collections.abc import AsyncGenerator

from .core import DbSession, SessionLocal


async def get_db_session() -> AsyncGenerator[DbSession, None]:
    """提供数据库会话的 FastAPI dependency。

    每个请求独立创建一个数据库会话。
    如果请求处理过程中抛出异常，则回滚事务；请求结束后始终关闭会话。
    """
    async with SessionLocal() as db_session:
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise
