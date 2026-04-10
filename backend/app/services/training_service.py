"""
训练业务逻辑服务
处理训练记录的创建、查询、统计、难度推荐等逻辑
"""
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.training import TrainingRecord
from app.models.achievement import UserAchievement, ACHIEVEMENT_DEFINITIONS
from app.schemas.training import TrainingCreate


GAME_TYPE_INFO = {
    "memory": {"name": "记忆力训练", "description": "翻牌配对、数字记忆序列"},
    "attention": {"name": "注意力训练", "description": "舒尔特方格、找不同"},
    "calculation": {"name": "计算力训练", "description": "速算挑战、24点"},
    "logic": {"name": "逻辑推理", "description": "图形推理、数列规律"},
    "language": {"name": "语言能力", "description": "成语接龙、词语联想"},
    "spatial": {"name": "空间定向", "description": "方向判断、路线记忆"},
    "face": {"name": "人脸识别", "description": "面孔记忆与识别"},
    "rhythm": {"name": "节律训练", "description": "节拍跟随、节奏复现"},
    "classification": {"name": "分类归纳", "description": "物品分类、语义归纳"},
    "dual_task": {"name": "双重任务", "description": "多任务并行处理"},
}


class TrainingService:
    """训练服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_training_record(self, user_id: int, training_data: TrainingCreate) -> TrainingRecord:
        """创建训练记录"""
        record = TrainingRecord(
            user_id=user_id,
            game_type=training_data.game_type,
            score=training_data.score,
            difficulty=training_data.difficulty,
            duration=training_data.duration,
            is_practice=training_data.is_practice,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        if training_data.is_practice == 0:
            self._check_achievements(user_id, training_data)

        return record

    def _check_achievements(self, user_id: int, training_data: TrainingCreate):
        """检查并解锁成就"""
        existing = {
            r.achievement_key
            for r in self.db.query(UserAchievement.achievement_key)
            .filter(UserAchievement.user_id == user_id)
            .all()
        }

        if "first_game" not in existing:
            self._unlock_achievement(user_id, "first_game")

        perfect_key = f"perfect_{training_data.game_type}"
        if perfect_key in ACHIEVEMENT_DEFINITIONS and perfect_key not in existing:
            if training_data.score >= 100:
                self._unlock_achievement(user_id, perfect_key)

        total_count = (
            self.db.query(func.count(TrainingRecord.id))
            .filter(TrainingRecord.user_id == user_id, TrainingRecord.is_practice == 0)
            .scalar() or 0
        )
        if total_count >= 10 and "total_10" not in existing:
            self._unlock_achievement(user_id, "total_10")
        if total_count >= 50 and "total_50" not in existing:
            self._unlock_achievement(user_id, "total_50")
        if total_count >= 200 and "total_200" not in existing:
            self._unlock_achievement(user_id, "total_200")

        distinct_types = (
            self.db.query(func.count(func.distinct(TrainingRecord.game_type)))
            .filter(TrainingRecord.user_id == user_id, TrainingRecord.is_practice == 0)
            .scalar() or 0
        )
        if distinct_types >= len(GAME_TYPE_INFO) and "all_types" not in existing:
            self._unlock_achievement(user_id, "all_types")

        streak = self._calculate_streak(user_id)
        if streak >= 3 and "streak_3" not in existing:
            self._unlock_achievement(user_id, "streak_3")
        if streak >= 7 and "streak_7" not in existing:
            self._unlock_achievement(user_id, "streak_7")
        if streak >= 30 and "streak_30" not in existing:
            self._unlock_achievement(user_id, "streak_30")
        if streak >= 100 and "streak_100" not in existing:
            self._unlock_achievement(user_id, "streak_100")

    def _unlock_achievement(self, user_id: int, achievement_key: str):
        """解锁成就"""
        achievement = UserAchievement(
            user_id=user_id,
            achievement_key=achievement_key,
        )
        self.db.add(achievement)
        self.db.commit()

    def _calculate_streak(self, user_id: int) -> int:
        """计算连续训练天数"""
        today = datetime.now(timezone.utc).date()
        streak = 0
        check_date = today
        for _ in range(200):
            start_dt = datetime.combine(check_date, datetime.min.time())
            end_dt = start_dt + timedelta(days=1)
            count = (
                self.db.query(func.count(TrainingRecord.id))
                .filter(
                    TrainingRecord.user_id == user_id,
                    TrainingRecord.is_practice == 0,
                    TrainingRecord.created_at >= start_dt,
                    TrainingRecord.created_at < end_dt,
                )
                .scalar() or 0
            )
            if count > 0:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        return streak

    def get_user_training_records(
        self,
        user_id: int,
        game_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[TrainingRecord]:
        """获取用户训练记录列表，支持过滤和分页"""
        query = self.db.query(TrainingRecord).filter(TrainingRecord.user_id == user_id)
        if game_type:
            query = query.filter(TrainingRecord.game_type == game_type)
        query = query.order_by(TrainingRecord.created_at.desc())
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()
        return records

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户训练统计数据"""
        stats_query = (
            self.db.query(
                TrainingRecord.game_type,
                func.count(TrainingRecord.id).label("count"),
                func.avg(TrainingRecord.score).label("avg_score"),
                func.max(TrainingRecord.score).label("max_score"),
                func.sum(TrainingRecord.duration).label("total_duration"),
            )
            .filter(TrainingRecord.user_id == user_id, TrainingRecord.is_practice == 0)
            .group_by(TrainingRecord.game_type)
            .all()
        )

        stats = {}
        for row in stats_query:
            stats[row.game_type] = {
                "count": row.count,
                "avg_score": round(float(row.avg_score or 0), 2),
                "max_score": round(float(row.max_score or 0), 2),
                "total_duration": row.total_duration or 0,
            }

        total_count = sum(s["count"] for s in stats.values())
        total_duration = sum(s["total_duration"] for s in stats.values())

        return {
            "by_type": stats,
            "total_count": total_count,
            "total_duration": total_duration,
            "streak_days": self._calculate_streak(user_id),
        }

    def get_difficulty_recommendation(self, user_id: int, game_type: str) -> Dict[str, Any]:
        """获取自适应难度推荐"""
        recent_records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.game_type == game_type,
                TrainingRecord.is_practice == 0,
            )
            .order_by(TrainingRecord.created_at.desc())
            .limit(5)
            .all()
        )

        if not recent_records:
            return {
                "game_type": game_type,
                "recommended_difficulty": 1,
                "reason": "首次训练，建议从简单难度开始",
                "recent_avg_score": None,
                "recent_count": 0,
            }

        avg_score = sum(r.score for r in recent_records) / len(recent_records)
        current_diff = recent_records[0].difficulty

        if avg_score >= 85:
            recommended = min(current_diff + 1, 5)
            reason = f"近期平均分{avg_score:.0f}分，表现出色，建议提升难度"
        elif avg_score >= 60:
            recommended = current_diff
            reason = f"近期平均分{avg_score:.0f}分，当前难度适中"
        elif avg_score >= 40:
            recommended = max(current_diff - 1, 1)
            reason = f"近期平均分{avg_score:.0f}分，建议降低难度以巩固基础"
        else:
            recommended = max(current_diff - 1, 1)
            reason = f"近期平均分{avg_score:.0f}分，建议降低难度多加练习"

        return {
            "game_type": game_type,
            "recommended_difficulty": recommended,
            "reason": reason,
            "recent_avg_score": round(avg_score, 2),
            "recent_count": len(recent_records),
        }

    def get_daily_report(self, user_id: int, date_str: Optional[str] = None) -> Dict[str, Any]:
        """获取每日训练报告"""
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = datetime.now(timezone.utc).date()

        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)

        records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= start_dt,
                TrainingRecord.created_at < end_dt,
            )
            .all()
        )

        return {
            "date": target_date.isoformat(),
            "total_count": len(records),
            "total_duration": sum(r.duration for r in records),
            "records": [
                {
                    "game_type": r.game_type,
                    "score": r.score,
                    "difficulty": r.difficulty,
                    "duration": r.duration,
                }
                for r in records
            ],
        }

    def get_weekly_report(self, user_id: int) -> Dict[str, Any]:
        """获取最近7天的训练报告"""
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(days=7)

        records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= start_dt,
            )
            .order_by(TrainingRecord.created_at.asc())
            .all()
        )

        daily_data: Dict[str, Dict] = {}
        for record in records:
            date_key = record.created_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {"count": 0, "total_score": 0, "total_duration": 0}
            daily_data[date_key]["count"] += 1
            daily_data[date_key]["total_score"] += record.score
            daily_data[date_key]["total_duration"] += record.duration

        return {
            "start_date": start_dt.date().isoformat(),
            "end_date": end_dt.date().isoformat(),
            "total_count": len(records),
            "daily_data": daily_data,
        }

    def get_monthly_report(
        self, user_id: int, year: Optional[int] = None, month: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取月度训练报告"""
        now = datetime.now(timezone.utc)
        target_year = year or now.year
        target_month = month or now.month

        start_dt = datetime(target_year, target_month, 1)
        if target_month == 12:
            end_dt = datetime(target_year + 1, 1, 1)
        else:
            end_dt = datetime(target_year, target_month + 1, 1)

        records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= start_dt,
                TrainingRecord.created_at < end_dt,
            )
            .all()
        )

        return {
            "year": target_year,
            "month": target_month,
            "total_count": len(records),
            "total_duration": sum(r.duration for r in records),
        }

    def get_radar_data(self, user_id: int) -> Dict[str, Any]:
        """获取认知能力雷达图数据"""
        since_dt = datetime.now(timezone.utc) - timedelta(days=30)
        stats_query = (
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

        radar = {gt: 0 for gt in GAME_TYPE_INFO}
        for row in stats_query:
            radar[row.game_type] = round(float(row.avg_score or 0), 2)

        return {
            "radar_data": radar,
            "period": "近30天",
        }

    def get_training_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """获取今日训练推荐"""
        radar_data = self.get_radar_data(user_id)["radar_data"]
        sorted_types = sorted(radar_data.items(), key=lambda x: x[1])

        recommendations = []
        for game_type, score in sorted_types[:3]:
            info = GAME_TYPE_INFO.get(game_type, {})
            diff_rec = self.get_difficulty_recommendation(user_id, game_type)
            recommendations.append({
                "game_type": game_type,
                "name": info.get("name", game_type),
                "description": info.get("description", ""),
                "current_score": score,
                "recommended_difficulty": diff_rec["recommended_difficulty"],
                "reason": f"该维度得分较低（{score:.0f}分），建议重点训练",
            })
        return recommendations

    def get_game_types(self) -> List[Dict[str, str]]:
        """获取所有游戏类型"""
        return [
            {"key": k, "name": v["name"], "description": v["description"]}
            for k, v in GAME_TYPE_INFO.items()
        ]
