"""
分镜头管理API路由
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.api.schemas.storyboard import (
    StoryboardCreate,
    StoryboardUpdate,
    StoryboardResponse,
    StoryboardGenerateRequest,
    StoryboardGenerateResponse
)
from app.models.user import User
from app.services.storyboard_service import StoryboardService

router = APIRouter(prefix="/storyboards", tags=["storyboards"])


@router.post("/generate", response_model=StoryboardGenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_storyboards(
    request: StoryboardGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成分镜头剧本
    
    - **script_id**: 脚本ID
    - **model_config_id**: 使用的AI模型配置ID
    - **system_prompt**: 自定义系统提示词(可选)
    - **temperature**: 温度参数(0.0-2.0,默认0.7)
    - **max_tokens**: 最大生成长度(500-6000,默认3000)
    """
    try:
        result = StoryboardService.generate_storyboards(
            db=db,
            user_id=current_user.user_id,
            script_id=request.script_id,
            model_config_id=request.model_config_id,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        storyboards_data = [
            {
                "storyboard_id": str(sb.storyboard_id),
                "sequence_number": sb.sequence_number,
                "content": sb.content,
                "duration": sb.duration
            }
            for sb in result["storyboards"]
        ]
        
        return StoryboardGenerateResponse(
            storyboards=storyboards_data,
            count=result["count"],
            usage=result["usage"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分镜生成失败: {str(e)}"
        )


@router.get("/script/{script_id}", response_model=List[StoryboardResponse])
def get_storyboards_by_script(
    script_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取脚本的所有分镜
    
    - **script_id**: 脚本ID
    """
    try:
        storyboards = StoryboardService.get_storyboards_by_script(
            db=db,
            script_id=script_id,
            user_id=current_user.user_id
        )
        return storyboards
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分镜列表失败: {str(e)}"
        )


@router.post("", response_model=StoryboardResponse, status_code=status.HTTP_201_CREATED)
def create_storyboard(
    storyboard_data: StoryboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    手动创建分镜
    
    - **script_id**: 脚本ID
    - **sequence_number**: 分镜序号
    - **content**: 分镜内容描述
    - **duration**: 预计时长(秒,可选)
    """
    try:
        storyboard = StoryboardService.create_storyboard(
            db=db,
            user_id=current_user.user_id,
            script_id=storyboard_data.script_id,
            sequence_number=storyboard_data.sequence_number,
            content=storyboard_data.content,
            duration=storyboard_data.duration
        )
        return storyboard
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分镜失败: {str(e)}"
        )


@router.get("/{storyboard_id}", response_model=StoryboardResponse)
def get_storyboard(
    storyboard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定分镜
    
    - **storyboard_id**: 分镜ID
    """
    storyboard = StoryboardService.get_storyboard(
        db=db,
        storyboard_id=storyboard_id,
        user_id=current_user.user_id
    )
    
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分镜不存在"
        )
    
    return storyboard


@router.put("/{storyboard_id}", response_model=StoryboardResponse)
def update_storyboard(
    storyboard_id: UUID,
    update_data: StoryboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新分镜
    
    - **storyboard_id**: 分镜ID
    - **sequence_number**: 分镜序号(可选)
    - **content**: 分镜内容(可选)
    - **duration**: 预计时长(可选)
    """
    try:
        storyboard = StoryboardService.update_storyboard(
            db=db,
            storyboard_id=storyboard_id,
            user_id=current_user.user_id,
            **update_data.model_dump(exclude_unset=True)
        )
        
        if not storyboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分镜不存在"
            )
        
        return storyboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分镜失败: {str(e)}"
        )


@router.delete("/{storyboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_storyboard(
    storyboard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除分镜
    
    - **storyboard_id**: 分镜ID
    """
    success = StoryboardService.delete_storyboard(
        db=db,
        storyboard_id=storyboard_id,
        user_id=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分镜不存在"
        )
    
    return None
