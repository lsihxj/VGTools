"""
通义千问文本生成适配器
"""
from typing import Dict, Any, Optional
import dashscope
from dashscope import Generation
from app.services.ai_adapters.base import TextModelAdapter


class TongyiAdapter(TextModelAdapter):
    """通义千问适配器"""
    
    def __init__(self, api_key: str, model_name: str = "qwen-turbo", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = model_name
        dashscope.api_key = api_key
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            # 简单测试请求
            response = Generation.call(
                model=self.model_name,
                prompt="测试连接",
                max_tokens=10
            )
            return response.status_code == 200
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
            
            response = Generation.call(
                model=self.model_name,
                messages=messages,
                result_format='message',
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            if response.status_code == 200:
                output = response.output
                return {
                    "success": True,
                    "text": output.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": output.usage.input_tokens,
                        "completion_tokens": output.usage.output_tokens,
                        "total_tokens": output.usage.total_tokens
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"API返回错误: {response.code} - {response.message}"
                }
                
        except Exception as e:
            return self.handle_error(e)
