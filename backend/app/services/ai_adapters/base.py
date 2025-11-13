"""
AI模型适配器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Iterator


class BaseModelAdapter(ABC):
    """AI模型适配器基类"""
    
    def __init__(self, api_key: str, api_endpoint: Optional[str] = None, **kwargs):
        """
        初始化适配器
        
        Args:
            api_key: API密钥
            api_endpoint: API端点URL
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.config = kwargs
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **params) -> Dict[str, Any]:
        """
        生成内容
        
        Args:
            prompt: 提示词
            **params: 生成参数
            
        Returns:
            Dict: 生成结果
        """
        pass
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 异常对象
            
        Returns:
            Dict: 错误响应
        """
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__
        }


class TextModelAdapter(BaseModelAdapter):
    """文本生成模型适配器基类"""
    
    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果 {"text": str, "usage": dict}
        """
        pass
    
    def stream_generate(self, prompt: str, **params) -> Iterator[str]:
        """
        流式生成(可选实现)
        
        Args:
            prompt: 提示词
            **params: 生成参数
            
        Yields:
            str: 生成的文本片段
        """
        raise NotImplementedError("Stream generation not supported")


class ImageModelAdapter(BaseModelAdapter):
    """图像生成模型适配器基类"""
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 图像描述
            width: 图像宽度
            height: 图像高度
            num_images: 生成数量
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果 {"images": [{"url": str, "b64": str}]}
        """
        pass
    
    def img2img(
        self,
        image_data: bytes,
        prompt: str,
        strength: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图生图(可选实现)
        
        Args:
            image_data: 原始图像数据
            prompt: 修改描述
            strength: 变化强度
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果
        """
        raise NotImplementedError("Image-to-image not supported")


class VideoModelAdapter(BaseModelAdapter):
    """视频生成模型适配器基类"""
    
    @abstractmethod
    def generate_video(
        self,
        prompt: str,
        duration: float = 5.0,
        fps: int = 30,
        width: int = 1280,
        height: int = 720,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频
        
        Args:
            prompt: 视频描述
            duration: 视频时长(秒)
            fps: 帧率
            width: 视频宽度
            height: 视频高度
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果 {"task_id": str, "status": str}
        """
        pass
    
    @abstractmethod
    def check_status(self, task_id: str) -> Dict[str, Any]:
        """
        检查视频生成状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 状态信息 {"status": str, "progress": int, "video_url": str}
        """
        pass
