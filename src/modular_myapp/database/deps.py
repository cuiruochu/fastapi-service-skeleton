"""请求处理中的数据库依赖。

提供 FastAPI dependency 和非 FastAPI 场景下的数据库会话上下文。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from .core import DbSession, SessionLocal


@asynccontextmanager
async def session_scope() -> AsyncGenerator[DbSession, None]:
    """为非 FastAPI 依赖注入场景提供数据库会话上下文。

    适用于 gRPC、后台任务、WebSocket 辅助流程等无法直接使用 FastAPI Depends 的入口。
    """
    async with SessionLocal() as db_session:
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise


async def get_db_session() -> AsyncGenerator[DbSession, None]:
    """为 FastAPI Depends 提供数据库会话。"""
    async with session_scope() as db_session:
        yield db_session
