"""
训练记录相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator


class TrainingCreate(BaseModel):
    """创建训练记录请求模型"""
    game_type: str  # memory/attention/calculation/logic/language
    score: float
    difficulty: int = 1
    duration: int = 0  # 训练时长（秒）

    @validator("game_type")
    def game_type_must_be_valid(cls, v):
        """游戏类型校验"""
        valid_types = ["memory", "attention", "calculation", "logic", "language"]
        if v not in valid_types:
            raise ValueError(f"游戏类型必须是以下之一：{valid_types}")
        return v

    @validator("score")
    def score_must_be_valid(cls, v):
        """得分校验：0-100"""
        if v < 0 or v > 100:
            raise ValueError("得分必须在0到100之间")
        return v

    @validator("difficulty")
    def difficulty_must_be_valid(cls, v):
        """难度校验：1-5"""
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
    created_at: datetime

    class Config:
        from_attributes = True
