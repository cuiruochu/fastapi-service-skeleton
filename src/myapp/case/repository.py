"""case 持久化操作。

这里约定使用 Repository 类封装数据库查询、创建、更新、删除，以及查询相关辅助逻辑。
同时对外提供 `get_case_repository()` 之类的 dependency 工厂函数，供 service 层注入使用。
"""

from fastapi import Depends

from myapp.database.core import DbSession
from myapp.database.deps import get_db_session

from .schemas import CaseCreate, CaseRead


class CaseRepository:
    """case 持久化仓储。"""

    def __init__(self, db_session: DbSession):
        self.db_session = db_session

    async def get(self, case_id: int) -> CaseRead:
        """获取单个 case。"""
        return CaseRead(id=case_id, title=f"case-{case_id}")

    async def create(self, case_in: CaseCreate) -> CaseRead:
        """创建 case。"""
        return CaseRead(id=1, title=case_in.title)


def get_case_repository(
    db_session: DbSession = Depends(get_db_session),
) -> CaseRepository:
    """提供 case repository 的 dependency 工厂函数。"""
    return CaseRepository(db_session=db_session)
