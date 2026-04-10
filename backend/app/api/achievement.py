"""
成就系统接口模块
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.achievement_service import AchievementService

router = APIRouter()


@router.get("/list", summary="获取成就列表")
async def get_achievements(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有成就（含已解锁和未解锁）"""
    achievement_service = AchievementService(db)
    result = achievement_service.get_user_achievements(current_user.id)
    return result
