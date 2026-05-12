"""incident Pydantic schema。

定义 incident API 使用的请求体、响应模型、过滤条件和轻量 DTO。
"""

from pydantic import BaseModel


class IncidentCreate(BaseModel):
    """创建 incident 的请求体。"""

    title: str


class IncidentRead(BaseModel):
    """返回给调用方的 incident 响应模型。"""

    id: int
    title: str
