"""RabbitMQ 拓扑声明。

这里放通用的 exchange、queue、binding、dead letter exchange/dead letter queue 声明能力。
本文件不 import 任何业务模块，避免 myapp.mq 反向依赖 case、incident 等业务包。

推荐做法：
- 业务模块在自己的 messaging.py 中定义消息常量和 MQQueueTopology。
- main.py 这种组合入口按需收集业务模块的 topology，并传给 declare_mq_topology()。
- 普通 service 不直接声明 MQ 拓扑，也不直接操作 connection、channel、exchange 或 queue。
"""

from collections.abc import Iterable
from dataclasses import dataclass, field

import aio_pika

from myapp.mq.producer import get_mq_channel


@dataclass(frozen=True)
class MQQueueTopology:
    """一个业务队列及其死信队列的拓扑配置。"""

    exchange: str
    routing_key: str
    queue: str
    exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.TOPIC
    durable: bool = True
    queue_arguments: dict[str, object] = field(default_factory=dict)
    """RabbitMQ 队列原生参数。

    例如：
    - x-message-ttl: 队列内消息的存活时间，单位毫秒
    - x-max-length: 队列允许保留的最大消息数
    - x-overflow: 队列满了以后的策略，例如 reject-publish

    死信配置也可以直接写成 x-dead-letter-exchange / x-dead-letter-routing-key，
    但当前骨架更推荐使用下面的 dead_letter_exchange / dead_letter_routing_key 字段，
    declare_queue_topology() 会把它们写回 RabbitMQ 队列参数中。
    """
    dead_letter_exchange: str | None = None
    dead_letter_routing_key: str | None = None
    dead_letter_queue: str | None = None


async def declare_queue_topology(topology: MQQueueTopology) -> None:
    """声明一个队列及其可选的死信队列。"""
    channel = await get_mq_channel()

    exchange = await channel.declare_exchange(
        topology.exchange,
        type=topology.exchange_type,
        durable=topology.durable,
    )

    queue_arguments = dict(topology.queue_arguments)
    dead_letter_exchange = None

    if topology.dead_letter_exchange:
        dead_letter_exchange = await channel.declare_exchange(
            topology.dead_letter_exchange,
            type=topology.exchange_type,
            durable=topology.durable,
        )
        queue_arguments["x-dead-letter-exchange"] = topology.dead_letter_exchange

    if topology.dead_letter_routing_key:
        queue_arguments["x-dead-letter-routing-key"] = topology.dead_letter_routing_key

    queue = await channel.declare_queue(
        topology.queue,
        durable=topology.durable,
        arguments=queue_arguments or None,
    )
    await queue.bind(exchange, routing_key=topology.routing_key)

    if (
        dead_letter_exchange is not None
        and topology.dead_letter_queue
        and topology.dead_letter_routing_key
    ):
        dead_letter_queue = await channel.declare_queue(
            topology.dead_letter_queue,
            durable=topology.durable,
        )
        await dead_letter_queue.bind(
            dead_letter_exchange,
            routing_key=topology.dead_letter_routing_key,
        )


async def declare_mq_topology(topologies: Iterable[MQQueueTopology]) -> None:
    """声明当前服务需要维护的 MQ 拓扑。"""
    for topology in topologies:
        await declare_queue_topology(topology)
