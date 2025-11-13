"""
模型配置管理服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ai_model import AIModelConfig
from app.utils.encryption import encrypt_string, decrypt_string
import uuid


class ModelConfigService:
    """模型配置管理服务"""
    
    @staticmethod
    def create_config(
        db: Session,
        user_id: uuid.UUID,
        config_name: str,
        vendor: str,
        model_name: str,
        api_key: str,
        api_endpoint: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt_template: Optional[str] = None,
        parameters: dict = None
    ) -> AIModelConfig:
        """创建模型配置"""
        # 加密API Key
        encrypted_api_key = encrypt_string(api_key)
        
        config = AIModelConfig(
            user_id=user_id,
            config_name=config_name,
            vendor=vendor,
            model_name=model_name,
            api_key=encrypted_api_key,
            api_endpoint=api_endpoint,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            parameters=parameters or {}
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return config
    
    @staticmethod
    def get_config(db: Session, config_id: uuid.UUID, user_id: uuid.UUID) -> Optional[AIModelConfig]:
        """获取单个配置"""
        return db.query(AIModelConfig).filter(
            AIModelConfig.config_id == config_id,
            AIModelConfig.user_id == user_id
        ).first()
    
    @staticmethod
    def get_configs(db: Session, user_id: uuid.UUID) -> List[AIModelConfig]:
        """获取用户的所有配置"""
        return db.query(AIModelConfig).filter(
            AIModelConfig.user_id == user_id
        ).all()
    
    @staticmethod
    def update_config(
        db: Session,
        config_id: uuid.UUID,
        user_id: uuid.UUID,
        **kwargs
    ) -> Optional[AIModelConfig]:
        """更新配置"""
        config = ModelConfigService.get_config(db, config_id, user_id)
        if not config:
            return None
        
        # 如果更新API Key，需要加密
        if 'api_key' in kwargs and kwargs['api_key']:
            kwargs['api_key'] = encrypt_string(kwargs['api_key'])
        
        for key, value in kwargs.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)
        
        db.commit()
        db.refresh(config)
        
        return config
    
    @staticmethod
    def delete_config(db: Session, config_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """删除配置"""
        config = ModelConfigService.get_config(db, config_id, user_id)
        if not config:
            return False
        
        db.delete(config)
        db.commit()
        
        return True
    
    @staticmethod
    def get_decrypted_api_key(config: AIModelConfig) -> str:
        """获取解密后的API Key"""
        return decrypt_string(config.api_key)
    
    @staticmethod
    def test_config(config: AIModelConfig, test_prompt: str = "测试") -> dict:
        """测试模型配置"""
        from app.services.ai_adapters.tongyi import TongyiAdapter
        from app.services.ai_adapters.zhipu import ZhipuAdapter
        from app.services.ai_adapters.baidu import BaiduAdapter
        from app.services.ai_adapters.stable_diffusion import StableDiffusionAdapter
        from app.services.ai_adapters.keling import KeLingAdapter
        
        try:
            # 解密API Key
            api_key = decrypt_string(config.api_key)
            
            # 根据厂商创建适配器
            if config.vendor == "tongyi":
                adapter = TongyiAdapter(api_key=api_key, model_name=config.model_name)
            elif config.vendor == "zhipu":
                adapter = ZhipuAdapter(api_key=api_key, model_name=config.model_name)
            elif config.vendor == "baidu":
                # 百度需要secret_key，从parameters中获取
                secret_key = config.parameters.get("secret_key", "")
                adapter = BaiduAdapter(api_key=api_key, secret_key=secret_key, model_name=config.model_name)
            elif config.vendor == "stable_diffusion":
                adapter = StableDiffusionAdapter(api_key=api_key, api_endpoint=config.api_endpoint)
            elif config.vendor == "keling":
                adapter = KeLingAdapter(api_key=api_key, api_endpoint=config.api_endpoint)
            else:
                return {
                    "success": False,
                    "error": f"不支持的厂商: {config.vendor}"
                }
            
            # 验证配置
            is_valid = adapter.validate_config()
            
            if is_valid:
                return {
                    "success": True,
                    "message": "配置有效，连接成功",
                    "vendor": config.vendor,
                    "model": config.model_name
                }
            else:
                return {
                    "success": False,
                    "error": "配置验证失败，请检查API Key和端点"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"测试失败: {str(e)}"
            }
