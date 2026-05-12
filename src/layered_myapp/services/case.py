"""case 业务逻辑。

这里约定使用 Service 类封装 case 业务逻辑。
Service 负责编排 repository 调用、维护状态流转、触发副作用，并对外提供
`get_case_service()` 之类的 FastAPI Depends 入口，供 `views.py` 注入使用。
"""

from fastapi import Depends

from layered_myapp.caches.case import CaseRedis, get_case_redis
from layered_myapp.messaging.case import (
    CaseMessagePublisher,
    get_case_message_publisher,
)
from layered_myapp.repositories.case import CaseRepository, get_case_repository
from layered_myapp.schemas.case import CaseCreate, CaseRead


class CaseService:
    """case 业务逻辑服务。"""

    def __init__(
        self,
        repository: CaseRepository,
        case_redis: CaseRedis,
        message_publisher: CaseMessagePublisher,
    ):
        self.repository = repository
        self.case_redis = case_redis
        self.message_publisher = message_publisher

    async def get(self, case_id: int) -> CaseRead:
        """获取单个 case。"""
        cached_case = await self.case_redis.get_case(case_id)
        if cached_case:
            return cached_case

        case_data = await self.repository.get(case_id)
        await self.case_redis.set_case(case_data)
        return case_data

    async def create(self, case_in: CaseCreate) -> CaseRead:
        """创建 case。"""
        case_data = await self.repository.create(case_in)
        await self.case_redis.set_case(case_data)
        await self.message_publisher.publish_case_created(case_data)
        return case_data


def get_case_service(
    repository: CaseRepository = Depends(get_case_repository),
    case_redis: CaseRedis = Depends(get_case_redis),
    message_publisher: CaseMessagePublisher = Depends(get_case_message_publisher),
) -> CaseService:
    """提供 case service 的 FastAPI dependency。"""
    return CaseService(
        repository=repository,
        case_redis=case_redis,
        message_publisher=message_publisher,
    )
