"""MQ 基础设施异常。

这里放通用 MQ 连接、声明、发布相关的底层异常。
业务模块如果需要把底层异常翻译成更明确的业务异常，可以在自己的 messaging.py 中转换。
"""


class MQError(Exception):
    """MQ 基础设施基础异常。"""


class MQPublishRejectedError(MQError):
    """RabbitMQ 拒绝接收消息。"""

    def __init__(
        self,
        *,
        exchange_name: str | None,
        routing_key: str,
        confirmation: str,
    ) -> None:
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.confirmation = confirmation
        message = (
            "RabbitMQ 拒绝接收消息。"
            f" exchange={exchange_name or '<default>'},"
            f" routing_key={routing_key},"
            f" confirmation={confirmation}"
        )
        super().__init__(message)
