"""
认证接口模块
包含用户注册、登录、用户偏好设置等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    - username: 用户名
    - password: 密码
    - nickname: 昵称
    - age_group: 年龄段（youth/middle/elder）
    - phone: 手机号（可选）
    """
    auth_service = AuthService(db)
    existing_user = auth_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    if user_data.phone:
        existing_phone = auth_service.get_user_by_phone(user_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册",
            )
    user = auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    - username: 用户名
    - password: 密码
    返回 JWT access token
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_service.create_access_token(user)
    return token


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前登录用户的基本信息（含偏好设置）"""
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_user_info(
    update_data: UserUpdate,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新当前用户信息
    支持更新：昵称、头像、手机、年龄段、字体大小、高对比度、提醒时间
    """
    auth_service = AuthService(db)
    allowed_fields = {"nickname", "avatar", "phone", "age_group", "font_size", "high_contrast", "reminder_time"}
    update_dict = update_data.dict(exclude_unset=True)
    filtered = {k: v for k, v in update_dict.items() if k in allowed_fields}
    updated_user = auth_service.update_user(current_user.id, filtered)
    return updated_user
