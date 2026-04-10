"""
MySQL 数据库连接模块
使用 SQLAlchemy 同步 session 配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    获取数据库会话（依赖注入函数）
    使用 yield 确保请求结束后关闭连接
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有数据库表（开发/测试使用，生产环境使用 Alembic）"""
    from app.models import user, training, family, achievement, daily_task, cognitive  # noqa: F401
    Base.metadata.create_all(bind=engine)
