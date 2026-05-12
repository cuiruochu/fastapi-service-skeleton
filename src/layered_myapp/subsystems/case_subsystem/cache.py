"""case 子系统 Redis 封装。

这里适合放当前子系统专用的 Redis key 规则、序列化、反序列化和缓存读写函数。
简单通用 Redis 操作仍然可以直接使用 layered_myapp/redis 提供的 dependency。
"""

