"""
家人关注业务逻辑服务
"""
import random
import string
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.family import FamilyRelation
from app.models.user import User
from app.models.training import TrainingRecord
from app.services.training_service import TrainingService


class FamilyService:
    """家人关注服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.training_service = TrainingService(db)

    def generate_invite_code(self, user_id: int) -> Dict[str, Any]:
        """生成邀请码"""
        code = ''.join(random.choices(string.digits, k=6))
        existing = (
            self.db.query(FamilyRelation)
            .filter(FamilyRelation.invite_code == code, FamilyRelation.status == "pending")
            .first()
        )
        while existing:
            code = ''.join(random.choices(string.digits, k=6))
            existing = (
                self.db.query(FamilyRelation)
                .filter(FamilyRelation.invite_code == code, FamilyRelation.status == "pending")
                .first()
            )

        relation = FamilyRelation(
            watched_id=user_id,
            watcher_id=0,
            invite_code=code,
            status="pending",
        )
        self.db.add(relation)
        self.db.commit()
        self.db.refresh(relation)

        return {
            "invite_code": code,
            "expire_minutes": 30,
            "relation_id": relation.id,
        }

    def bind_family(self, watcher_id: int, invite_code: str, relation_type: str = "child") -> Dict[str, Any]:
        """通过邀请码绑定家人"""
        relation = (
            self.db.query(FamilyRelation)
            .filter(FamilyRelation.invite_code == invite_code, FamilyRelation.status == "pending")
            .first()
        )
        if not relation:
            raise ValueError("邀请码无效或已过期")

        if relation.watched_id == watcher_id:
            raise ValueError("不能关注自己")

        relation.watcher_id = watcher_id
        relation.relation_type = relation_type
        relation.status = "accepted"
        relation.invite_code = None
        self.db.commit()
        self.db.refresh(relation)

        watched_user = self.db.query(User).filter(User.id == relation.watched_id).first()
        return {
            "relation_id": relation.id,
            "watched_user": {
                "id": watched_user.id,
                "username": watched_user.username,
                "nickname": watched_user.nickname,
                "avatar": watched_user.avatar,
            },
            "relation_type": relation.relation_type,
            "status": relation.status,
        }

    def get_family_list(self, user_id: int) -> List[Dict[str, Any]]:
        """获取关注的家人列表"""
        relations = (
            self.db.query(FamilyRelation)
            .filter(FamilyRelation.watcher_id == user_id, FamilyRelation.status == "accepted")
            .all()
        )

        result = []
        for rel in relations:
            watched = self.db.query(User).filter(User.id == rel.watched_id).first()
            if watched:
                result.append({
                    "relation_id": rel.id,
                    "user_id": watched.id,
                    "username": watched.username,
                    "nickname": watched.nickname,
                    "avatar": watched.avatar,
                    "relation_type": rel.relation_type,
                    "status": rel.status,
                    "created_at": rel.created_at.isoformat() if rel.created_at else None,
                })
        return result

    def get_family_report(self, watcher_id: int, family_id: int) -> Dict[str, Any]:
        """查看家人训练报告"""
        relation = (
            self.db.query(FamilyRelation)
            .filter(
                FamilyRelation.watcher_id == watcher_id,
                FamilyRelation.watched_id == family_id,
                FamilyRelation.status == "accepted",
            )
            .first()
        )
        if not relation:
            raise ValueError("未关注该用户或关注关系未确认")

        watched_user = self.db.query(User).filter(User.id == family_id).first()
        radar_data = self.training_service.get_radar_data(family_id)
        stats = self.training_service.get_user_stats(family_id)

        today = datetime.now(timezone.utc).date()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
        today_count = (
            self.db.query(func.count(TrainingRecord.id))
            .filter(
                TrainingRecord.user_id == family_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= start_dt,
                TrainingRecord.created_at < end_dt,
            )
            .scalar() or 0
        )

        recent_records = (
            self.db.query(TrainingRecord)
            .filter(TrainingRecord.user_id == family_id, TrainingRecord.is_practice == 0)
            .order_by(TrainingRecord.created_at.desc())
            .limit(10)
            .all()
        )

        alerts = self._check_alerts(family_id, stats)

        return {
            "user_id": family_id,
            "nickname": watched_user.nickname if watched_user else None,
            "today_trained": today_count > 0,
            "total_count": stats.get("total_count", 0),
            "total_duration": stats.get("total_duration", 0),
            "radar_data": radar_data.get("radar_data", {}),
            "recent_records": [
                {
                    "game_type": r.game_type,
                    "score": r.score,
                    "difficulty": r.difficulty,
                    "duration": r.duration,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in recent_records
            ],
            "streak_days": stats.get("streak_days", 0),
            "alerts": alerts,
        }

    def _check_alerts(self, user_id: int, stats: Dict) -> List[Dict[str, Any]]:
        """检查异常预警"""
        alerts = []

        streak = stats.get("streak_days", 0)
        if streak == 0:
            alerts.append({
                "type": "no_training_today",
                "level": "warning",
                "message": "今日尚未训练",
            })

        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        recent_count = (
            self.db.query(func.count(TrainingRecord.id))
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= three_days_ago,
            )
            .scalar() or 0
        )
        if recent_count == 0:
            alerts.append({
                "type": "no_training_3days",
                "level": "danger",
                "message": "已连续3天未训练，请关注",
            })

        radar = stats.get("by_type", {})
        for game_type, type_stats in radar.items():
            avg_score = type_stats.get("avg_score", 0)
            if avg_score > 0 and avg_score < 30:
                alerts.append({
                    "type": "low_score",
                    "level": "warning",
                    "message": f"{game_type}维度得分较低（{avg_score:.0f}分）",
                })

        return alerts

    def unbind_family(self, watcher_id: int, relation_id: int) -> bool:
        """解除家人绑定"""
        relation = (
            self.db.query(FamilyRelation)
            .filter(
                FamilyRelation.id == relation_id,
                FamilyRelation.watcher_id == watcher_id,
            )
            .first()
        )
        if not relation:
            raise ValueError("关注关系不存在")

        relation.status = "unbound"
        self.db.commit()
        return True
