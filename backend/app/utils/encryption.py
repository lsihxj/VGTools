"""
数据加密工具(用于加密API Key等敏感信息)
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64


def get_cipher():
    """获取加密器"""
    # 将密钥转换为32字节
    key = settings.ENCRYPTION_KEY.encode()
    if len(key) < 32:
        key = key.ljust(32, b'0')
    else:
        key = key[:32]
    
    # Base64编码
    key_b64 = base64.urlsafe_b64encode(key)
    return Fernet(key_b64)


def encrypt_string(plain_text: str) -> str:
    """加密字符串"""
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(plain_text.encode())
    return encrypted_bytes.decode()


def decrypt_string(encrypted_text: str) -> str:
    """解密字符串"""
    cipher = get_cipher()
    decrypted_bytes = cipher.decrypt(encrypted_text.encode())
    return decrypted_bytes.decode()
