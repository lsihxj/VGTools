"""
Celery异步任务模块
"""
from app.tasks.video_tasks import (
    generate_script_task,
    generate_storyboard_task,
    generate_character_images_task,
    generate_scene_images_task,
    generate_video_segment_task,
    merge_video_segments_task
)

__all__ = [
    "generate_script_task",
    "generate_storyboard_task",
    "generate_character_images_task",
    "generate_scene_images_task",
    "generate_video_segment_task",
    "merge_video_segments_task"
]
