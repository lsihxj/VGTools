"""
脚本管理API路由
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.api.schemas.script import (
    ScriptGenerateRequest,
    ScriptGenerateResponse,
    ScriptResponse,
    ScriptUpdate
)
from app.models.user import User
from app.services.script_service import ScriptService

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/generate", response_model=ScriptGenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_script(
    project_id: UUID,
    request: ScriptGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成视频脚本
    
    - **project_id**: 项目ID(查询参数)
    - **story_outline**: 故事梗概
    - **model_config_id**: 使用的AI模型配置ID
    - **system_prompt**: 自定义系统提示词(可选)
    - **temperature**: 温度参数(0.0-2.0,默认0.7)
    - **max_tokens**: 最大生成长度(500-8000,默认4000)
    """
    try:
        result = ScriptService.generate_script(
            db=db,
            user_id=current_user.user_id,
            project_id=project_id,
            story_outline=request.story_outline,
            model_config_id=request.model_config_id,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        script = result["script"]
        
        return ScriptGenerateResponse(
            script_id=script.script_id,
            content=script.content,
            version=script.version,
            usage=result["usage"],
            created_at=script.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"脚本生成失败: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=List[ScriptResponse])
def get_scripts_by_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目的所有脚本版本
    
    - **project_id**: 项目ID
    """
    try:
        scripts = ScriptService.get_scripts_by_project(
            db=db,
            project_id=project_id,
            user_id=current_user.user_id
        )
        return scripts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取脚本列表失败: {str(e)}"
        )


@router.get("/{script_id}", response_model=ScriptResponse)
def get_script(
    script_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定脚本
    
    - **script_id**: 脚本ID
    """
    script = ScriptService.get_script(
        db=db,
        script_id=script_id,
        user_id=current_user.user_id
    )
    
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )
    
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
def update_script(
    script_id: UUID,
    update_data: ScriptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新脚本
    
    - **script_id**: 脚本ID
    - **content**: 脚本内容(可选)
    - **is_final**: 是否为最终版本(可选)
    """
    try:
        script = ScriptService.update_script(
            db=db,
            script_id=script_id,
            user_id=current_user.user_id,
            **update_data.model_dump(exclude_unset=True)
        )
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="脚本不存在"
            )
        
        return script
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新脚本失败: {str(e)}"
        )


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_script(
    script_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除脚本
    
    - **script_id**: 脚本ID
    """
    success = ScriptService.delete_script(
        db=db,
        script_id=script_id,
        user_id=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="脚本不存在"
        )
    
    return None
