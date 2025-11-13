"""
分镜头相关的数据验证模式
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StoryboardCreate(BaseModel):
    """创建分镜请求"""
    script_id: uuid.UUID = Field(..., description="脚本ID")
    sequence_number: int = Field(..., ge=1, description="分镜序号")
    content: str = Field(..., min_length=1, description="分镜内容描述")
    duration: Optional[float] = Field(None, ge=0.1, description="预计时长(秒)")


class StoryboardUpdate(BaseModel):
    """更新分镜请求"""
    sequence_number: Optional[int] = Field(None, ge=1, description="分镜序号")
    content: Optional[str] = Field(None, min_length=1, description="分镜内容描述")
    duration: Optional[float] = Field(None, ge=0.1, description="预计时长(秒)")


class StoryboardResponse(BaseModel):
    """分镜响应"""
    storyboard_id: uuid.UUID
    script_id: uuid.UUID
    sequence_number: int
    content: str
    duration: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class StoryboardGenerateRequest(BaseModel):
    """分镜生成请求"""
    script_id: uuid.UUID = Field(..., description="脚本ID")
    model_config_id: uuid.UUID = Field(..., description="使用的AI模型配置ID")
    system_prompt: Optional[str] = Field(None, description="自定义系统提示词")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(3000, ge=500, le=6000, description="最大生成长度")


class StoryboardGenerateResponse(BaseModel):
    """分镜生成响应"""
    storyboards: list[dict]
    count: int
    usage: dict
