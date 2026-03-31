"""
训练数据接口模块
包含提交训练成绩、获取训练记录列表等功能
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.training import TrainingCreate, TrainingResponse
from app.services.auth_service import AuthService
from app.services.training_service import TrainingService

router = APIRouter()


@router.post("/submit", response_model=TrainingResponse, summary="提交训练成绩")
async def submit_training(
    training_data: TrainingCreate,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    提交一次训练成绩
    - game_type: 游戏类型（memory/attention/calculation/logic/language）
    - score: 得分
    - difficulty: 难度等级（1-5）
    - duration: 训练时长（秒）
    """
    training_service = TrainingService(db)
    record = training_service.create_training_record(current_user.id, training_data)
    return record


@router.get("/list", response_model=List[TrainingResponse], summary="获取训练记录列表")
async def get_training_list(
    game_type: Optional[str] = Query(None, description="游戏类型过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取当前用户的训练记录列表
    支持按游戏类型过滤，支持分页
    """
    training_service = TrainingService(db)
    records = training_service.get_user_training_records(
        user_id=current_user.id,
        game_type=game_type,
        page=page,
        page_size=page_size,
    )
    return records


@router.get("/types", summary="获取训练类型列表")
async def get_training_types():
    """获取所有支持的训练类型"""
    return {
        "types": [
            {"key": "memory", "name": "记忆力训练", "description": "翻牌配对、数字记忆序列"},
            {"key": "attention", "name": "注意力训练", "description": "舒尔特方格、找不同"},
            {"key": "calculation", "name": "计算力训练", "description": "速算挑战、24点"},
            {"key": "logic", "name": "逻辑推理", "description": "图形推理、数列规律"},
            {"key": "language", "name": "语言能力", "description": "成语接龙、词语联想"},
        ]
    }


@router.get("/stats", summary="获取训练统计数据")
async def get_training_stats(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的训练统计数据（各类型平均分、训练次数等）"""
    training_service = TrainingService(db)
    stats = training_service.get_user_stats(current_user.id)
    return stats
