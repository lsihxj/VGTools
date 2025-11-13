"""
智谱AI文本生成适配器
"""
from typing import Dict, Any, Optional
from zhipuai import ZhipuAI
from app.services.ai_adapters.base import TextModelAdapter


class ZhipuAdapter(TextModelAdapter):
    """智谱AI适配器"""
    
    def __init__(self, api_key: str, model_name: str = "glm-4", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = model_name
        self.client = ZhipuAI(api_key=api_key)
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "测试"}],
                max_tokens=10
            )
            return response is not None
        except Exception:
            return False
    
    def generate(self, prompt: str, **params) -> Dict[str, Any]:
        """生成内容"""
        return self.generate_text(prompt, **params)
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """生成文本"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
                
        except Exception as e:
            return self.handle_error(e)
