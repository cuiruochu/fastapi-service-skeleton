"""case Pydantic schema。

定义 case API 使用的请求体、响应模型、过滤条件和轻量 DTO。
"""

from pydantic import BaseModel


class CaseCreate(BaseModel):
    """创建 case 的请求体。"""

    title: str


class CaseRead(BaseModel):
    """返回给调用方的 case 响应模型。"""

    id: int
    title: str


class CaseCreatedMessage(BaseModel):
    """case 创建消息体。"""

    case_id: int
    title: str
