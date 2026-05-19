"""日志配置。

这里提供应用自身的日志配置，不主动接管 FastAPI、uvicorn、httpx 等第三方 logger。
日志同时输出到控制台和按固定周期轮转的文件，并支持通过 `logger.info(..., extra={...})`
附加结构化字段。

业务模块中建议统一使用：

    import logging
    logger = logging.getLogger(__name__)

只要模块路径位于 `myapp` 包下，就会自动挂到当前配置的父 logger 下。
"""

import json
import logging
import logging.config
from dataclasses import dataclass
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path

from modular_myapp.config import settings
from modular_myapp.middleware.request_id import get_request_id


# 这些是 logging.LogRecord 的内建字段名。
# extra 里只保留非内建字段，用于做结构化输出。
RESERVED_LOG_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


class ExtraFieldsFilter(logging.Filter):
    """从 LogRecord 中提取 extra 字段，并自动注入 request_id。"""

    def filter(self, record: logging.LogRecord) -> bool:
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in RESERVED_LOG_RECORD_ATTRS and not key.startswith("_"):
                extra_fields[key] = value

        request_id = get_request_id()
        if request_id is not None and "request_id" not in extra_fields:
            extra_fields["request_id"] = request_id

        record.extra_fields = extra_fields
        return True


class StructuredFormatter(logging.Formatter):
    """支持 extra 字段输出的格式化器。"""

    def format(self, record: logging.LogRecord) -> str:
        base_message = super().format(record)
        extra_fields = getattr(record, "extra_fields", {})
        if not extra_fields:
            return base_message

        try:
            extra_text = json.dumps(extra_fields, ensure_ascii=False, default=str)
        except TypeError:
            extra_text = str(extra_fields)

        return f"{base_message} | extra={extra_text}"


@dataclass
class LoggingRuntime:
    """运行中的异步日志组件。"""

    logger: logging.Logger
    listener: QueueListener
    _started: bool = False

    def start(self) -> None:
        if self._started:
            return
        self.listener.start()
        self._started = True

    def stop(self) -> None:
        if self._started:
            self.listener.stop()
            self._started = False
        for handler in self.listener.handlers:
            handler.close()


_logging_runtime: LoggingRuntime | None = None


def configure_logging(
    *,
    log_dir: Path | str | None = None,
    log_file: str | None = None,
    level: int | str | None = None,
) -> LoggingRuntime:
    """配置应用自身日志。

    约定：
    - 只配置应用父 logger，不主动修改第三方 logger
    - 应用 logger 只写入队列，由后台 listener 写控制台和文件
    - 控制台和文件双输出
    - 文件每 10 天轮转归档，保留历史日志
    - 支持 `extra={...}` 结构化字段输出
    """
    global _logging_runtime

    if _logging_runtime is not None:
        _logging_runtime.stop()
        _logging_runtime = None

    resolved_log_dir = Path(log_dir or settings.logging.dir)
    resolved_log_file = log_file or settings.logging.file
    resolved_level = level or settings.logging.level
    resolved_logger_name = settings.logging.logger_name
    resolved_backup_count = settings.logging.backup_count
    resolved_rotate_every_days = settings.logging.rotate_every_days

    if isinstance(resolved_level, str):
        resolved_level = resolved_level.upper()
        resolved_level = logging.getLevelName(resolved_level)
        if not isinstance(resolved_level, int):
            resolved_level = logging.INFO

    resolved_log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_log_dir / resolved_log_file

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "()": StructuredFormatter,
                    "fmt": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "filters": {
                "extra_fields": {
                    "()": ExtraFieldsFilter,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": resolved_level,
                    "formatter": "structured",
                },
                "file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "level": resolved_level,
                    "formatter": "structured",
                    "filename": str(log_file_path),
                    "when": "MIDNIGHT",
                    "interval": resolved_rotate_every_days,
                    "backupCount": resolved_backup_count,
                    "encoding": "utf-8",
                },
                "queue": {
                    "class": "logging.handlers.QueueHandler",
                    "level": resolved_level,
                    "queue": "queue.Queue",
                    "handlers": ["console", "file"],
                    "filters": ["extra_fields"],
                    "respect_handler_level": True,
                },
            },
            "loggers": {
                resolved_logger_name: {
                    "level": resolved_level,
                    "handlers": ["queue"],
                    "propagate": False,
                }
            },
        }
    )

    logger = logging.getLogger(resolved_logger_name)
    queue_handler = next(handler for handler in logger.handlers if isinstance(handler, QueueHandler))
    listener = queue_handler.listener
    if listener is None:
        raise RuntimeError("QueueHandler listener was not configured")

    _logging_runtime = LoggingRuntime(logger=logger, listener=listener)
    _logging_runtime.start()
    return _logging_runtime
