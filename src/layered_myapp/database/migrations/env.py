"""Alembic 迁移环境配置。

Alembic 执行 `upgrade`、`downgrade`、`revision --autogenerate` 时会加载这个文件。
这里通常负责读取应用配置、导入 SQLAlchemy metadata，并配置离线/在线迁移上下文。
"""
