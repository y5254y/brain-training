"""
Alembic 数据库迁移环境配置
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 将后端应用添加到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.core.database import Base

# 导入所有模型以确保它们被注册
from app.models import user, training  # noqa: F401

# Alembic Config 对象
config = context.config

# 从配置文件设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置模型的元数据（用于自动生成迁移脚本）
target_metadata = Base.metadata


def get_url():
    """获取数据库连接 URL"""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """离线模式运行迁移（不需要实际数据库连接）"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式运行迁移（需要实际数据库连接）"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
