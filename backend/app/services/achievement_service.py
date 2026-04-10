"""
成就系统业务逻辑服务
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.achievement import UserAchievement, ACHIEVEMENT_DEFINITIONS


class AchievementService:
    """成就服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_achievements(self, user_id: int) -> Dict[str, Any]:
        """获取用户成就列表"""
        unlocked_records = (
            self.db.query(UserAchievement)
            .filter(UserAchievement.user_id == user_id)
            .all()
        )
        unlocked_map = {r.achievement_key: r.unlocked_at for r in unlocked_records}

        achievements = []
        for key, definition in ACHIEVEMENT_DEFINITIONS.items():
            unlocked_at = unlocked_map.get(key)
            achievements.append({
                "key": key,
                "name": definition["name"],
                "desc": definition["desc"],
                "icon": definition["icon"],
                "unlocked": unlocked_at is not None,
                "unlocked_at": unlocked_at.isoformat() if unlocked_at else None,
            })

        unlocked_count = sum(1 for a in achievements if a["unlocked"])

        return {
            "total": len(achievements),
            "unlocked": unlocked_count,
            "achievements": achievements,
        }
