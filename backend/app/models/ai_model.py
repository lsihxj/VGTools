"""
AI模型配置模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class AIModelConfig(Base):
    """AI模型配置表"""
    __tablename__ = "ai_model_configs"
    
    config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    config_name = Column(String(100), nullable=False)
    vendor = Column(String(50), nullable=False, index=True)  # tongyi/zhipu/baidu/keling等
    model_name = Column(String(100), nullable=False)
    api_key = Column(String(255), nullable=False)  # 加密存储
    api_endpoint = Column(String(500), nullable=True)
    system_prompt = Column(Text, nullable=True)
    user_prompt_template = Column(Text, nullable=True)
    parameters = Column(JSONB, default={}, nullable=False)  # temperature等参数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", backref="model_configs")
    
    def __repr__(self):
        return f"<AIModelConfig(name='{self.config_name}', vendor='{self.vendor}', model='{self.model_name}')>"
