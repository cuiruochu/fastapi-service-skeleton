"""应用级异常类型定义。

这里定义可复用的业务异常和应用异常。
每个异常类自己维护 `code`、`message` 和 `status_code`，HTTP 层的异常处理器可以直接读取这些属性，
把错误统一转换成 `api.py` 中约定的错误响应格式。
"""

from fastapi import status


class AppError(Exception):
    """应用基础异常。

    所有可预期的业务异常都可以继承这个类型。
    外部抛出异常时通常只需要按需覆盖 message。
    """

    code = "app_error"
    message = "应用错误。"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(AppError):
    """资源不存在异常。"""

    code = "resource_not_found"
    message = "资源不存在。"
    status_code = status.HTTP_404_NOT_FOUND


class PermissionDeniedError(AppError):
    """无权限异常。"""

    code = "permission_denied"
    message = "没有权限执行当前操作。"
    status_code = status.HTTP_403_FORBIDDEN


class ValidationError(AppError):
    """业务参数校验异常。"""

    code = "validation_error"
    message = "请求参数不合法。"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InternalError(AppError):
    """内部错误异常。"""

    code = "internal_error"
    message = "服务内部错误。"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class MQQueueOverflowError(AppError):
    """MQ 队列已满异常。"""

    code = "mq_queue_overflow"
    message = "消息队列已满，请稍后重试。"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class CaseNotFoundError(NotFoundError):
    """case 不存在异常。"""

    code = "case_not_found"
    message = "case 不存在。"


class IncidentNotFoundError(NotFoundError):
    """incident 不存在异常。"""

    code = "incident_not_found"
    message = "incident 不存在。"
