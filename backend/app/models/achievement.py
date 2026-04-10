"""
成就系统数据模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


ACHIEVEMENT_DEFINITIONS = {
    "streak_3": {"name": "坚持不懈", "desc": "连续训练3天", "icon": "🔥"},
    "streak_7": {"name": "一周达人", "desc": "连续训练7天", "icon": "⭐"},
    "streak_30": {"name": "月度冠军", "desc": "连续训练30天", "icon": "👑"},
    "streak_100": {"name": "百日传奇", "desc": "连续训练100天", "icon": "💎"},
    "perfect_memory": {"name": "记忆大师", "desc": "记忆力训练获得满分", "icon": "🧠"},
    "perfect_attention": {"name": "专注达人", "desc": "注意力训练获得满分", "icon": "🎯"},
    "perfect_calculation": {"name": "速算高手", "desc": "计算力训练获得满分", "icon": "🔢"},
    "perfect_logic": {"name": "逻辑天才", "desc": "逻辑推理获得满分", "icon": "🧩"},
    "perfect_language": {"name": "语言专家", "desc": "语言能力获得满分", "icon": "💬"},
    "perfect_spatial": {"name": "空间导航", "desc": "空间定向获得满分", "icon": "🧭"},
    "perfect_face": {"name": "过目不忘", "desc": "人脸识别获得满分", "icon": "👤"},
    "perfect_rhythm": {"name": "节奏大师", "desc": "节律训练获得满分", "icon": "🎵"},
    "perfect_classification": {"name": "分类达人", "desc": "分类归纳获得满分", "icon": "📂"},
    "perfect_dual_task": {"name": "一心二用", "desc": "双重任务获得满分", "icon": "🔄"},
    "total_10": {"name": "初露锋芒", "desc": "累计训练10次", "icon": "🌱"},
    "total_50": {"name": "勤学苦练", "desc": "累计训练50次", "icon": "🌿"},
    "total_200": {"name": "训练达人", "desc": "累计训练200次", "icon": "🌳"},
    "all_types": {"name": "全能选手", "desc": "完成所有类型训练各1次", "icon": "🏅"},
    "improve_20": {"name": "进步之星", "desc": "某项能力得分提升20%以上", "icon": "📈"},
    "first_game": {"name": "初次尝试", "desc": "完成第一次训练", "icon": "🎉"},
}


class UserAchievement(Base):
    """用户成就模型"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    achievement_key = Column(String(50), nullable=False, index=True, comment="成就标识")
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="解锁时间")

    user = relationship("User", back_populates="achievements")

    def __repr__(self):
        return f"<UserAchievement(id={self.id}, user_id={self.user_id}, key={self.achievement_key})>"
