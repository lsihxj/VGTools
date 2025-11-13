"""
可灵AI视频生成适配器
"""
from typing import Dict, Any
import httpx
import time
from app.services.ai_adapters.base import VideoModelAdapter


class KeLingAdapter(VideoModelAdapter):
    """可灵AI适配器"""
    
    def __init__(self, api_key: str, api_endpoint: str, **kwargs):
        super().__init__(api_key, api_endpoint, **kwargs)
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            response = httpx.get(
                f"{self.api_endpoint}/api/v1/status",
                headers=self.headers,
                timeout=10.0
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, **params) -> Dict[str, Any]:
        """生成内容"""
        return self.generate_video(prompt, **params)
    
    def generate_video(
        self,
        prompt: str,
        duration: float = 5.0,
        fps: int = 30,
        width: int = 1280,
        height: int = 720,
        **kwargs
    ) -> Dict[str, Any]:
        """生成视频"""
        try:
            payload = {
                "prompt": prompt,
                "duration": duration,
                "fps": fps,
                "width": width,
                "height": height,
                "mode": kwargs.get("mode", "standard"),
                "seed": kwargs.get("seed", -1)
            }
            
            response = httpx.post(
                f"{self.api_endpoint}/api/v1/videos/generate",
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "task_id": data.get("task_id"),
                    "status": "pending"
                }
            else:
                return {
                    "success": False,
                    "error": f"API返回错误: {response.status_code}"
                }
                
        except Exception as e:
            return self.handle_error(e)
    
    def check_status(self, task_id: str) -> Dict[str, Any]:
        """检查视频生成状态"""
        try:
            response = httpx.get(
                f"{self.api_endpoint}/api/v1/videos/status/{task_id}",
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                result = {
                    "success": True,
                    "status": status,
                    "progress": data.get("progress", 0)
                }
                
                if status == "completed":
                    result["video_url"] = data.get("video_url")
                elif status == "failed":
                    result["error"] = data.get("error", "未知错误")
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"API返回错误: {response.status_code}"
                }
                
        except Exception as e:
            return self.handle_error(e)
    
    def wait_for_completion(self, task_id: str, max_wait: int = 600, check_interval: int = 5) -> Dict[str, Any]:
        """等待视频生成完成"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self.check_status(task_id)
            
            if not result.get("success"):
                return result
            
            status = result.get("status")
            if status == "completed":
                return result
            elif status == "failed":
                return result
            
            time.sleep(check_interval)
        
        return {
            "success": False,
            "error": "等待超时",
            "status": "timeout"
        }
