"""
认知评估业务逻辑服务
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cognitive import CognitiveBaseline
from app.models.training import TrainingRecord
from app.models.user import User
from app.services.training_service import GAME_TYPE_INFO


class CognitiveService:
    """认知评估服务类"""

    def __init__(self, db: Session):
        self.db = db

    def save_baseline(self, user_id: int, scores: Dict[str, float], assessment_type: str = "initial") -> CognitiveBaseline:
        """保存基线评估"""
        total = sum(scores.values())
        baseline = CognitiveBaseline(
            user_id=user_id,
            memory_score=scores.get("memory", 0),
            attention_score=scores.get("attention", 0),
            calculation_score=scores.get("calculation", 0),
            logic_score=scores.get("logic", 0),
            language_score=scores.get("language", 0),
            spatial_score=scores.get("spatial", 0),
            face_score=scores.get("face", 0),
            rhythm_score=scores.get("rhythm", 0),
            classification_score=scores.get("classification", 0),
            dual_task_score=scores.get("dual_task", 0),
            total_score=round(total, 2),
            assessment_type=assessment_type,
        )
        self.db.add(baseline)

        if assessment_type == "initial":
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.baseline_completed = 1

        self.db.commit()
        self.db.refresh(baseline)
        return baseline

    def get_latest_baseline(self, user_id: int) -> Optional[CognitiveBaseline]:
        """获取最新的基线评估"""
        return (
            self.db.query(CognitiveBaseline)
            .filter(CognitiveBaseline.user_id == user_id)
            .order_by(CognitiveBaseline.created_at.desc())
            .first()
        )

    def get_current_scores(self, user_id: int) -> Dict[str, float]:
        """获取当前各维度得分（近30天平均分）"""
        since_dt = datetime.now(timezone.utc) - timedelta(days=30)
        stats = (
            self.db.query(
                TrainingRecord.game_type,
                func.avg(TrainingRecord.score).label("avg_score"),
            )
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= since_dt,
            )
            .group_by(TrainingRecord.game_type)
            .all()
        )
        return {row.game_type: round(float(row.avg_score or 0), 2) for row in stats}

    def get_cognitive_trend(self, user_id: int) -> Dict[str, Any]:
        """获取认知趋势数据"""
        baseline = self.get_latest_baseline(user_id)
        current = self.get_current_scores(user_id)

        baseline_scores = {}
        if baseline:
            baseline_scores = {
                "memory": baseline.memory_score,
                "attention": baseline.attention_score,
                "calculation": baseline.calculation_score,
                "logic": baseline.logic_score,
                "language": baseline.language_score,
                "spatial": baseline.spatial_score,
                "face": baseline.face_score,
                "rhythm": baseline.rhythm_score,
                "classification": baseline.classification_score,
                "dual_task": baseline.dual_task_score,
            }

        changes = {}
        for dim in GAME_TYPE_INFO:
            b = baseline_scores.get(dim, 0)
            c = current.get(dim, 0)
            if b > 0:
                changes[dim] = round((c - b) / b * 100, 1)
            else:
                changes[dim] = 0

        trend_data = self._get_trend_time_series(user_id)

        return {
            "dimensions": list(GAME_TYPE_INFO.keys()),
            "baseline": baseline_scores,
            "current": current,
            "changes": changes,
            "trend_data": trend_data,
        }

    def _get_trend_time_series(self, user_id: int) -> list:
        """获取趋势时间序列数据"""
        end_dt = datetime.now(timezone.utc)
        result = []
        for i in range(6, -1, -1):
            check_date = (end_dt - timedelta(days=i)).date()
            start = datetime.combine(check_date, datetime.min.time())
            end = start + timedelta(days=1)
            records = (
                self.db.query(TrainingRecord)
                .filter(
                    TrainingRecord.user_id == user_id,
                    TrainingRecord.is_practice == 0,
                    TrainingRecord.created_at >= start,
                    TrainingRecord.created_at < end,
                )
                .all()
            )
            avg = sum(r.score for r in records) / len(records) if records else 0
            result.append({
                "date": check_date.isoformat(),
                "avg_score": round(avg, 2),
                "count": len(records),
            })
        return result

    def get_peer_comparison(self, user_id: int) -> Dict[str, Any]:
        """获取同龄人对比数据"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        age_group = user.age_group or "middle"
        user_scores = self.get_current_scores(user_id)

        peer_users = (
            self.db.query(User.id)
            .filter(User.age_group == age_group, User.id != user_id)
            .all()
        )
        peer_ids = [u.id for u in peer_users]

        peer_avg_scores = {}
        percentiles = {}

        if peer_ids:
            since_dt = datetime.now(timezone.utc) - timedelta(days=30)
            for game_type in GAME_TYPE_INFO:
                peer_avg = (
                    self.db.query(func.avg(TrainingRecord.score))
                    .filter(
                        TrainingRecord.user_id.in_(peer_ids),
                        TrainingRecord.game_type == game_type,
                        TrainingRecord.is_practice == 0,
                        TrainingRecord.created_at >= since_dt,
                    )
                    .scalar() or 0
                )
                peer_avg_scores[game_type] = round(float(peer_avg), 2)

                user_score = user_scores.get(game_type, 0)
                below_count = (
                    self.db.query(func.count(func.distinct(TrainingRecord.user_id)))
                    .filter(
                        TrainingRecord.user_id.in_(peer_ids),
                        TrainingRecord.game_type == game_type,
                        TrainingRecord.is_practice == 0,
                        TrainingRecord.created_at >= since_dt,
                        TrainingRecord.score < user_score,
                    )
                    .scalar() or 0
                )
                total_peers = len(peer_ids)
                percentiles[game_type] = round(below_count / total_peers * 100, 1) if total_peers > 0 else 50
        else:
            for game_type in GAME_TYPE_INFO:
                peer_avg_scores[game_type] = 0
                percentiles[game_type] = 50

        return {
            "age_group": age_group,
            "user_scores": user_scores,
            "peer_avg_scores": peer_avg_scores,
            "percentiles": percentiles,
        }
