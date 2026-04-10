"""
每日任务接口模块
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.daily_task_service import DailyTaskService

router = APIRouter()


@router.get("/today", summary="获取今日任务")
async def get_today_tasks(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取今日任务列表（自动生成，自动更新进度）"""
    task_service = DailyTaskService(db)
    result = task_service.get_or_create_daily_tasks(current_user.id)
    return result
