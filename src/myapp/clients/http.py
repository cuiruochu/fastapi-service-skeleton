"""基础 HTTP 客户端。

这里放持久化的通用 HTTP 客户端初始化，例如 httpx.AsyncClient 的创建、超时、重试、连接池配置等。
其他具体外部系统客户端可以复用这里的基础能力。
"""

import httpx

from myapp.config import settings


http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(settings.http.timeout),
    limits=httpx.Limits(
        max_connections=settings.http.max_connections,
        max_keepalive_connections=settings.http.max_keepalive_connections,
    ),
    verify=settings.http.verify_ssl,
    follow_redirects=settings.http.follow_redirects,
)
"""基础 HTTP 客户端单实例。"""


async def close_http_client() -> None:
    """关闭基础 HTTP 客户端。

    OpenAI SDK 客户端复用了这个 http_client，所以这里统一关闭一次即可。
    """
    await http_client.aclose()
