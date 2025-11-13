"""
脚本相关的数据验证模式
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScriptCreate(BaseModel):
    """创建脚本请求"""
    project_id: uuid.UUID = Field(..., description="项目ID")
    story_outline: str = Field(..., min_length=10, description="故事梗概")
    model_config_id: uuid.UUID = Field(..., description="使用的AI模型配置ID")
    system_prompt: Optional[str] = Field(None, description="自定义系统提示词")


class ScriptUpdate(BaseModel):
    """更新脚本请求"""
    content: Optional[str] = Field(None, description="脚本内容")
    version: Optional[int] = Field(None, description="版本号")
    is_final: Optional[bool] = Field(None, description="是否为最终版本")


class ScriptResponse(BaseModel):
    """脚本响应"""
    script_id: uuid.UUID
    project_id: uuid.UUID
    content: str
    version: int
    is_final: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScriptGenerateRequest(BaseModel):
    """脚本生成请求"""
    story_outline: str = Field(..., min_length=10, description="故事梗概")
    model_config_id: uuid.UUID = Field(..., description="使用的AI模型配置ID")
    system_prompt: Optional[str] = Field(
        None, 
        description="自定义系统提示词"
    )
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(4000, ge=500, le=8000, description="最大生成长度")


class ScriptGenerateResponse(BaseModel):
    """脚本生成响应"""
    script_id: uuid.UUID
    content: str
    version: int
    usage: dict
    created_at: datetime
