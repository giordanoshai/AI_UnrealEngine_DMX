# aetherlight/database/auth_manager.py
"""
Auth 认证管理器 (单机模式 dummy 实现)
"""
from typing import Optional, Dict

# 默认本地用户 ID
DEFAULT_USER_ID = 'local-user'


class AuthManager:
    """
    认证管理器 (Dummy)
    
    单机模式下总是返回默认用户。
    """
    
    def __init__(self):
        pass
    
    def sign_up(self, email: str, password: str, metadata: Optional[Dict] = None) -> Optional[Dict]:
        return {"id": DEFAULT_USER_ID, "email": email}
    
    def sign_in(self, email: str, password: str) -> Optional[Dict]:
        return {"id": DEFAULT_USER_ID, "email": email}
    
    def sign_out(self) -> bool:
        return True
    
    def get_current_user(self) -> Optional[Dict]:
        return {"id": DEFAULT_USER_ID, "email": "local@admin"}
    
    def get_current_user_id(self) -> str:
        return DEFAULT_USER_ID
    
    def is_authenticated(self) -> bool:
        return True
    
    def get_access_token(self) -> Optional[str]:
        return "dummy-token"
    
    def refresh_session(self) -> bool:
        return True


# 全局认证管理器实例
_auth_manager = AuthManager()


def get_auth_manager() -> AuthManager:
    """获取全局认证管理器实例"""
    return _auth_manager
