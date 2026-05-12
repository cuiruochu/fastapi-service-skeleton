"""消息队列依赖注入。

这里负责对外暴露 MQ producer 的 FastAPI dependency，供 service 层发布领域事件或异步任务消息。
service 层只应该表达“发布什么业务消息”，不应该直接操作 MQ connection、channel、exchange 或 queue。
所有 MQ 连接、channel、拓扑声明、序列化、routing key 等细节，都应该收敛在 myapp.mq 包内。
如果某个业务模块有复杂消息逻辑，可以像 case/messaging.py 一样，在业务模块内封装消息 DTO 和发布方法。
"""

from .producer import MQProducer, mq_producer


def get_mq_producer() -> MQProducer:
    """提供 MQ producer dependency。"""
    return mq_producer
