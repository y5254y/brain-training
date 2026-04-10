"""
每日任务业务逻辑服务
"""
from datetime import datetime, timezone
from typing import Dict, Any, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.daily_task import DailyTask
from app.models.training import TrainingRecord


TASK_TEMPLATES = [
    {"task_type": "train_once", "task_desc": "完成1次训练", "target_value": 1, "reward_points": 10},
    {"task_type": "train_score_80", "task_desc": "单次训练得分达到80分", "target_value": 1, "reward_points": 15},
    {"task_type": "train_new_type", "task_desc": "尝试一种新的训练类型", "target_value": 1, "reward_points": 20},
    {"task_type": "train_three_times", "task_desc": "完成3次训练", "target_value": 3, "reward_points": 25},
]


class DailyTaskService:
    """每日任务服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_daily_tasks(self, user_id: int) -> Dict[str, Any]:
        """获取或创建今日任务"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        existing = (
            self.db.query(DailyTask)
            .filter(DailyTask.user_id == user_id, DailyTask.task_date == today)
            .all()
        )

        if not existing:
            import random
            selected = random.sample(TASK_TEMPLATES, min(3, len(TASK_TEMPLATES)))
            for template in selected:
                task = DailyTask(
                    user_id=user_id,
                    task_date=today,
                    task_type=template["task_type"],
                    task_desc=template["task_desc"],
                    target_value=template["target_value"],
                    reward_points=template["reward_points"],
                )
                self.db.add(task)
            self.db.commit()
            existing = (
                self.db.query(DailyTask)
                .filter(DailyTask.user_id == user_id, DailyTask.task_date == today)
                .all()
            )

        self._update_task_progress(user_id, today, existing)

        tasks = []
        total_points = 0
        earned_points = 0
        completed_count = 0
        for task in existing:
            total_points += task.reward_points
            if task.is_completed:
                earned_points += task.reward_points
                completed_count += 1
            tasks.append({
                "id": task.id,
                "task_type": task.task_type,
                "task_desc": task.task_desc,
                "target_value": task.target_value,
                "current_value": task.current_value,
                "is_completed": task.is_completed,
                "reward_points": task.reward_points,
            })

        return {
            "date": today,
            "total_tasks": len(tasks),
            "completed_tasks": completed_count,
            "total_points": total_points,
            "earned_points": earned_points,
            "tasks": tasks,
        }

    def _update_task_progress(self, user_id: int, date_str: str, tasks: List[DailyTask]):
        """更新任务进度"""
        from datetime import timedelta
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)

        today_records = (
            self.db.query(TrainingRecord)
            .filter(
                TrainingRecord.user_id == user_id,
                TrainingRecord.is_practice == 0,
                TrainingRecord.created_at >= start_dt,
                TrainingRecord.created_at < end_dt,
            )
            .all()
        )

        today_count = len(today_records)
        high_score_count = sum(1 for r in today_records if r.score >= 80)
        today_types = set(r.game_type for r in today_records)

        for task in tasks:
            if task.is_completed:
                continue

            if task.task_type == "train_once":
                task.current_value = min(today_count, task.target_value)
            elif task.task_type == "train_score_80":
                task.current_value = min(high_score_count, task.target_value)
            elif task.task_type == "train_new_type":
                all_types = set()
                all_records = (
                    self.db.query(TrainingRecord.game_type)
                    .filter(TrainingRecord.user_id == user_id, TrainingRecord.is_practice == 0)
                    .all()
                )
                for r in all_records:
                    all_types.add(r[0])
                new_types = today_types - all_types
                task.current_value = min(len(new_types), task.target_value) if new_types else 0
            elif task.task_type == "train_three_times":
                task.current_value = min(today_count, task.target_value)

            if task.current_value >= task.target_value:
                task.is_completed = 1
                task.completed_at = datetime.now(timezone.utc)

        self.db.commit()
