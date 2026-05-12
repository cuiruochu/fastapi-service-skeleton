# myapp skeleton

一个基于 FastAPI 的服务端代码骨架。

当前骨架重点放在这些内容：

- 按业务模块分层组织代码
- 按技术/子系统分层组织代码
- SQLAlchemy 异步数据库访问
- Redis / RabbitMQ 基础设施接入
- 统一异常处理、日志、中间件
- Alembic 迁移目录预留
- 提供两份目录组织对照包

## 目录

```text
src/
  modular_myapp/
    case/
      complex_flow/
    database/
    redis/
    mq/
    main.py

  layered_myapp/
    api/
    services/
    repositories/
    schemas/
    caches/
    messaging/
    subsystems/
      case_subsystem/
        api.py
        service.py
        repository.py
        schemas.py
        messaging.py
    database/
    redis/
    mq/
    main.py
```

## 运行

业务模块分层版本：

```bash
uv sync
uv run uvicorn modular_myapp.main:app --app-dir src --reload
```

技术/子系统分层版本：

```bash
uv run uvicorn layered_myapp.main:app --app-dir src --reload
```

## 说明

这是一个起步骨架，不是完整业务项目。两份代码示例的业务语义尽量保持一致，主要用于对比目录组织方式。

`layered_myapp/subsystems/` 用于表达一种折中方式：项目整体仍然按技术层组织，
但当某个业务能力复杂到不适合继续拆散在顶层目录时，可以在 `subsystems/` 下局部恢复成类似
`modular_myapp/case/` 的模块化结构。
