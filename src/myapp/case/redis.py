"""case 模块的 Redis 封装。

这里放 case 业务自己的 Redis 逻辑，例如 case 缓存 key、ttl、序列化、幂等 key 等。
通用 Redis 连接池和客户端仍然由 myapp.redis 提供，这里只关心 case 模块自己的缓存规则。
Redis 缓存值优先复用本模块 schemas.py 中已有的 Pydantic schema 做序列化和反序列化。
如果缓存结构和 API 入参/响应不一致，可以在 schemas.py 中定义专门的 DTO，例如 CaseCache。
不建议为了 Redis 单独维护一套类似 ORM 的 Redis model，避免模型层级过早复杂化。
"""

import json

from fastapi import Depends
import redis.asyncio as redis

from myapp.redis.deps import get_redis_client

from .schemas import CaseRead


class CaseRedis:
    """case 模块的 Redis 操作封装。"""

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def _case_key(self, case_id: int) -> str:
        """生成 case 详情缓存 key。"""
        return f"case:{case_id}"

    async def get_case(self, case_id: int) -> CaseRead | None:
        """读取 case 详情缓存。"""
        raw_value = await self.redis_client.get(self._case_key(case_id))
        if raw_value is None:
            return None

        return CaseRead.model_validate_json(raw_value)

    async def set_case(self, case_data: CaseRead, *, ttl_seconds: int = 300) -> None:
        """写入 case 详情缓存。"""
        await self.redis_client.set(
            self._case_key(case_data.id),
            case_data.model_dump_json(),
            ex=ttl_seconds,
        )

    async def delete_case(self, case_id: int) -> None:
        """删除 case 详情缓存。"""
        await self.redis_client.delete(self._case_key(case_id))

    async def set_create_idempotency_key(
        self,
        request_id: str,
        *,
        ttl_seconds: int = 300,
    ) -> bool:
        """记录创建 case 的幂等 key。

        返回 True 表示这次成功写入，返回 False 表示同一个 request_id 已经处理过。
        """
        return bool(
            await self.redis_client.set(
                f"case:create:idempotency:{request_id}",
                json.dumps({"request_id": request_id}, ensure_ascii=False),
                ex=ttl_seconds,
                nx=True,
            )
        )


def get_case_redis(
    redis_client: redis.Redis = Depends(get_redis_client),
) -> CaseRedis:
    """提供 case Redis 封装的 FastAPI dependency。"""
    return CaseRedis(redis_client=redis_client)
