"""HTTP 异常处理器。

这里定义 FastAPI 的异常处理函数，例如业务异常、权限异常、参数异常和未捕获异常的统一转换逻辑。
通常由 `main.py` 调用 `register_exception_handlers()` 统一注册到应用实例上。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from myapp.exceptions import AppError, InternalError, NotFoundError, ValidationError


logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """统一错误响应中的明细项。"""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """统一错误响应模型。"""

    error: ErrorDetail


def build_error_response(code: str, message: str) -> ErrorResponse:
    """构造统一错误响应。"""
    return ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
        )
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """处理应用内可预期的业务异常。"""
    if exc.status_code >= 500:
        logger.error(
            "应用异常",
            extra={
                "error_code": exc.code,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            },
            exc_info=exc,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """处理 FastAPI 请求参数校验异常。"""
    return JSONResponse(
        status_code=ValidationError.status_code,
        content=build_error_response(
            code=ValidationError.code,
            message=str(exc),
        ).model_dump(),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """处理框架层 HTTP 异常，例如路由 404。"""
    if exc.status_code == NotFoundError.status_code:
        return JSONResponse(
            status_code=NotFoundError.status_code,
            content=build_error_response(
                code=NotFoundError.code,
                message="请求的资源不存在。",
            ).model_dump(),
        )

    # 这里处理框架层的其他 HTTP 异常，例如 405、401、403 等。
    # 当前骨架先统一收口为 `http_error`，后续如果前端或网关需要更细粒度的错误码，
    # 再按状态码继续拆分即可。
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            code="http_error",
            message=str(exc.detail),
        ).model_dump(),
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获异常。

    这里先返回统一的内部错误响应。后续可以在这里补日志记录、告警或 Sentry 上报。
    """
    return JSONResponse(
        status_code=InternalError.status_code,
        content=build_error_response(
            code=InternalError.code,
            message=InternalError.message,
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """为应用统一注册异常处理器。"""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)
