# aetherlight/database/config.py
"""
配置管理模块
处理认证状态、离线模式、缓存路径等配置
"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "offline_mode": False,
    "cache_dir": ".cache",
    "auto_sync": True,
    "sync_interval": 300,  # 5分钟
    "session": None,
    "user_id": None
}


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 .cache/config.json
        """
        if config_path is None:
            cache_dir = Path(".cache")
            cache_dir.mkdir(exist_ok=True)
            config_path = cache_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Returns:
            配置字典
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    print(f"✅ 已加载配置: {self.config_path}")
            except Exception as e:
                print(f"⚠️  加载配置失败: {e}, 使用默认配置")
        
        return self.config
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            成功返回 True
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
            save: 是否立即保存
            
        Returns:
            成功返回 True
        """
        self.config[key] = value
        if save:
            return self.save()
        return True
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        批量更新配置
        
        Args:
            updates: 更新字典
            save: 是否立即保存
            
        Returns:
            成功返回 True
        """
        self.config.update(updates)
        if save:
            return self.save()
        return True
    
    # 快捷访问方法
    
    @property
    def offline_mode(self) -> bool:
        """是否离线模式"""
        return self.config.get("offline_mode", False)
    
    @offline_mode.setter
    def offline_mode(self, value: bool):
        """设置离线模式"""
        self.set("offline_mode", value)
    
    @property
    def cache_dir(self) -> Path:
        """缓存目录路径"""
        return Path(self.config.get("cache_dir", ".cache"))
    
    @property
    def session(self) -> Optional[Dict]:
        """当前 session"""
        return self.config.get("session")
    
    @session.setter
    def session(self, value: Optional[Dict]):
        """设置 session"""
        self.set("session", value)
    
    @property
    def user_id(self) -> Optional[str]:
        """当前用户 ID"""
        return self.config.get("user_id")
    
    @user_id.setter
    def user_id(self, value: Optional[str]):
        """设置用户 ID"""
        self.set("user_id", value)
    
    def clear_session(self):
        """清除 session"""
        self.update({
            "session": None,
            "user_id": None
        })


# 全局配置实例
_config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return _config
