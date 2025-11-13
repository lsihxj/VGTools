"""
百度文心一言适配器
"""
from typing import Dict, Any, Optional
import qianfan
from app.services.ai_adapters.base import TextModelAdapter


class BaiduAdapter(TextModelAdapter):
    """百度文心适配器"""
    
    def __init__(self, api_key: str, secret_key: str, model_name: str = "ERNIE-Bot-turbo", **kwargs):
        super().__init__(api_key, **kwargs)
        self.secret_key = secret_key
        self.model_name = model_name
        self.client = qianfan.ChatCompletion()
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            response = self.client.do(
                model=self.model_name,
                messages=[{"role": "user", "content": "测试"}],
                api_key=self.api_key,
                secret_key=self.secret_key
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
            
            response = self.client.do(
                model=self.model_name,
                messages=messages,
                api_key=self.api_key,
                secret_key=self.secret_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "success": True,
                "text": response["result"],
                "usage": {
                    "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": response.get("usage", {}).get("total_tokens", 0)
                }
            }
                
        except Exception as e:
            return self.handle_error(e)
