"""
脚本生成和管理服务
"""
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.project import Script, VideoProject
from app.models.ai_model import AIModelConfig
from app.services.ai_adapters.base import TextModelAdapter
from app.services.ai_adapters.tongyi import TongyiAdapter
from app.services.ai_adapters.zhipu import ZhipuAdapter
from app.services.ai_adapters.baidu import BaiduAdapter
from app.utils.encryption import decrypt_string


class ScriptService:
    """脚本服务类"""
    
    # 默认系统提示词
    DEFAULT_SYSTEM_PROMPT = """你是一位专业的视频脚本创作专家。
你需要根据用户提供的故事梗概,创作一个完整的视频脚本。

脚本要求:
1. 结构清晰,包含开头、发展、高潮、结尾
2. 对话自然,符合角色性格
3. 场景描述详细,便于后续生成分镜头
4. 时长控制在3-5分钟(约800-1200字)
5. 适合视频呈现,注意视觉化表达

请直接输出脚本内容,不要包含任何说明文字。"""
    
    @staticmethod
    def _get_adapter(config: AIModelConfig) -> TextModelAdapter:
        """根据配置获取对应的AI适配器"""
        # 解密API Key
        api_key = decrypt_string(config.api_key)
        
        # 根据厂商创建适配器
        if config.vendor == "tongyi":
            return TongyiAdapter(
                api_key=api_key,
                model_name=config.model_name,
                api_endpoint=config.api_endpoint
            )
        elif config.vendor == "zhipu":
            return ZhipuAdapter(
                api_key=api_key,
                model_name=config.model_name,
                api_endpoint=config.api_endpoint
            )
        elif config.vendor == "baidu":
            return BaiduAdapter(
                api_key=api_key,
                model_name=config.model_name,
                api_endpoint=config.api_endpoint
            )
        else:
            raise ValueError(f"不支持的厂商: {config.vendor}")
    
    @staticmethod
    def generate_script(
        db: Session,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        story_outline: str,
        model_config_id: uuid.UUID,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> dict:
        """
        生成视频脚本
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            project_id: 项目ID
            story_outline: 故事梗概
            model_config_id: AI模型配置ID
            system_prompt: 自定义系统提示词(可选)
            temperature: 温度参数
            max_tokens: 最大生成长度
            
        Returns:
            包含脚本信息和使用统计的字典
        """
        # 验证项目是否属于用户
        project = db.query(VideoProject).filter(
            and_(
                VideoProject.project_id == project_id,
                VideoProject.user_id == user_id
            )
        ).first()
        
        if not project:
            raise ValueError("项目不存在或无权访问")
        
        # 获取模型配置
        config = db.query(AIModelConfig).filter(
            and_(
                AIModelConfig.config_id == model_config_id,
                AIModelConfig.user_id == user_id
            )
        ).first()
        
        if not config:
            raise ValueError("模型配置不存在或无权访问")
        
        # 使用自定义系统提示词或配置中的提示词或默认提示词
        final_system_prompt = (
            system_prompt or 
            config.system_prompt or 
            ScriptService.DEFAULT_SYSTEM_PROMPT
        )
        
        # 构建用户提示词
        if config.user_prompt_template:
            user_prompt = config.user_prompt_template.format(story_outline=story_outline)
        else:
            user_prompt = f"故事梗概:\n{story_outline}\n\n请根据以上梗概创作完整的视频脚本。"
        
        # 获取适配器并生成脚本
        adapter = ScriptService._get_adapter(config)
        
        result = adapter.generate_text(
            prompt=user_prompt,
            system_prompt=final_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not result.get("success"):
            raise Exception(f"脚本生成失败: {result.get('error', '未知错误')}")
        
        # 获取当前最大版本号
        max_version = db.query(Script).filter(
            Script.project_id == project_id
        ).count()
        
        # 创建脚本记录
        script = Script(
            project_id=project_id,
            content=result["text"],
            version=max_version + 1,
            is_final=False
        )
        
        db.add(script)
        db.commit()
        db.refresh(script)
        
        return {
            "script": script,
            "usage": result.get("usage", {}),
            "model_info": {
                "vendor": config.vendor,
                "model_name": config.model_name
            }
        }
    
    @staticmethod
    def get_script(
        db: Session,
        script_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[Script]:
        """获取脚本"""
        script = db.query(Script).join(VideoProject).filter(
            and_(
                Script.script_id == script_id,
                VideoProject.user_id == user_id
            )
        ).first()
        
        return script
    
    @staticmethod
    def get_scripts_by_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[Script]:
        """获取项目的所有脚本版本"""
        scripts = db.query(Script).join(VideoProject).filter(
            and_(
                Script.project_id == project_id,
                VideoProject.user_id == user_id
            )
        ).order_by(Script.version.desc()).all()
        
        return scripts
    
    @staticmethod
    def update_script(
        db: Session,
        script_id: uuid.UUID,
        user_id: uuid.UUID,
        content: Optional[str] = None,
        is_final: Optional[bool] = None
    ) -> Optional[Script]:
        """更新脚本"""
        script = ScriptService.get_script(db, script_id, user_id)
        
        if not script:
            return None
        
        if content is not None:
            script.content = content
        
        if is_final is not None:
            # 如果设置为最终版本,取消其他版本的最终标记
            if is_final:
                db.query(Script).filter(
                    and_(
                        Script.project_id == script.project_id,
                        Script.script_id != script_id
                    )
                ).update({"is_final": False})
            
            script.is_final = is_final
        
        db.commit()
        db.refresh(script)
        
        return script
    
    @staticmethod
    def delete_script(
        db: Session,
        script_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """删除脚本"""
        script = ScriptService.get_script(db, script_id, user_id)
        
        if not script:
            return False
        
        db.delete(script)
        db.commit()
        
        return True
