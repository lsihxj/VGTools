"""
项目相关的数据验证模式
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """创建项目请求"""
    project_name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    project_name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    status: Optional[str] = Field(None, description="项目状态: draft/processing/completed/failed")


class ProjectResponse(BaseModel):
    """项目响应"""
    project_id: uuid.UUID
    user_id: uuid.UUID
    project_name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
