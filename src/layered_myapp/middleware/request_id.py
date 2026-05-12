"""request_id 中间件。

这里负责为每个请求提取或生成 request_id，并将其写入上下文和响应头。
日志系统可以从这里维护的上下文中读取 request_id，实现全链路日志关联。
"""

from contextvars import ContextVar
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


REQUEST_ID_HEADER = "X-Request-ID"
request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """从上下文中获取当前 request_id。"""
    return request_id_ctx_var.get()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """为每个请求注入 request_id。"""

    async def dispatch(self, request: Request, call_next):
        existing_request_id = request.headers.get(REQUEST_ID_HEADER)
        request_id = existing_request_id or str(uuid4())

        # 如果请求头里本来没有 X-Request-ID，就补一个，方便后续依赖、日志或下游逻辑统一读取。
        if existing_request_id is None:
            request.scope["headers"].append(
                (REQUEST_ID_HEADER.lower().encode("latin-1"), request_id.encode("latin-1"))
            )

        token = request_id_ctx_var.set(request_id)

        try:
            response = await call_next(request)
        finally:
            request_id_ctx_var.reset(token)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
