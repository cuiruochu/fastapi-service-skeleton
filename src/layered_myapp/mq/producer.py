"""消息生产者封装。

这里负责封装 MQ 的连接和消息发送逻辑，例如 exchange、routing key、消息序列化和重试策略。
当前服务只负责生产消息，不在这里放 consumer。
"""

import asyncio
import json

import aio_pika
import pamqp.commands

from layered_myapp.config import settings
from layered_myapp.mq.exceptions import MQPublishRejectedError


class MQProducer:
    """RabbitMQ 消息生产者。"""

    async def publish(
        self,
        payload: dict,
        *,
        exchange_name: str | None = None,
        exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.TOPIC,
        routing_key: str | None = None,
    ) -> None:
        """发布一条 JSON 消息。"""
        channel = await get_mq_channel()
        exchange = channel.default_exchange
        if exchange_name:
            exchange = await channel.declare_exchange(
                exchange_name,
                type=exchange_type,
                durable=True,
            )

        message = aio_pika.Message(
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
        )
        resolved_routing_key = routing_key or settings.mq.default_routing_key
        result = await exchange.publish(
            message,
            routing_key=resolved_routing_key,
        )
        if isinstance(result, (pamqp.commands.Basic.Nack, pamqp.commands.Basic.Reject)):
            raise MQPublishRejectedError(
                exchange_name=exchange_name,
                routing_key=resolved_routing_key,
                confirmation=type(result).__name__,
            )


mq_connection: aio_pika.abc.AbstractRobustConnection | None = None
"""RabbitMQ 长连接单实例。

RabbitMQ 连接需要异步建立，所以不能像 SQLAlchemy engine 那样在 import 时直接创建。
应用启动时通过 connect_mq() 建立连接，关闭时通过 close_mq() 释放连接。
"""

mq_channel: aio_pika.abc.AbstractRobustChannel | None = None
"""RabbitMQ channel 单实例。

RabbitMQ connection 是 TCP 长连接，channel 是同一条连接上的逻辑通道。
生产者复用一个发布 channel，避免每次 publish 都创建和关闭 channel。
"""

_mq_lock = asyncio.Lock()

mq_producer = MQProducer()
"""MQ producer 单实例。"""


async def connect_mq() -> None:
    """建立 RabbitMQ 长连接和发布 channel。"""
    global mq_connection, mq_channel

    if (
        mq_connection is None
        or mq_connection.is_closed
        or mq_channel is None
        or mq_channel.is_closed
    ):
        async with _mq_lock:
            if mq_connection is None or mq_connection.is_closed:
                mq_connection = await aio_pika.connect_robust(settings.mq.url)
                mq_channel = None

            if mq_channel is None or mq_channel.is_closed:
                mq_channel = await mq_connection.channel()


async def get_mq_channel() -> aio_pika.abc.AbstractRobustChannel:
    """获取 RabbitMQ 发布 channel 单实例。"""
    await connect_mq()

    if mq_channel is None:
        raise RuntimeError("MQ channel 初始化失败。")

    return mq_channel


async def close_mq() -> None:
    """关闭 MQ channel 和底层长连接。"""
    global mq_connection, mq_channel

    if mq_channel is not None and not mq_channel.is_closed:
        await mq_channel.close()

    if mq_connection is not None and not mq_connection.is_closed:
        await mq_connection.close()

    mq_channel = None
    mq_connection = None

