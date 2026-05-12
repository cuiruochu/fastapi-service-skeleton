"""incident 持久化操作。

这里约定使用 Repository 类封装数据库查询、创建、更新、删除，以及查询相关辅助逻辑。
同时对外提供 `get_incident_repository()` 之类的 dependency 工厂函数，供 service 层注入使用。
"""

from fastapi import Depends

from modular_myapp.database.core import DbSession
from modular_myapp.database.deps import get_db_session

from .schemas import IncidentCreate, IncidentRead


class IncidentRepository:
    """incident 持久化仓储。"""

    def __init__(self, db_session: DbSession):
        self.db_session = db_session

    async def get(self, incident_id: int) -> IncidentRead:
        """获取单个 incident。"""
        return IncidentRead(id=incident_id, title=f"incident-{incident_id}")

    async def create(self, incident_in: IncidentCreate) -> IncidentRead:
        """创建 incident。"""
        return IncidentRead(id=1, title=incident_in.title)


def get_incident_repository(
    db_session: DbSession = Depends(get_db_session),
) -> IncidentRepository:
    """提供 incident repository 的 dependency 工厂函数。"""
    return IncidentRepository(db_session=db_session)
