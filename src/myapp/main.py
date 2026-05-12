"""ASGI 应用入口。

创建 FastAPI 应用，注册日志、中间件、异常处理器和顶层路由，
并暴露给 uvicorn 或其他 ASGI 服务器使用的模块级 `app` 对象。
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from myapp.api import api_router
from myapp.clients.http import close_http_client
from myapp.config import settings
from myapp.exception_handlers import register_exception_handlers
from myapp.logging import configure_logging
from myapp.middleware.request_id import RequestIdMiddleware
from myapp.mq.producer import close_mq, connect_mq
from myapp.mq.registry import declare_registered_mq_topologies
from myapp.redis.client import close_redis_client


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期钩子。

    这里适合做应用启动和关闭时的一次性资源管理，例如：
    - 初始化持久化 HTTP 客户端
    - 初始化 MQ 长连接和发布 channel
    - 声明当前服务需要维护的 MQ exchange、queue、binding 和死信队列
    - 关闭 Redis / MQ / HTTP 客户端
    - 注册监控或 tracing
    """
    configure_logging()
    logger.info("应用启动", extra={"app_name": settings.app_name})

    await connect_mq()
    await declare_registered_mq_topologies()

    try:
        yield
    finally:
        await close_http_client()
        await close_redis_client()
        await close_mq()
        logger.info("应用关闭", extra={"app_name": settings.app_name})


def create_app() -> FastAPI:
    """创建并装配 FastAPI 应用。"""
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    app.include_router(api_router)

    media_dir = Path(settings.media.dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        settings.media.url_prefix,
        app=StaticFiles(directory=media_dir),
        name="media",
    )

    return app


app = create_app()
