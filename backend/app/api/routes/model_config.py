"""
模型配置管理API路由
提供模型配置的增删改查和测试功能
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.api.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse,
    ModelConfigTest,
    ModelConfigTestResponse
)
from app.models.user import User
from app.services.model_config_service import ModelConfigService

router = APIRouter(prefix="/model-configs", tags=["model-configs"])


@router.post("", response_model=ModelConfigResponse, status_code=status.HTTP_201_CREATED)
def create_model_config(
    config_data: ModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的模型配置
    
    - **config_name**: 配置名称
    - **vendor**: 厂商(tongyi/zhipu/baidu/stable_diffusion/keling)
    - **model_name**: 模型名称
    - **api_key**: API密钥(会自动加密存储)
    - **api_endpoint**: API端点(可选)
    - **system_prompt**: 系统提示词(可选)
    - **user_prompt_template**: 用户提示词模板(可选)
    - **parameters**: 其他参数(可选)
    """
    try:
        config = ModelConfigService.create_config(
            db=db,
            user_id=current_user.user_id,
            config_name=config_data.config_name,
            vendor=config_data.vendor,
            model_name=config_data.model_name,
            api_key=config_data.api_key,
            api_endpoint=config_data.api_endpoint,
            system_prompt=config_data.system_prompt,
            user_prompt_template=config_data.user_prompt_template,
            parameters=config_data.parameters
        )
        return config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建配置失败: {str(e)}"
        )


@router.get("", response_model=List[ModelConfigResponse])
def get_model_configs(
    vendor: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有模型配置
    
    - **vendor**: 按厂商筛选(可选)
    """
    try:
        configs = ModelConfigService.get_configs(
            db=db,
            user_id=current_user.user_id,
            vendor=vendor
        )
        return configs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配置列表失败: {str(e)}"
        )


@router.get("/{config_id}", response_model=ModelConfigResponse)
def get_model_config(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定的模型配置
    
    - **config_id**: 配置ID
    """
    config = ModelConfigService.get_config(
        db=db,
        config_id=config_id,
        user_id=current_user.user_id
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    return config


@router.put("/{config_id}", response_model=ModelConfigResponse)
def update_model_config(
    config_id: UUID,
    config_data: ModelConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新模型配置
    
    - **config_id**: 配置ID
    - 其他字段同创建接口(仅更新提供的字段)
    """
    try:
        config = ModelConfigService.update_config(
            db=db,
            config_id=config_id,
            user_id=current_user.user_id,
            **config_data.model_dump(exclude_unset=True)
        )
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="配置不存在"
            )
        
        return config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新配置失败: {str(e)}"
        )


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_config(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除模型配置
    
    - **config_id**: 配置ID
    """
    success = ModelConfigService.delete_config(
        db=db,
        config_id=config_id,
        user_id=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    return None


@router.post("/{config_id}/test", response_model=ModelConfigTestResponse)
def test_model_config(
    config_id: UUID,
    test_data: ModelConfigTest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    测试模型配置
    
    - **config_id**: 配置ID
    - **test_prompt**: 测试提示词(可选,默认为"测试")
    """
    # 获取配置
    config = ModelConfigService.get_config(
        db=db,
        config_id=config_id,
        user_id=current_user.user_id
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 测试配置
    try:
        result = ModelConfigService.test_config(
            config=config,
            test_prompt=test_data.test_prompt
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试配置失败: {str(e)}"
        )
