"""case HTTP 路由。

定义 case 接口的 FastAPI router。这里负责请求解析和响应映射，并通过 Depends
注入 `service.py` 暴露出来的 service 对象，再调用其方法完成业务处理。
"""

from fastapi import APIRouter, Depends

from layered_myapp.schemas.case import CaseCreate, CaseRead
from layered_myapp.services.case import CaseService, get_case_service


router = APIRouter()


@router.get("/{case_id}", response_model=CaseRead)
async def get_case(
    case_id: int,
    service: CaseService = Depends(get_case_service),
) -> CaseRead:
    """获取单个 case。"""
    return await service.get(case_id)


@router.post("", response_model=CaseRead)
async def create_case(
    case_in: CaseCreate,
    service: CaseService = Depends(get_case_service),
) -> CaseRead:
    """创建 case。"""
    return await service.create(case_in)
