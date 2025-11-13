"""
项目管理API路由
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.api.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)
from app.models.user import User
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新项目
    
    - **project_name**: 项目名称
    - **description**: 项目描述(可选)
    """
    try:
        project = ProjectService.create_project(
            db=db,
            user_id=current_user.user_id,
            project_name=project_data.project_name,
            description=project_data.description
        )
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建项目失败: {str(e)}"
        )


@router.get("", response_model=List[ProjectResponse])
def get_projects(
    status_filter: str | None = Query(None, alias="status", description="按状态筛选"),
    search: str | None = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(50, ge=1, le=100, description="限制条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目列表
    
    - **status**: 按状态筛选(draft/processing/completed/failed)
    - **search**: 搜索关键词
    - **skip**: 跳过条数
    - **limit**: 限制条数(最大100)
    """
    try:
        projects = ProjectService.get_projects(
            db=db,
            user_id=current_user.user_id,
            status=status_filter,
            search=search,
            skip=skip,
            limit=limit
        )
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目列表失败: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定项目
    
    - **project_id**: 项目ID
    """
    project = ProjectService.get_project(
        db=db,
        project_id=project_id,
        user_id=current_user.user_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    update_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新项目
    
    - **project_id**: 项目ID
    - **project_name**: 项目名称(可选)
    - **description**: 项目描述(可选)
    - **status**: 项目状态(可选,draft/processing/completed/failed)
    """
    try:
        project = ProjectService.update_project(
            db=db,
            project_id=project_id,
            user_id=current_user.user_id,
            **update_data.model_dump(exclude_unset=True)
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新项目失败: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除项目(会级联删除所有关联数据)
    
    - **project_id**: 项目ID
    """
    success = ProjectService.delete_project(
        db=db,
        project_id=project_id,
        user_id=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return None


@router.get("/stats/count")
def get_project_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目统计信息"""
    try:
        total = ProjectService.count_projects(db, current_user.user_id)
        draft = ProjectService.count_projects(db, current_user.user_id, status="draft")
        processing = ProjectService.count_projects(db, current_user.user_id, status="processing")
        completed = ProjectService.count_projects(db, current_user.user_id, status="completed")
        failed = ProjectService.count_projects(db, current_user.user_id, status="failed")
        
        return {
            "total": total,
            "draft": draft,
            "processing": processing,
            "completed": completed,
            "failed": failed
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
