"""Redis 客户端初始化。

这里负责创建和管理 Redis 连接池和客户端单实例。
业务代码不要直接在这里之外创建新的 Redis 客户端，统一通过 deps.py 注入使用。
"""

import redis.asyncio as redis

from myapp.config import settings


redis_pool = redis.ConnectionPool.from_url(
    settings.redis.url,
    decode_responses=settings.redis.decode_responses,
    max_connections=settings.redis.max_connections,
    socket_timeout=settings.redis.socket_timeout,
    socket_connect_timeout=settings.redis.socket_connect_timeout,
    health_check_interval=settings.redis.health_check_interval,
)
"""Redis 连接池单实例。

Redis 异步客户端执行命令时，会从这个连接池中借用连接。
显式维护连接池后，连接数、超时、健康检查等参数都可以从配置中统一控制。
"""


redis_client = redis.Redis(connection_pool=redis_pool)
"""Redis 异步客户端单实例。"""


async def close_redis_client() -> None:
    """关闭 Redis 客户端和连接池。"""
    await redis_client.aclose()
    await redis_pool.aclose()
