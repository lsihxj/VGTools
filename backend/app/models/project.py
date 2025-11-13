"""
视频项目相关模型
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class VideoProject(Base):
    """视频项目表"""
    __tablename__ = "video_projects"
    
    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    story_synopsis = Column(Text, nullable=True)
    status = Column(String(50), default='draft', nullable=False, index=True)  # draft/in_progress/completed
    workflow_graph = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="projects")
    
    def __repr__(self):
        return f"<VideoProject(name='{self.project_name}', status='{self.status}')>"


class Script(Base):
    """脚本表"""
    __tablename__ = "scripts"
    
    script_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('video_projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    generated_by_config = Column(UUID(as_uuid=True), ForeignKey('ai_model_configs.config_id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    project = relationship("VideoProject", backref="scripts")
    model_config = relationship("AIModelConfig")
    
    def __repr__(self):
        return f"<Script(project_id='{self.project_id}', version={self.version})>"


class Character(Base):
    """人物表"""
    __tablename__ = "characters"
    
    character_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('video_projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    biography = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    appearance = Column(Text, nullable=True)
    voice_profile = Column(JSONB, default={}, nullable=False)
    generated_by_config = Column(UUID(as_uuid=True), ForeignKey('ai_model_configs.config_id', ondelete='SET NULL'), nullable=True)
    
    # 关系
    project = relationship("VideoProject", backref="characters")
    model_config = relationship("AIModelConfig")
    
    def __repr__(self):
        return f"<Character(name='{self.name}')>"


class CharacterImage(Base):
    """人物形象表"""
    __tablename__ = "character_images"
    
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.character_id', ondelete='CASCADE'), nullable=False, index=True)
    view_type = Column(String(50), nullable=False)  # front/back/closeup
    local_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    generated_by_config = Column(UUID(as_uuid=True), ForeignKey('ai_model_configs.config_id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    character = relationship("Character", backref="images")
    model_config = relationship("AIModelConfig")
    
    def __repr__(self):
        return f"<CharacterImage(character_id='{self.character_id}', view='{self.view_type}')>"


class Scene(Base):
    """场景表"""
    __tablename__ = "scenes"
    
    scene_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('video_projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    environment_type = Column(String(100), nullable=True)
    
    # 关系
    project = relationship("VideoProject", backref="scenes")
    
    def __repr__(self):
        return f"<Scene(name='{self.name}')>"


class SceneImage(Base):
    """场景图表"""
    __tablename__ = "scene_images"
    
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('scenes.scene_id', ondelete='CASCADE'), nullable=False, index=True)
    angle_type = Column(String(50), nullable=False)  # front/side/top
    local_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    generated_by_config = Column(UUID(as_uuid=True), ForeignKey('ai_model_configs.config_id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    scene = relationship("Scene", backref="images")
    model_config = relationship("AIModelConfig")
    
    def __repr__(self):
        return f"<SceneImage(scene_id='{self.scene_id}', angle='{self.angle_type}')>"


class Storyboard(Base):
    """分镜表"""
    __tablename__ = "storyboards"
    
    storyboard_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey('scripts.script_id', ondelete='CASCADE'), nullable=False, index=True)
    shot_number = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    camera_angle = Column(String(50), nullable=True)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('scenes.scene_id', ondelete='SET NULL'), nullable=True)
    character_ids = Column(JSONB, default=[], nullable=False)
    
    # 关系
    script = relationship("Script", backref="storyboards")
    scene = relationship("Scene")
    
    def __repr__(self):
        return f"<Storyboard(shot_number={self.shot_number})>"


class VideoSegment(Base):
    """视频片段表"""
    __tablename__ = "video_segments"
    
    segment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storyboard_id = Column(UUID(as_uuid=True), ForeignKey('storyboards.storyboard_id', ondelete='CASCADE'), nullable=False, index=True)
    sequence_order = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    local_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(50), default='generating', nullable=False)  # generating/completed/failed
    is_approved = Column(Boolean, default=False, nullable=False)
    generated_by_config = Column(UUID(as_uuid=True), ForeignKey('ai_model_configs.config_id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    storyboard = relationship("Storyboard", backref="segments")
    model_config = relationship("AIModelConfig")
    
    def __repr__(self):
        return f"<VideoSegment(sequence={self.sequence_order}, status='{self.status}')>"


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('video_projects.project_id', ondelete='CASCADE'), nullable=False, index=True)
    task_type = Column(String(50), nullable=False, index=True)  # script/character/scene/video
    celery_task_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), default='pending', nullable=False, index=True)  # pending/running/success/failed
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    error_message = Column(Text, nullable=True)
    result_data = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    project = relationship("VideoProject", backref="tasks")
    
    def __repr__(self):
        return f"<Task(type='{self.task_type}', status='{self.status}')>"
