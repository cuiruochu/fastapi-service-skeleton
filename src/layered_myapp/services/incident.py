"""incident 业务逻辑。

这里约定使用 Service 类封装 incident 业务逻辑。
Service 负责编排 repository 调用、维护状态流转、触发副作用，并对外提供
`get_incident_service()` 之类的 FastAPI Depends 入口，供 `views.py` 注入使用。
"""

from fastapi import Depends

from layered_myapp.repositories.incident import (
    IncidentRepository,
    get_incident_repository,
)
from layered_myapp.schemas.incident import IncidentCreate, IncidentRead


class IncidentService:
    """incident 业务逻辑服务。"""

    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    async def get(self, incident_id: int) -> IncidentRead:
        """获取单个 incident。"""
        return await self.repository.get(incident_id)

    async def create(self, incident_in: IncidentCreate) -> IncidentRead:
        """创建 incident。"""
        return await self.repository.create(incident_in)


def get_incident_service(
    repository: IncidentRepository = Depends(get_incident_repository),
) -> IncidentService:
    """提供 incident service 的 FastAPI dependency。"""
    return IncidentService(repository=repository)
