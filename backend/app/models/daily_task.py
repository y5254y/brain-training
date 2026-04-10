"""
每日任务数据模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class DailyTask(Base):
    """每日任务模型"""
    __tablename__ = "daily_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    task_date = Column(String(10), nullable=False, index=True, comment="任务日期 YYYY-MM-DD")
    task_type = Column(String(50), nullable=False, comment="任务类型")
    task_desc = Column(String(200), nullable=False, comment="任务描述")
    target_value = Column(Integer, default=1, comment="目标值")
    current_value = Column(Integer, default=0, comment="当前进度")
    is_completed = Column(Integer, default=0, comment="是否完成(0否1是)")
    reward_points = Column(Integer, default=10, comment="奖励积分")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    user = relationship("User")

    def __repr__(self):
        return f"<DailyTask(id={self.id}, user_id={self.user_id}, date={self.task_date})>"
