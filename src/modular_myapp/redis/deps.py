"""Redis 依赖注入。

这里负责对外暴露 Redis 客户端的 FastAPI dependency，供 service 或其他基础设施层使用。
简单场景可以直接注入 Redis client 执行命令。
通用 Redis 能力，例如分布式锁、通用限流、通用序列化工具，可以放在 myapp.redis 包内。
业务相关的复杂 Redis 逻辑，例如 case 缓存 key、case 幂等 key、incident 状态缓存，
更适合放在对应业务模块自己的 redis.py 中，避免 myapp.redis 变成业务逻辑大杂烩。
"""

import redis.asyncio as redis

from .client import redis_client


def get_redis_client() -> redis.Redis:
    """提供 Redis 客户端 dependency。"""
    return redis_client
