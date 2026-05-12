"""外部客户端依赖注入。

这里统一对外暴露基础 HTTP 客户端和 OpenAI SDK 客户端的 dependency，
保持与 Redis、MQ 的使用风格一致。
"""

import httpx
from openai import AsyncOpenAI

from .http import http_client
from .openai import openai_client


def get_http_client() -> httpx.AsyncClient:
    """提供基础 HTTP 客户端 dependency。"""
    return http_client


def get_openai_client() -> AsyncOpenAI:
    """提供 OpenAI SDK 客户端 dependency。"""
    return openai_client
