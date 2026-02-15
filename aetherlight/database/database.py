# aetherlight/database/database.py
"""
本地数据库操作模块
使用本地 JSON 缓存存储 Effects, Projects, CueLists
不再依赖 Supabase
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

# 延迟导入以避免循环依赖
_local_cache = None
_config = None


def _get_cache():
    """延迟加载 LocalCache"""
    global _local_cache
    if _local_cache is None:
        try:
            from aetherlight.database.local_cache import get_local_cache
            _local_cache = get_local_cache()
        except ImportError:
            pass
    return _local_cache


def _get_config():
    """延迟加载 Config"""
    global _config
    if _config is None:
        try:
            from aetherlight.database.config import get_config
            _config = get_config()
        except ImportError:
            pass
    return _config


DEFAULT_USER_ID = 'local-user'


def get_current_user_id() -> str:
    """获取当前用户 ID (单机模式返回固定 ID)"""
    return DEFAULT_USER_ID


# ========================================
# Effects CRUD 操作
# ========================================

def create_effect(effect_name: str, description: str, primitives: List[Dict], duration: float = 10.0, user_id: Optional[str] = None) -> Optional[Dict]:
    """
    创建新的灯光效果
    """
    data = {
        "effect_name": effect_name,
        "description": description,
        "primitives": primitives,
        "duration": duration,
        "user_id": user_id or DEFAULT_USER_ID,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    cache = _get_cache()
    if cache:
        return cache.create("effects", data)
    return None


def get_effect(effect_id: Optional[str] = None, effect_name: Optional[str] = None) -> Optional[Dict]:
    """
    获取单个效果
    """
    cache = _get_cache()
    if not cache:
        return None

    if effect_id:
        return cache.get("effects", effect_id)
    elif effect_name:
        return cache.get_by_field("effects", "effect_name", effect_name)
    return None


def list_effects() -> List[Dict]:
    """
    列出所有效果
    """
    cache = _get_cache()
    if cache:
        return cache.list("effects")
    return []


def update_effect(effect_id: str, **kwargs) -> Optional[Dict]:
    """
    更新效果
    """
    kwargs["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    cache = _get_cache()
    if cache:
        return cache.update("effects", effect_id, kwargs)
    return None


def delete_effect(effect_id: str) -> bool:
    """
    删除效果
    """
    cache = _get_cache()
    if cache:
        return cache.delete("effects", effect_id)
    return False


# ========================================
# Projects CRUD 操作
# ========================================

def create_project(project_name: str, fixtures: List[Dict], channel_config: Optional[Dict] = None, user_id: Optional[str] = None) -> Optional[Dict]:
    """
    创建新项目
    """
    data = {
        "project_name": project_name,
        "fixtures": fixtures,
        "channel_config": channel_config,
        "user_id": user_id or DEFAULT_USER_ID,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    cache = _get_cache()
    if cache:
        return cache.create("projects", data)
    return None


def get_project(project_id: Optional[str] = None, project_name: Optional[str] = None) -> Optional[Dict]:
    """
    获取单个项目
    """
    cache = _get_cache()
    if not cache:
        return None

    if project_id:
        return cache.get("projects", project_id)
    elif project_name:
        return cache.get_by_field("projects", "project_name", project_name)
    return None


def list_projects() -> List[Dict]:
    """
    列出所有项目
    """
    cache = _get_cache()
    if cache:
        return cache.list("projects")
    return []


def update_project(project_id: str, **kwargs) -> Optional[Dict]:
    """
    更新项目
    """
    kwargs["updated_at"] = datetime.utcnow().isoformat() + "Z"

    cache = _get_cache()
    if cache:
        return cache.update("projects", project_id, kwargs)
    return None


def delete_project(project_id: str) -> bool:
    """
    删除项目
    """
    cache = _get_cache()
    if cache:
        return cache.delete("projects", project_id)
    return False


# ========================================
# Cue Lists CRUD 操作
# ========================================

def create_cue_list(cue_list_name: str, project_id: str, cues: List[Dict], loop: bool = False, user_id: Optional[str] = None) -> Optional[Dict]:
    """
    创建新的 cue list
    """
    data = {
        "cue_list_name": cue_list_name,
        "project_id": project_id,
        "cues": cues,
        "loop": loop,
        "user_id": user_id or DEFAULT_USER_ID,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    cache = _get_cache()
    if cache:
        return cache.create("cue_lists", data)
    return None


def get_cue_list(cue_list_id: Optional[str] = None, cue_list_name: Optional[str] = None) -> Optional[Dict]:
    """
    获取单个 cue list
    """
    cache = _get_cache()
    if not cache:
        return None

    if cue_list_id:
        return cache.get("cue_lists", cue_list_id)
    elif cue_list_name:
        return cache.get_by_field("cue_lists", "cue_list_name", cue_list_name)
    return None


def list_cue_lists(project_id: Optional[str] = None) -> List[Dict]:
    """
    列出 cue lists
    """
    cache = _get_cache()
    if not cache:
        return []

    if project_id:
        return cache.list("cue_lists", lambda x: x.get("project_id") == project_id)
    return cache.list("cue_lists")


def update_cue_list(cue_list_id: str, **kwargs) -> Optional[Dict]:
    """
    更新 cue list
    """
    kwargs["updated_at"] = datetime.utcnow().isoformat() + "Z"

    cache = _get_cache()
    if cache:
        return cache.update("cue_lists", cue_list_id, kwargs)
    return None


def delete_cue_list(cue_list_id: str) -> bool:
    """
    删除 cue list
    """
    cache = _get_cache()
    if cache:
        return cache.delete("cue_lists", cue_list_id)
    return False


# ========================================
# GDTF Profiles CRUD 操作
# ========================================

def create_fixture_profile(manufacturer: str, name: str, modes: Dict, file_path: Optional[str] = None, user_id: Optional[str] = None) -> Optional[Dict]:
    """
    创建 Fixture Profile
    """
    data = {
        "manufacturer": manufacturer,
        "name": name,
        "channels": modes,
        "file_path": file_path,
        "user_id": user_id or DEFAULT_USER_ID,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    cache = _get_cache()
    if cache:
        return cache.create("fixture_profiles", data)
    return None


def get_fixture_profile(profile_id: Optional[str] = None, name: Optional[str] = None) -> Optional[Dict]:
    """获取 Fixture Profile"""
    cache = _get_cache()
    if not cache:
        return None

    if profile_id:
        return cache.get("fixture_profiles", profile_id)
    elif name:
        return cache.get_by_field("fixture_profiles", "name", name)
    return None


def list_fixture_profiles() -> List[Dict]:
    """列出所有 Fixture Profiles"""
    cache = _get_cache()
    if cache:
        return cache.list("fixture_profiles")
    return []


def delete_fixture_profile(profile_id: str) -> bool:
    """删除 Fixture Profile"""
    cache = _get_cache()
    if cache:
        return cache.delete("fixture_profiles", profile_id)
    return False
