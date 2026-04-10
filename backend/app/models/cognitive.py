"""
认知基线评估数据模型
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class CognitiveBaseline(Base):
    """认知基线评估模型"""
    __tablename__ = "cognitive_baselines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    memory_score = Column(Float, default=0, comment="记忆力基线分数")
    attention_score = Column(Float, default=0, comment="注意力基线分数")
    calculation_score = Column(Float, default=0, comment="计算力基线分数")
    logic_score = Column(Float, default=0, comment="逻辑推理基线分数")
    language_score = Column(Float, default=0, comment="语言能力基线分数")
    spatial_score = Column(Float, default=0, comment="空间定向基线分数")
    face_score = Column(Float, default=0, comment="人脸识别基线分数")
    rhythm_score = Column(Float, default=0, comment="节律训练基线分数")
    classification_score = Column(Float, default=0, comment="分类归纳基线分数")
    dual_task_score = Column(Float, default=0, comment="双重任务基线分数")
    total_score = Column(Float, default=0, comment="综合基线分数")
    assessment_type = Column(String(20), default="initial", comment="评估类型: initial/periodic")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="评估时间")

    user = relationship("User")

    def __repr__(self):
        return f"<CognitiveBaseline(id={self.id}, user_id={self.user_id})>"
