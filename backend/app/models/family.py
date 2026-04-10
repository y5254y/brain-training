"""
家人关注关系数据模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class FamilyRelation(Base):
    """家人关注关系模型"""
    __tablename__ = "family_relations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    watcher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="关注者ID(子女)")
    watched_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="被关注者ID(父母)")
    relation_type = Column(
        Enum("child", "spouse", "caregiver", "other"),
        default="child",
        comment="关系类型",
    )
    invite_code = Column(String(20), nullable=True, unique=True, comment="邀请码")
    status = Column(
        Enum("pending", "accepted", "rejected", "unbound"),
        default="pending",
        comment="状态",
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="更新时间",
    )

    watcher = relationship("User", foreign_keys=[watcher_id], back_populates="family_as_watcher")
    watched = relationship("User", foreign_keys=[watched_id], back_populates="family_as_watched")

    def __repr__(self):
        return f"<FamilyRelation(id={self.id}, watcher={self.watcher_id}, watched={self.watched_id})>"
