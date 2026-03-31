"""
报告接口模块
包含获取训练报告、统计数据等功能
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.training_service import TrainingService

router = APIRouter()


@router.get("/daily", summary="获取每日训练报告")
async def get_daily_report(
    date: str = Query(None, description="日期（YYYY-MM-DD），默认今天"),
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取指定日期的训练报告
    包含当日训练次数、总时长、各类型得分等
    """
    training_service = TrainingService(db)
    report = training_service.get_daily_report(current_user.id, date)
    return report


@router.get("/weekly", summary="获取每周训练报告")
async def get_weekly_report(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取最近7天的训练报告
    包含每日训练趋势、各认知能力雷达图数据
    """
    training_service = TrainingService(db)
    report = training_service.get_weekly_report(current_user.id)
    return report


@router.get("/monthly", summary="获取每月训练报告")
async def get_monthly_report(
    year: int = Query(None, description="年份，默认当前年"),
    month: int = Query(None, ge=1, le=12, description="月份，默认当前月"),
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取指定月份的训练报告
    包含月度训练总结、能力提升趋势
    """
    training_service = TrainingService(db)
    report = training_service.get_monthly_report(current_user.id, year, month)
    return report


@router.get("/radar", summary="获取认知能力雷达图数据")
async def get_radar_data(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取用户各认知能力雷达图数据
    包含记忆力、注意力、计算力、逻辑推理、语言能力的综合评分
    """
    training_service = TrainingService(db)
    radar_data = training_service.get_radar_data(current_user.id)
    return radar_data
