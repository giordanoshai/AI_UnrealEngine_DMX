# aetherlight/database/sync_manager.py
"""
Sync Manager (单机模式 dummy 实现)
"""
from typing import Dict

class SyncManager:
    """
    同步管理器 (Dummy)
    
    单机模式下不进行任何同步。
    """
    def __init__(self):
        pass
    
    def sync_all(self) -> Dict:
        return {
            "uploaded": 0,
            "downloaded": 0,
            "conflicts": 0,
            "errors": 0
        }

# 全局同步管理器实例
_sync_manager = SyncManager()

def get_sync_manager() -> SyncManager:
    """获取全局同步管理器实例"""
    return _sync_manager
