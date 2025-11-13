"""
模型配置相关的Pydantic模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class ModelConfigCreate(BaseModel):
    """创建模型配置"""
    config_name: str = Field(..., min_length=1, max_length=100)
    vendor: str = Field(..., description="厂商: tongyi/zhipu/baidu/stable_diffusion/keling")
    model_name: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1)
    api_endpoint: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    config_name: Optional[str] = None
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ModelConfigResponse(BaseModel):
    """模型配置响应"""
    config_id: uuid.UUID
    user_id: uuid.UUID
    config_name: str
    vendor: str
    model_name: str
    api_endpoint: Optional[str]
    system_prompt: Optional[str]
    user_prompt_template: Optional[str]
    parameters: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModelConfigTest(BaseModel):
    """测试模型配置"""
    config_id: uuid.UUID
    test_prompt: str = "测试连接"
