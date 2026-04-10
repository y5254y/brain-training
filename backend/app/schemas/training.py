"""
训练记录相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator


VALID_GAME_TYPES = [
    "memory", "attention", "calculation", "logic", "language",
    "spatial", "face", "rhythm", "classification", "dual_task",
]


class TrainingCreate(BaseModel):
    """创建训练记录请求模型"""
    game_type: str
    score: float
    difficulty: int = 1
    duration: int = 0
    is_practice: int = 0

    @validator("game_type")
    def game_type_must_be_valid(cls, v):
        if v not in VALID_GAME_TYPES:
            raise ValueError(f"游戏类型必须是以下之一：{VALID_GAME_TYPES}")
        return v

    @validator("score")
    def score_must_be_valid(cls, v):
        if v < 0 or v > 100:
            raise ValueError("得分必须在0到100之间")
        return v

    @validator("difficulty")
    def difficulty_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError("难度等级必须在1到5之间")
        return v


class TrainingResponse(BaseModel):
    """训练记录响应模型"""
    id: int
    user_id: int
    game_type: str
    score: float
    difficulty: int
    duration: int
    is_practice: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DifficultyRecommend(BaseModel):
    """难度推荐响应模型"""
    game_type: str
    recommended_difficulty: int
    reason: str
    recent_avg_score: Optional[float] = None
    recent_count: int = 0
