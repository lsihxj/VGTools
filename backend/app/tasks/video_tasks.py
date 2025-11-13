"""
视频制作相关的异步任务
"""
import uuid
from typing import Optional
from celery import Task
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.project import Task as TaskModel
from app.services.script_service import ScriptService
from app.services.storyboard_service import StoryboardService


class DatabaseTask(Task):
    """带数据库会话的任务基类"""
    _db: Optional[Session] = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


def update_task_status(
    db: Session,
    task_id: uuid.UUID,
    status: str,
    progress: Optional[int] = None,
    result: Optional[str] = None,
    error_message: Optional[str] = None
):
    """更新任务状态"""
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if task:
        task.status = status
        if progress is not None:
            task.progress = progress
        if result is not None:
            task.result = result
        if error_message is not None:
            task.error_message = error_message
        db.commit()


@celery_app.task(base=DatabaseTask, bind=True, name="tasks.generate_script")
def generate_script_task(
    self,
    task_id: str,
    user_id: str,
    project_id: str,
    story_outline: str,
    model_config_id: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
):
    """
    异步生成脚本任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        project_id: 项目ID
        story_outline: 故事梗概
        model_config_id: 模型配置ID
        system_prompt: 系统提示词
        temperature: 温度
        max_tokens: 最大令牌数
    """
    db = self.db
    task_uuid = uuid.UUID(task_id)
    
    try:
        # 更新任务状态为进行中
        update_task_status(db, task_uuid, "processing", progress=10)
        
        # 生成脚本
        result = ScriptService.generate_script(
            db=db,
            user_id=uuid.UUID(user_id),
            project_id=uuid.UUID(project_id),
            story_outline=story_outline,
            model_config_id=uuid.UUID(model_config_id),
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 更新任务状态为完成
        update_task_status(
            db,
            task_uuid,
            "completed",
            progress=100,
            result=str(result["script"].script_id)
        )
        
        return {
            "script_id": str(result["script"].script_id),
            "version": result["script"].version
        }
        
    except Exception as e:
        # 更新任务状态为失败
        update_task_status(
            db,
            task_uuid,
            "failed",
            error_message=str(e)
        )
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="tasks.generate_storyboard")
def generate_storyboard_task(
    self,
    task_id: str,
    user_id: str,
    script_id: str,
    model_config_id: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 3000
):
    """
    异步生成分镜任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        script_id: 脚本ID
        model_config_id: 模型配置ID
        system_prompt: 系统提示词
        temperature: 温度
        max_tokens: 最大令牌数
    """
    db = self.db
    task_uuid = uuid.UUID(task_id)
    
    try:
        # 更新任务状态
        update_task_status(db, task_uuid, "processing", progress=10)
        
        # 生成分镜
        result = StoryboardService.generate_storyboards(
            db=db,
            user_id=uuid.UUID(user_id),
            script_id=uuid.UUID(script_id),
            model_config_id=uuid.UUID(model_config_id),
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 更新任务状态
        update_task_status(
            db,
            task_uuid,
            "completed",
            progress=100,
            result=f"生成了{result['count']}个分镜"
        )
        
        return {
            "count": result["count"],
            "storyboards": [str(sb.storyboard_id) for sb in result["storyboards"]]
        }
        
    except Exception as e:
        update_task_status(db, task_uuid, "failed", error_message=str(e))
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="tasks.generate_character_images")
def generate_character_images_task(
    self,
    task_id: str,
    user_id: str,
    character_id: str,
    model_config_id: str
):
    """
    异步生成人物形象任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        character_id: 人物ID
        model_config_id: 模型配置ID
    """
    db = self.db
    task_uuid = uuid.UUID(task_id)
    
    try:
        update_task_status(db, task_uuid, "processing", progress=10)
        
        # TODO: 实现人物形象生成逻辑
        # 这里需要调用图像生成服务
        
        update_task_status(db, task_uuid, "completed", progress=100)
        
        return {"character_id": character_id}
        
    except Exception as e:
        update_task_status(db, task_uuid, "failed", error_message=str(e))
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="tasks.generate_scene_images")
def generate_scene_images_task(
    self,
    task_id: str,
    user_id: str,
    scene_id: str,
    model_config_id: str
):
    """
    异步生成场景图任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        scene_id: 场景ID
        model_config_id: 模型配置ID
    """
    db = self.db
    task_uuid = uuid.UUID(task_id)
    
    try:
        update_task_status(db, task_uuid, "processing", progress=10)
        
        # TODO: 实现场景图生成逻辑
        
        update_task_status(db, task_uuid, "completed", progress=100)
        
        return {"scene_id": scene_id}
        
    except Exception as e:
        update_task_status(db, task_uuid, "failed", error_message=str(e))
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="tasks.generate_video_segment")
def generate_video_segment_task(
    self,
    task_id: str,
    user_id: str,
    storyboard_id: str,
    model_config_id: str
):
    """
    异步生成视频片段任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        storyboard_id: 分镜ID
        model_config_id: 模型配置ID
    """
    db = self.db
    task_uuid = uuid.UUID(task_id)
    
    try:
        update_task_status(db, task_uuid, "processing", progress=10)
        
        # TODO: 实现视频片段生成逻辑
        
        update_task_status(db, task_uuid, "completed", progress=100)
        
        return {"storyboard_id": storyboard_id}
        
    except Exception as e:
        update_task_status(db, task_uuid, "failed", error_message=str(e))
        raise


@celery_app.task(base=DatabaseTask, bind=True, name="tasks.merge_video_segments")
def merge_video_segments_task(
    self,
    task_id: str,
    user_id: str,
    project_id: str
):
    """
    异步合并视频片段任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        project_id: 项目ID
    """
    db = self.db
    task_uuid = uuid.UUID(task_id)
    
    try:
        update_task_status(db, task_uuid, "processing", progress=10)
        
        # TODO: 实现视频合并逻辑(使用FFmpeg)
        
        update_task_status(db, task_uuid, "completed", progress=100)
        
        return {"project_id": project_id}
        
    except Exception as e:
        update_task_status(db, task_uuid, "failed", error_message=str(e))
        raise
