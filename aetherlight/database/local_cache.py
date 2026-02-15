# aetherlight/database/local_cache.py
"""
本地 JSON 缓存系统
支持离线 CRUD 操作和时间戳跟踪
"""
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import uuid


class LocalCache:
    """
    本地缓存管理器
    
    使用 JSON 文件存储 Effects, Projects, CueLists
    每条记录包含时间戳和同步状态
    """
    
    def __init__(self, cache_dir: str = "data"):
        """
        初始化本地缓存
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 表文件映射
        self.tables = {
            "effects": self.cache_dir / "effects.json",
            "projects": self.cache_dir / "projects.json",
            "cue_lists": self.cache_dir / "cue_lists.json",
            "fixture_profiles": self.cache_dir / "fixture_profiles.json",
            "gdtf_profiles": self.cache_dir / "gdtf_profiles.json"
        }
        
        # 确保所有表文件存在
        for table_path in self.tables.values():
            if not table_path.exists():
                self._save_table(table_path, {"items": []})
    
    def _load_table(self, table_path: Path) -> Dict:
        """加载表数据"""
        try:
            with open(table_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载表失败 {table_path}: {e}")
            return {"items": []}
    
    def _save_table(self, table_path: Path, data: Dict) -> bool:
        """保存表数据"""
        try:
            with open(table_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存表失败 {table_path}: {e}")
            return False
    
    def _add_metadata(self, item: Dict) -> Dict:
        """
        添加元数据到记录
        
        Args:
            item: 原始记录
            
        Returns:
            添加元数据后的记录
        """
        now = datetime.utcnow().isoformat() + "Z"
        
        # 生成 ID（如果没有）
        if "id" not in item:
            item["id"] = str(uuid.uuid4())
        
        # 添加时间戳
        if "created_at" not in item:
            item["created_at"] = now
        item["updated_at"] = now
        
        # 添加同步状态
        item["sync_status"] = "pending"
        item["synced_at"] = None
        
        return item
    
    def create(self, table_name: str, data: Dict) -> Optional[Dict]:
        """
        创建记录
        
        Args:
            table_name: 表名 (effects, projects, cue_lists)
            data: 记录数据
            
        Returns:
            创建的记录，失败返回 None
        """
        if table_name not in self.tables:
            print(f"❌ 未知表: {table_name}")
            return None
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        # 添加元数据
        item = self._add_metadata(data.copy())
        
        # 添加到列表
        table_data["items"].append(item)
        
        # 保存
        if self._save_table(table_path, table_data):
            print(f"✅ 本地创建成功: {table_name}/{item['id']}")
            return item
        
        return None
    
    def get(self, table_name: str, item_id: str) -> Optional[Dict]:
        """
        获取单条记录
        
        Args:
            table_name: 表名
            item_id: 记录 ID
            
        Returns:
            记录，不存在返回 None
        """
        if table_name not in self.tables:
            return None
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        for item in table_data["items"]:
            if item.get("id") == item_id:
                return item
        
        return None
    
    def get_by_field(self, table_name: str, field: str, value: Any) -> Optional[Dict]:
        """
        根据字段查询记录
        
        Args:
            table_name: 表名
            field: 字段名
            value: 字段值
            
        Returns:
            第一条匹配记录，不存在返回 None
        """
        if table_name not in self.tables:
            return None
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        for item in table_data["items"]:
            if item.get(field) == value:
                return item
        
        return None
    
    def list(self, table_name: str, filter_func=None) -> List[Dict]:
        """
        列出所有记录
        
        Args:
            table_name: 表名
            filter_func: 过滤函数（可选）
            
        Returns:
            记录列表
        """
        if table_name not in self.tables:
            return []
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        items = table_data["items"]
        
        if filter_func:
            items = [item for item in items if filter_func(item)]
        
        # 按创建时间倒序
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return items
    
    def update(self, table_name: str, item_id: str, updates: Dict) -> Optional[Dict]:
        """
        更新记录
        
        Args:
            table_name: 表名
            item_id: 记录 ID
            updates: 更新字段
            
        Returns:
            更新后的记录，失败返回 None
        """
        if table_name not in self.tables:
            return None
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        for i, item in enumerate(table_data["items"]):
            if item.get("id") == item_id:
                # 更新字段
                item.update(updates)
                
                # 更新时间戳和同步状态
                item["updated_at"] = datetime.utcnow().isoformat() + "Z"
                item["sync_status"] = "pending"
                
                # 保存
                if self._save_table(table_path, table_data):
                    print(f"✅ 本地更新成功: {table_name}/{item_id}")
                    return item
                break
        
        return None
    
    def delete(self, table_name: str, item_id: str) -> bool:
        """
        删除记录
        
        Args:
            table_name: 表名
            item_id: 记录 ID
            
        Returns:
            成功返回 True
        """
        if table_name not in self.tables:
            return False
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        original_count = len(table_data["items"])
        table_data["items"] = [
            item for item in table_data["items"]
            if item.get("id") != item_id
        ]
        
        if len(table_data["items"]) < original_count:
            if self._save_table(table_path, table_data):
                print(f"✅ 本地删除成功: {table_name}/{item_id}")
                return True
        
        return False
    
    def get_pending_items(self, table_name: str) -> List[Dict]:
        """
        获取待同步的记录
        
        Args:
            table_name: 表名
            
        Returns:
            待同步记录列表
        """
        return self.list(table_name, lambda x: x.get("sync_status") == "pending")
    
    def mark_synced(self, table_name: str, item_id: str) -> bool:
        """
        标记记录为已同步
        
        Args:
            table_name: 表名
            item_id: 记录 ID
            
        Returns:
            成功返回 True
        """
        if table_name not in self.tables:
            return False
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        for item in table_data["items"]:
            if item.get("id") == item_id:
                item["sync_status"] = "synced"
                item["synced_at"] = datetime.utcnow().isoformat() + "Z"
                return self._save_table(table_path, table_data)
        
        return False
    
    def mark_conflict(self, table_name: str, item_id: str) -> bool:
        """
        标记记录为冲突
        
        Args:
            table_name: 表名
            item_id: 记录 ID
            
        Returns:
            成功返回 True
        """
        if table_name not in self.tables:
            return False
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        for item in table_data["items"]:
            if item.get("id") == item_id:
                item["sync_status"] = "conflict"
                return self._save_table(table_path, table_data)
        
        return False
    
    def upsert(self, table_name: str, item: Dict) -> Optional[Dict]:
        """
        插入或更新记录（用于同步）
        
        Args:
            table_name: 表名
            item: 完整记录
            
        Returns:
            记录，失败返回 None
        """
        if table_name not in self.tables:
            return None
        
        table_path = self.tables[table_name]
        table_data = self._load_table(table_path)
        
        item_id = item.get("id")
        if not item_id:
            print("❌ Upsert 失败: 缺少 ID")
            return None
        
        # 查找现有记录
        for i, existing in enumerate(table_data["items"]):
            if existing.get("id") == item_id:
                # 更新
                table_data["items"][i] = item
                if self._save_table(table_path, table_data):
                    return item
                return None
        
        # 插入
        table_data["items"].append(item)
        if self._save_table(table_path, table_data):
            return item
        
        return None


# 全局缓存实例
_local_cache = LocalCache()


def get_local_cache() -> LocalCache:
    """获取全局本地缓存实例"""
    return _local_cache
