"""
分镜头生成和管理服务
"""
import uuid
import re
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.project import Storyboard, Script, VideoProject
from app.models.ai_model import AIModelConfig
from app.services.ai_adapters.base import TextModelAdapter
from app.services.ai_adapters.tongyi import TongyiAdapter
from app.services.ai_adapters.zhipu import ZhipuAdapter
from app.services.ai_adapters.baidu import BaiduAdapter
from app.utils.encryption import decrypt_string


class StoryboardService:
    """分镜服务类"""
    
    # 默认系统提示词
    DEFAULT_SYSTEM_PROMPT = """你是一位专业的视频分镜师。
你需要根据视频脚本,将其拆分为详细的分镜头剧本。

分镜要求:
1. 每个分镜包含清晰的画面描述、人物动作、对话内容
2. 标注镜头类型(特写/中景/全景/远景等)
3. 标注预计时长(秒)
4. 保持逻辑连贯,镜头切换自然
5. 适合后续的图像和视频生成

输出格式为JSON数组,每个分镜包含以下字段:
{
  "sequence_number": 分镜序号(从1开始),
  "content": "分镜内容描述",
  "duration": 预计时长(秒,浮点数)
}

请严格按照JSON格式输出,不要包含任何其他文字。"""
    
    @staticmethod
    def _get_adapter(config: AIModelConfig) -> TextModelAdapter:
        """根据配置获取对应的AI适配器"""
        api_key = decrypt_string(config.api_key)
        
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
    def _parse_storyboards(text: str) -> List[Dict[str, Any]]:
        """解析AI生成的分镜内容"""
        try:
            # 尝试直接解析JSON
            # 移除可能的markdown代码块标记
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*$', '', text)
            text = text.strip()
            
            storyboards = json.loads(text)
            
            if not isinstance(storyboards, list):
                raise ValueError("分镜数据应该是数组格式")
            
            # 验证每个分镜的字段
            validated = []
            for idx, sb in enumerate(storyboards, 1):
                if not isinstance(sb, dict):
                    continue
                
                validated.append({
                    "sequence_number": sb.get("sequence_number", idx),
                    "content": str(sb.get("content", "")).strip(),
                    "duration": float(sb.get("duration", 5.0))
                })
            
            return validated
            
        except json.JSONDecodeError:
            # 如果JSON解析失败,尝试简单的文本解析
            # 按行分割,寻找编号模式
            lines = text.strip().split('\n')
            storyboards = []
            current_sb = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检查是否是新的分镜(以数字开头)
                match = re.match(r'^(\d+)[\.、]\s*(.+)', line)
                if match:
                    if current_sb:
                        storyboards.append(current_sb)
                    
                    current_sb = {
                        "sequence_number": int(match.group(1)),
                        "content": match.group(2),
                        "duration": 5.0
                    }
                elif current_sb:
                    current_sb["content"] += " " + line
            
            if current_sb:
                storyboards.append(current_sb)
            
            if not storyboards:
                raise ValueError("无法解析分镜内容")
            
            return storyboards
    
    @staticmethod
    def generate_storyboards(
        db: Session,
        user_id: uuid.UUID,
        script_id: uuid.UUID,
        model_config_id: uuid.UUID,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 3000
    ) -> Dict[str, Any]:
        """
        生成分镜头剧本
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            script_id: 脚本ID
            model_config_id: AI模型配置ID
            system_prompt: 自定义系统提示词(可选)
            temperature: 温度参数
            max_tokens: 最大生成长度
            
        Returns:
            包含分镜列表和使用统计的字典
        """
        # 获取脚本
        script = db.query(Script).join(VideoProject).filter(
            and_(
                Script.script_id == script_id,
                VideoProject.user_id == user_id
            )
        ).first()
        
        if not script:
            raise ValueError("脚本不存在或无权访问")
        
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
            StoryboardService.DEFAULT_SYSTEM_PROMPT
        )
        
        # 构建用户提示词
        user_prompt = f"视频脚本:\n{script.content}\n\n请将以上脚本拆分为详细的分镜头剧本。"
        
        # 获取适配器并生成分镜
        adapter = StoryboardService._get_adapter(config)
        
        result = adapter.generate_text(
            prompt=user_prompt,
            system_prompt=final_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not result.get("success"):
            raise Exception(f"分镜生成失败: {result.get('error', '未知错误')}")
        
        # 解析分镜内容
        storyboards_data = StoryboardService._parse_storyboards(result["text"])
        
        # 删除该脚本的旧分镜
        db.query(Storyboard).filter(Storyboard.script_id == script_id).delete()
        
        # 创建分镜记录
        storyboards = []
        for sb_data in storyboards_data:
            storyboard = Storyboard(
                script_id=script_id,
                sequence_number=sb_data["sequence_number"],
                content=sb_data["content"],
                duration=sb_data["duration"]
            )
            db.add(storyboard)
            storyboards.append(storyboard)
        
        db.commit()
        
        # 刷新所有对象
        for sb in storyboards:
            db.refresh(sb)
        
        return {
            "storyboards": storyboards,
            "count": len(storyboards),
            "usage": result.get("usage", {}),
            "model_info": {
                "vendor": config.vendor,
                "model_name": config.model_name
            }
        }
    
    @staticmethod
    def get_storyboard(
        db: Session,
        storyboard_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[Storyboard]:
        """获取分镜"""
        storyboard = db.query(Storyboard).join(Script).join(VideoProject).filter(
            and_(
                Storyboard.storyboard_id == storyboard_id,
                VideoProject.user_id == user_id
            )
        ).first()
        
        return storyboard
    
    @staticmethod
    def get_storyboards_by_script(
        db: Session,
        script_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[Storyboard]:
        """获取脚本的所有分镜"""
        storyboards = db.query(Storyboard).join(Script).join(VideoProject).filter(
            and_(
                Storyboard.script_id == script_id,
                VideoProject.user_id == user_id
            )
        ).order_by(Storyboard.sequence_number).all()
        
        return storyboards
    
    @staticmethod
    def create_storyboard(
        db: Session,
        user_id: uuid.UUID,
        script_id: uuid.UUID,
        sequence_number: int,
        content: str,
        duration: Optional[float] = None
    ) -> Storyboard:
        """手动创建分镜"""
        # 验证脚本
        script = db.query(Script).join(VideoProject).filter(
            and_(
                Script.script_id == script_id,
                VideoProject.user_id == user_id
            )
        ).first()
        
        if not script:
            raise ValueError("脚本不存在或无权访问")
        
        storyboard = Storyboard(
            script_id=script_id,
            sequence_number=sequence_number,
            content=content,
            duration=duration
        )
        
        db.add(storyboard)
        db.commit()
        db.refresh(storyboard)
        
        return storyboard
    
    @staticmethod
    def update_storyboard(
        db: Session,
        storyboard_id: uuid.UUID,
        user_id: uuid.UUID,
        sequence_number: Optional[int] = None,
        content: Optional[str] = None,
        duration: Optional[float] = None
    ) -> Optional[Storyboard]:
        """更新分镜"""
        storyboard = StoryboardService.get_storyboard(db, storyboard_id, user_id)
        
        if not storyboard:
            return None
        
        if sequence_number is not None:
            storyboard.sequence_number = sequence_number
        
        if content is not None:
            storyboard.content = content
        
        if duration is not None:
            storyboard.duration = duration
        
        db.commit()
        db.refresh(storyboard)
        
        return storyboard
    
    @staticmethod
    def delete_storyboard(
        db: Session,
        storyboard_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """删除分镜"""
        storyboard = StoryboardService.get_storyboard(db, storyboard_id, user_id)
        
        if not storyboard:
            return False
        
        db.delete(storyboard)
        db.commit()
        
        return True
