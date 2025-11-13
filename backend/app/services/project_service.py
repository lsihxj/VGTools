"""
项目管理服务
"""
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.project import VideoProject


class ProjectService:
    """项目服务类"""
    
    @staticmethod
    def create_project(
        db: Session,
        user_id: uuid.UUID,
        project_name: str,
        description: Optional[str] = None
    ) -> VideoProject:
        """创建新项目"""
        project = VideoProject(
            user_id=user_id,
            project_name=project_name,
            description=description,
            status="draft"
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def get_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[VideoProject]:
        """获取项目"""
        project = db.query(VideoProject).filter(
            and_(
                VideoProject.project_id == project_id,
                VideoProject.user_id == user_id
            )
        ).first()
        
        return project
    
    @staticmethod
    def get_projects(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[VideoProject]:
        """
        获取用户的项目列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 按状态筛选(可选)
            search: 搜索关键词(可选)
            skip: 跳过条数
            limit: 限制条数
            
        Returns:
            项目列表
        """
        query = db.query(VideoProject).filter(VideoProject.user_id == user_id)
        
        # 按状态筛选
        if status:
            query = query.filter(VideoProject.status == status)
        
        # 搜索
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    VideoProject.project_name.ilike(search_pattern),
                    VideoProject.description.ilike(search_pattern)
                )
            )
        
        # 排序和分页
        projects = query.order_by(VideoProject.updated_at.desc()).offset(skip).limit(limit).all()
        
        return projects
    
    @staticmethod
    def update_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[VideoProject]:
        """更新项目"""
        project = ProjectService.get_project(db, project_id, user_id)
        
        if not project:
            return None
        
        if project_name is not None:
            project.project_name = project_name
        
        if description is not None:
            project.description = description
        
        if status is not None:
            # 验证状态值
            valid_statuses = ["draft", "processing", "completed", "failed"]
            if status not in valid_statuses:
                raise ValueError(f"无效的状态值: {status}. 有效值: {valid_statuses}")
            project.status = status
        
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def delete_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        删除项目
        由于数据库设置了级联删除,会自动删除关联的脚本、人物、场景等数据
        """
        project = ProjectService.get_project(db, project_id, user_id)
        
        if not project:
            return False
        
        db.delete(project)
        db.commit()
        
        return True
    
    @staticmethod
    def count_projects(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[str] = None
    ) -> int:
        """统计项目数量"""
        query = db.query(VideoProject).filter(VideoProject.user_id == user_id)
        
        if status:
            query = query.filter(VideoProject.status == status)
        
        return query.count()
