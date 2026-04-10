"""
成就系统相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class AchievementResponse(BaseModel):
    """成就响应模型"""
    key: str
    name: str
    desc: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None


class AchievementListResponse(BaseModel):
    """成就列表响应模型"""
    total: int
    unlocked: int
    achievements: List[AchievementResponse]
