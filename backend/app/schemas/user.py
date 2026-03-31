"""
用户相关的 Pydantic 数据校验模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator


class UserCreate(BaseModel):
    """用户注册请求模型"""
    username: str
    password: str
    nickname: Optional[str] = None
    age_group: Optional[str] = "youth"  # youth/middle/elder
    phone: Optional[str] = None

    @validator("username")
    def username_must_be_valid(cls, v):
        """用户名校验：3-50个字符"""
        if len(v) < 3 or len(v) > 50:
            raise ValueError("用户名长度必须在3到50个字符之间")
        return v

    @validator("password")
    def password_must_be_strong(cls, v):
        """密码校验：至少6个字符"""
        if len(v) < 6:
            raise ValueError("密码长度至少为6个字符")
        return v

    @validator("age_group")
    def age_group_must_be_valid(cls, v):
        """年龄段校验"""
        valid_groups = ["youth", "middle", "elder"]
        if v not in valid_groups:
            raise ValueError(f"年龄段必须是以下之一：{valid_groups}")
        return v


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模型（不包含密码）"""
    id: int
    username: str
    nickname: Optional[str] = None
    age_group: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token 响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token 载荷数据"""
    user_id: Optional[int] = None
    username: Optional[str] = None
