"""
用户数据模型
使用 SQLAlchemy ORM 定义用户表结构
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 用户名（唯一）
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    # 密码哈希
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    # 年龄段：youth=青少年, middle=中年, elder=老年
    age_group = Column(
        Enum("youth", "middle", "elder"),
        default="youth",
        comment="年龄段",
    )
    # 昵称
    nickname = Column(String(50), nullable=True, comment="昵称")
    # 头像 URL
    avatar = Column(String(255), nullable=True, comment="头像URL")
    # 手机号
    phone = Column(String(20), nullable=True, unique=True, comment="手机号")
    # 创建时间
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    # 更新时间
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    # 关联训练记录
    training_records = relationship("TrainingRecord", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
