"""OpenAI SDK 客户端。

这里复用基础 `http_client` 创建全局单实例 `AsyncOpenAI` 客户端，
这样可以统一复用 HTTP 层的连接池、超时、TLS 和代理配置。
"""

from openai import AsyncOpenAI

from myapp.clients.http import http_client
from myapp.config import settings


openai_client = AsyncOpenAI(
    api_key=settings.openai.api_key,
    base_url=settings.openai.base_url,
    organization=settings.openai.organization,
    project=settings.openai.project,
    http_client=http_client,
)
