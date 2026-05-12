"""incident HTTP 路由。

定义 incident 接口的 FastAPI router。这里负责请求解析和响应映射，并通过 Depends
注入 `service.py` 暴露出来的 service 对象，再调用其方法完成业务处理。
"""

from fastapi import APIRouter, Depends

from .schemas import IncidentCreate, IncidentRead
from .service import IncidentService, get_incident_service


router = APIRouter()


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(
    incident_id: int,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentRead:
    """获取单个 incident。"""
    return await service.get(incident_id)


@router.post("", response_model=IncidentRead)
async def create_incident(
    incident_in: IncidentCreate,
    service: IncidentService = Depends(get_incident_service),
) -> IncidentRead:
    """创建 incident。"""
    return await service.create(incident_in)
