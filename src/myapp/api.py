"""顶层 API 路由编排。

这个文件负责导入各个业务模块的 router，并按公开 URL 前缀统一挂载。
如果后续需要统一 API 版本前缀、公共 tags、根级路由或系统级接口，也可以在这里集中处理。

具体接口实现仍然保留在每个业务模块自己的 `views.py` 中。
"""

from fastapi import APIRouter

from myapp.case.views import router as case_router
from myapp.incident.views import router as incident_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(case_router, prefix="/cases", tags=["case"])
api_router.include_router(incident_router, prefix="/incidents", tags=["incident"])


@api_router.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    """健康检查接口。"""
    return {"status": "ok"}
