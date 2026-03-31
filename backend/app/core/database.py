"""
MySQL 数据库连接模块
使用 SQLAlchemy 同步 session 配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建数据库引擎（使用 pymysql 驱动连接 MySQL）
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # 每次使用连接前检查连接是否有效
    pool_size=10,                 # 连接池大小
    max_overflow=20,              # 超出连接池大小后允许的最大额外连接数
    pool_recycle=3600,            # 连接回收时间（秒），防止 MySQL 超时断开
    echo=settings.DEBUG,          # 开发模式下打印 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类（所有 ORM 模型继承此类）
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
    # 需要导入所有模型以确保它们被注册到 Base.metadata
    from app.models import user, training  # noqa: F401
    Base.metadata.create_all(bind=engine)
