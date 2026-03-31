"""
训练业务逻辑服务
处理训练记录的创建、查询、统计等逻辑
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.training import TrainingRecord
from app.schemas.training import TrainingCreate


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
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

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
        # 按时间倒序排列
        query = query.order_by(TrainingRecord.created_at.desc())
        # 分页
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()
        return records

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户训练统计数据"""
        # 查询各类型的训练统计
        stats_query = (
            self.db.query(
                TrainingRecord.game_type,
                func.count(TrainingRecord.id).label("count"),
                func.avg(TrainingRecord.score).label("avg_score"),
                func.max(TrainingRecord.score).label("max_score"),
                func.sum(TrainingRecord.duration).label("total_duration"),
            )
            .filter(TrainingRecord.user_id == user_id)
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

        # 总体统计
        total_count = sum(s["count"] for s in stats.values())
        total_duration = sum(s["total_duration"] for s in stats.values())

        return {
            "by_type": stats,
            "total_count": total_count,
            "total_duration": total_duration,
        }

    def get_daily_report(self, user_id: int, date_str: Optional[str] = None) -> Dict[str, Any]:
        """获取每日训练报告"""
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = datetime.utcnow().date()

        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)

        records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
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
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=7)

        records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.created_at >= start_dt,
            )
            .order_by(TrainingRecord.created_at.asc())
            .all()
        )

        # 按日期聚合
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
        now = datetime.utcnow()
        target_year = year or now.year
        target_month = month or now.month

        start_dt = datetime(target_year, target_month, 1)
        # 计算下个月的第一天
        if target_month == 12:
            end_dt = datetime(target_year + 1, 1, 1)
        else:
            end_dt = datetime(target_year, target_month + 1, 1)

        records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
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
        # 查询近30天各类型的平均分
        since_dt = datetime.utcnow() - timedelta(days=30)
        stats_query = (
            self.db.query(
                TrainingRecord.game_type,
                func.avg(TrainingRecord.score).label("avg_score"),
            )
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.created_at >= since_dt,
            )
            .group_by(TrainingRecord.game_type)
            .all()
        )

        # 初始化所有类型的默认分数为0
        radar = {
            "memory": 0,
            "attention": 0,
            "calculation": 0,
            "logic": 0,
            "language": 0,
        }
        for row in stats_query:
            radar[row.game_type] = round(float(row.avg_score or 0), 2)

        return {
            "radar_data": radar,
            "period": "近30天",
        }
