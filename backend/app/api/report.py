"""
报告接口模块
包含获取训练报告、认知评估、同龄对比等功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.training_service import TrainingService
from app.services.cognitive_service import CognitiveService

router = APIRouter()


@router.get("/daily", summary="获取每日训练报告")
async def get_daily_report(
    date: str = Query(None, description="日期（YYYY-MM-DD），默认今天"),
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定日期的训练报告"""
    training_service = TrainingService(db)
    report = training_service.get_daily_report(current_user.id, date)
    return report


@router.get("/weekly", summary="获取每周训练报告")
async def get_weekly_report(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取最近7天的训练报告，含每日趋势"""
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
    """获取指定月份的训练报告"""
    training_service = TrainingService(db)
    report = training_service.get_monthly_report(current_user.id, year, month)
    return report


@router.get("/radar", summary="获取认知能力雷达图数据")
async def get_radar_data(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户各认知能力雷达图数据（近30天各类型平均分）"""
    training_service = TrainingService(db)
    radar_data = training_service.get_radar_data(current_user.id)
    return radar_data


@router.get("/baseline", summary="获取认知基线评估数据")
async def get_baseline(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户最新的认知基线评估数据"""
    cognitive_service = CognitiveService(db)
    baseline = cognitive_service.get_latest_baseline(current_user.id)
    if not baseline:
        return {"has_baseline": False, "baseline": None}
    return {
        "has_baseline": True,
        "baseline": {
            "id": baseline.id,
            "memory_score": baseline.memory_score,
            "attention_score": baseline.attention_score,
            "calculation_score": baseline.calculation_score,
            "logic_score": baseline.logic_score,
            "language_score": baseline.language_score,
            "spatial_score": baseline.spatial_score,
            "face_score": baseline.face_score,
            "rhythm_score": baseline.rhythm_score,
            "classification_score": baseline.classification_score,
            "dual_task_score": baseline.dual_task_score,
            "total_score": baseline.total_score,
            "assessment_type": baseline.assessment_type,
            "created_at": baseline.created_at.isoformat() if baseline.created_at else None,
        },
    }


@router.post("/baseline", summary="保存认知基线评估")
async def save_baseline(
    scores: dict,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    保存认知基线评估结果
    - scores: 各维度得分 {memory: 80, attention: 75, ...}
    - assessment_type: initial(首次) / periodic(定期)
    """
    cognitive_service = CognitiveService(db)
    assessment_type = scores.get("assessment_type", "initial")
    score_data = {k: v for k, v in scores.items() if k != "assessment_type"}
    baseline = cognitive_service.save_baseline(current_user.id, score_data, assessment_type)
    return {
        "message": "基线评估保存成功",
        "total_score": baseline.total_score,
    }


@router.get("/comparison", summary="获取同龄人对比数据")
async def get_peer_comparison(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取与同龄人的认知能力对比数据"""
    cognitive_service = CognitiveService(db)
    comparison = cognitive_service.get_peer_comparison(current_user.id)
    return comparison


@router.get("/trend", summary="获取认知能力趋势")
async def get_cognitive_trend(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取认知能力变化趋势（基线 vs 当前）"""
    cognitive_service = CognitiveService(db)
    trend = cognitive_service.get_cognitive_trend(current_user.id)
    return trend
