"""
家人关注相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FamilyBindRequest(BaseModel):
    """绑定家人请求模型"""
    invite_code: str


class FamilyInviteCodeResponse(BaseModel):
    """邀请码响应模型"""
    invite_code: str
    expire_minutes: int = 30


class FamilyMemberResponse(BaseModel):
    """家人成员响应模型"""
    relation_id: int
    user_id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    relation_type: str
    status: str
    created_at: Optional[datetime] = None


class FamilyReportResponse(BaseModel):
    """家人训练报告响应模型"""
    user_id: int
    nickname: Optional[str] = None
    today_trained: bool = False
    total_count: int = 0
    total_duration: int = 0
    radar_data: dict = {}
    recent_records: list = []
    streak_days: int = 0
    alerts: list = []
