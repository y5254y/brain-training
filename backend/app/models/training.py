"""
训练记录数据模型
使用 SQLAlchemy ORM 定义训练记录表结构
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class TrainingRecord(Base):
    """训练记录模型"""
    __tablename__ = "training_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    game_type = Column(
        Enum("memory", "attention", "calculation", "logic", "language",
             "spatial", "face", "rhythm", "classification", "dual_task"),
        nullable=False,
        index=True,
        comment="游戏类型",
    )
    score = Column(Float, nullable=False, default=0.0, comment="得分")
    difficulty = Column(Integer, nullable=False, default=1, comment="难度等级")
    duration = Column(Integer, nullable=False, default=0, comment="训练时长（秒）")
    is_practice = Column(Integer, nullable=False, default=0, comment="是否练习模式(0否1是)")
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        comment="训练完成时间",
    )

    user = relationship("User", back_populates="training_records")

    def __repr__(self):
        return f"<TrainingRecord(id={self.id}, user_id={self.user_id}, game_type={self.game_type})>"
