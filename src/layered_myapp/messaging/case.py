"""case 模块的 MQ 消息封装。

这里放 case 业务自己的消息发布逻辑，例如消息 DTO、routing key、payload 结构等。
通用 MQ connection、channel 和 producer 仍然由 layered_myapp.mq 提供。
service 层只应该调用这里定义好的业务消息方法，不应该直接拼 MQ routing key 或操作 channel。
"""

import logging

from fastapi import Depends

from layered_myapp.exceptions import MQQueueOverflowError
from layered_myapp.mq.deps import get_mq_producer
from layered_myapp.mq.exceptions import MQPublishRejectedError
from layered_myapp.mq.producer import MQProducer
from layered_myapp.mq.topology import MQQueueTopology
from layered_myapp.schemas.case import CaseCreatedMessage, CaseRead


logger = logging.getLogger(__name__)


CASE_EVENTS_EXCHANGE = "case.events"
"""case 事件 exchange。"""

CASE_CREATED_ROUTING_KEY = "case.created"
"""case 创建消息的 routing key。"""

CASE_CREATED_QUEUE = "case.created.worker"
"""消费 case 创建消息的示例队列名。"""

CASE_EVENTS_DLX = "case.events.dlx"
"""case 事件死信 exchange。"""

CASE_CREATED_DEAD_ROUTING_KEY = "case.created.dead"
"""case 创建消息进入死信队列时使用的 routing key。"""

CASE_CREATED_DEAD_QUEUE = "case.created.dead"
"""case 创建消息的死信队列名。"""

CASE_CREATED_TOPOLOGY = MQQueueTopology(
    exchange=CASE_EVENTS_EXCHANGE,
    routing_key=CASE_CREATED_ROUTING_KEY,
    queue=CASE_CREATED_QUEUE,
    queue_arguments={
        "x-message-ttl": 60000,
        "x-max-length": 10000,
        "x-overflow": "reject-publish",
        "x-dead-letter-exchange": CASE_EVENTS_DLX,
        "x-dead-letter-routing-key": CASE_CREATED_DEAD_ROUTING_KEY,
    },
    dead_letter_exchange=CASE_EVENTS_DLX,
    dead_letter_routing_key=CASE_CREATED_DEAD_ROUTING_KEY,
    dead_letter_queue=CASE_CREATED_DEAD_QUEUE,
)
"""case 创建消息的 RabbitMQ 拓扑配置。"""


def get_case_mq_topologies() -> list[MQQueueTopology]:
    """返回 case 模块需要声明的 MQ 拓扑。"""
    return [CASE_CREATED_TOPOLOGY]


class CaseMessagePublisher:
    """case 模块的消息发布封装。"""

    def __init__(self, mq_producer: MQProducer):
        self.mq_producer = mq_producer

    async def publish_case_created(self, case_data: CaseRead) -> None:
        """发布 case 已创建消息。"""
        message = CaseCreatedMessage(
            case_id=case_data.id,
            title=case_data.title,
        )
        try:
            await self.mq_producer.publish(
                message.model_dump(),
                exchange_name=CASE_EVENTS_EXCHANGE,
                routing_key=CASE_CREATED_ROUTING_KEY,
            )
        except MQPublishRejectedError as exc:
            logger.warning(
                "case 创建消息发布被 RabbitMQ 拒绝",
                extra={
                    "queue": CASE_CREATED_QUEUE,
                    "exchange": CASE_EVENTS_EXCHANGE,
                    "routing_key": CASE_CREATED_ROUTING_KEY,
                    "confirmation": exc.confirmation,
                },
            )
            # 当前队列显式配置了 x-max-length + reject-publish，
            # 因此 RabbitMQ 的发布拒绝可以按“队列已满”来处理。
            if (
                CASE_CREATED_TOPOLOGY.queue_arguments.get("x-overflow") == "reject-publish"
                and "x-max-length" in CASE_CREATED_TOPOLOGY.queue_arguments
            ):
                raise MQQueueOverflowError(
                    message=(
                        f"队列 {CASE_CREATED_QUEUE} 已满，RabbitMQ 拒绝接收新消息。"
                    )
                ) from exc
            raise


def get_case_message_publisher(
    mq_producer: MQProducer = Depends(get_mq_producer),
) -> CaseMessagePublisher:
    """提供 case 消息发布器的 FastAPI dependency。"""
    return CaseMessagePublisher(mq_producer=mq_producer)
