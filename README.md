# myapp

一个基于 FastAPI 的服务端代码骨架。

当前骨架重点放在这些内容：

- 按业务模块分层组织代码
- SQLAlchemy 异步数据库访问
- Redis / RabbitMQ 基础设施接入
- 统一异常处理、日志、中间件
- Alembic 迁移目录预留

## 目录

```text
src/myapp/
  case/
  incident/
  database/
  redis/
  mq/
  clients/
  middleware/
  main.py
```

## 运行

```bash
uv sync
uv run uvicorn myapp.main:app --app-dir src --reload
```

## 说明

这是一个起步骨架，不是完整业务项目。
