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

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    age_group = Column(
        Enum("youth", "middle", "elder"),
        default="youth",
        comment="年龄段",
    )
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    phone = Column(String(20), nullable=True, unique=True, comment="手机号")
    font_size = Column(String(10), default="normal", comment="字体大小: normal/large/xlarge")
    high_contrast = Column(Integer, default=0, comment="高对比度模式(0关1开)")
    reminder_time = Column(String(10), nullable=True, comment="每日提醒时间 HH:MM")
    baseline_completed = Column(Integer, default=0, comment="是否完成基线评估(0否1是)")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    training_records = relationship("TrainingRecord", back_populates="user", order_by="TrainingRecord.created_at.desc()")
    family_as_watcher = relationship("FamilyRelation", foreign_keys="FamilyRelation.watcher_id", back_populates="watcher")
    family_as_watched = relationship("FamilyRelation", foreign_keys="FamilyRelation.watched_id", back_populates="watched")
    achievements = relationship("UserAchievement", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
