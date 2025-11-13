"""
Stable Diffusion图像生成适配器(通过API调用)
"""
from typing import Dict, Any
import httpx
import base64
from app.services.ai_adapters.base import ImageModelAdapter


class StableDiffusionAdapter(ImageModelAdapter):
    """Stable Diffusion适配器"""
    
    def __init__(self, api_key: str, api_endpoint: str, **kwargs):
        super().__init__(api_key, api_endpoint, **kwargs)
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            response = httpx.get(
                f"{self.api_endpoint}/health",
                headers=self.headers,
                timeout=10.0
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, **params) -> Dict[str, Any]:
        """生成内容"""
        return self.generate_image(prompt, **params)
    
    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """生成图像"""
        try:
            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_images": num_images,
                "steps": kwargs.get("steps", 50),
                "guidance_scale": kwargs.get("guidance_scale", 7.5),
                "seed": kwargs.get("seed", -1)
            }
            
            response = httpx.post(
                f"{self.api_endpoint}/v1/generation",
                json=payload,
                headers=self.headers,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "images": data.get("images", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"API返回错误: {response.status_code}"
                }
                
        except Exception as e:
            return self.handle_error(e)
    
    def img2img(
        self,
        image_data: bytes,
        prompt: str,
        strength: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """图生图"""
        try:
            # 将图像转换为base64
            image_b64 = base64.b64encode(image_data).decode()
            
            payload = {
                "prompt": prompt,
                "init_image": image_b64,
                "strength": strength,
                "steps": kwargs.get("steps", 50),
                "guidance_scale": kwargs.get("guidance_scale", 7.5)
            }
            
            response = httpx.post(
                f"{self.api_endpoint}/v1/img2img",
                json=payload,
                headers=self.headers,
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "images": data.get("images", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"API返回错误: {response.status_code}"
                }
                
        except Exception as e:
            return self.handle_error(e)
