"""
每日任务相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DailyTaskResponse(BaseModel):
    """每日任务响应模型"""
    id: int
    task_type: str
    task_desc: str
    target_value: int
    current_value: int
    is_completed: int
    reward_points: int

    class Config:
        from_attributes = True


class DailyTaskListResponse(BaseModel):
    """每日任务列表响应模型"""
    date: str
    total_tasks: int
    completed_tasks: int
    total_points: int
    earned_points: int
    tasks: List[DailyTaskResponse]
