"""技术分层版顶层 API 路由编排。"""

from fastapi import APIRouter

from layered_myapp.api.case import router as case_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(case_router, prefix="/cases", tags=["case"])


@api_router.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    """健康检查接口。"""
    return {"status": "ok"}
