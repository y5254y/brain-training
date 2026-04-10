"""
认知评估相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class CognitiveBaselineResponse(BaseModel):
    """认知基线响应模型"""
    id: int
    user_id: int
    memory_score: float = 0
    attention_score: float = 0
    calculation_score: float = 0
    logic_score: float = 0
    language_score: float = 0
    spatial_score: float = 0
    face_score: float = 0
    rhythm_score: float = 0
    classification_score: float = 0
    dual_task_score: float = 0
    total_score: float = 0
    assessment_type: str = "initial"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CognitiveComparisonResponse(BaseModel):
    """同龄人对比响应模型"""
    age_group: str
    user_scores: Dict[str, float]
    peer_avg_scores: Dict[str, float]
    percentiles: Dict[str, float]


class CognitiveTrendResponse(BaseModel):
    """认知趋势响应模型"""
    dimensions: list
    baseline: Dict[str, float]
    current: Dict[str, float]
    changes: Dict[str, float]
    trend_data: list
