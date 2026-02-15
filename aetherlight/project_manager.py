"""
AetherLight Pro - 项目管理器

管理 DMX 项目配置文件 (.json)，每个项目包含:
- 项目元数据 (名称、创建时间等)
- MVR 文件引用
- Fixture 列表及其 GDTF 链接关系

项目文件存储在 projects/ 目录下。
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import Fixture, FixtureGroup

logger = logging.getLogger(__name__)


class ProjectError(Exception):
    """项目管理异常"""
    pass


@dataclass
class ProjectInfo:
    """项目元数据"""
    uuid: str
    name: str
    created_at: str
    modified_at: str


@dataclass
class Project:
    """DMX 项目数据模型。
    
    一个项目对应一套完整的 DMX 配置:
    - 项目基本信息
    - MVR 文件路径
    - 所有 Fixture 及其 GDTF 链接
    - 灯具分组
    
    Attributes:
        project_info: 项目元数据
        mvr_file: MVR 文件路径
        fixtures: Fixture 列表
        groups: FixtureGroup 列表
        file_path: 项目 JSON 文件路径
    """
    project_info: ProjectInfo
    mvr_file: str = ""
    fixtures: List[Fixture] = field(default_factory=list)
    groups: List[FixtureGroup] = field(default_factory=list)
    file_path: str = ""
    
    def to_dict(self) -> dict:
        """转换为可序列化的字典"""
        return {
            "project_info": asdict(self.project_info),
            "mvr_file": self.mvr_file,
            "fixtures": [self._fixture_to_dict(f) for f in self.fixtures],
            "groups": [g.to_dict() for g in self.groups],
        }
    
    @staticmethod
    def _fixture_to_dict(fixture: Fixture) -> dict:
        """将 Fixture 转换为可序列化的字典 (不包含运行时对象)"""
        return {
            "uuid": fixture.uuid,
            "name": fixture.name,
            "fixture_id": fixture.fixture_id,
            "unit_number": fixture.unit_number,
            "universe": fixture.universe,
            "address": fixture.address,
            "position": list(fixture.position),
            "gdtf_spec": fixture.gdtf_spec,
            "gdtf_mode": fixture.gdtf_mode,
        }
    
    @staticmethod
    def from_dict(data: dict) -> Project:
        """从字典恢复 Project 对象"""
        import uuid as uuid_lib
        info_data = data["project_info"]
        if "uuid" not in info_data:
            info_data["uuid"] = str(uuid_lib.uuid4())
            
        project_info = ProjectInfo(**info_data)
        
        fixtures = [
            Fixture(
                uuid=f["uuid"],
                name=f["name"],
                fixture_id=f.get("fixture_id", ""),
                unit_number=f.get("unit_number", 0),
                universe=f.get("universe", 0),
                address=f.get("address", 1),
                position=tuple(f.get("position", [0.0, 0.0, 0.0])),
                gdtf_spec=f.get("gdtf_spec", ""),
                gdtf_mode=f.get("gdtf_mode", ""),
            )
            for f in data.get("fixtures", [])
        ]
        
        groups = [
            FixtureGroup.from_dict(g)
            for g in data.get("groups", [])
        ]
        
        return Project(
            project_info=project_info,
            mvr_file=data.get("mvr_file", ""),
            fixtures=fixtures,
            groups=groups,
        )


class ProjectManager:
    """项目管理器 — 管理所有 DMX 项目的创建、加载、保存。
    
    项目文件统一存储在 projects/ 目录下，格式为 .json。
    
    Example:
        >>> manager = ProjectManager()
        >>> project = manager.create_project("演唱会主舞台")
        >>> project.mvr_file = "path/to/stage.mvr"
        >>> manager.save_project(project)
        >>> loaded = manager.load_project("演唱会主舞台")
    """
    
    def __init__(self, projects_dir: str = "projects") -> None:
        """初始化项目管理器。
        
        Args:
            projects_dir: 项目文件存储目录 (默认为 "projects")
        """
        self.projects_dir = Path(projects_dir).resolve()
        self.projects_dir.mkdir(exist_ok=True)
        logger.info("项目管理器已初始化: %s", self.projects_dir)
    
    def create_project(self, name: str) -> Project:
        """创建新项目。
        
        Args:
            name: 项目名称
        
        Returns:
            新创建的 Project 对象
        
        Raises:
            ProjectError: 项目已存在
        """
        # 检查是否已存在同名项目
        file_path = self._get_project_path(name)
        if file_path.exists():
            raise ProjectError(f"项目已存在: {name}")
        
        now = datetime.now().isoformat()
        import uuid
        project_uuid = str(uuid.uuid4())
        
        project_info = ProjectInfo(
            name=name,
            uuid=project_uuid,
            created_at=now,
            modified_at=now,
        )
        
        project = Project(
            project_info=project_info,
            file_path=str(file_path),
        )
        
        logger.info("项目已创建: %s", name)
        return project
    
    def save_project(self, project: Project) -> None:
        """保存项目到 JSON 文件。
        
        Args:
            project: 要保存的 Project 对象
        
        Raises:
            ProjectError: 保存失败
        """
        if not project.file_path:
            project.file_path = str(self._get_project_path(project.project_info.name))
        
        # 更新修改时间
        project.project_info.modified_at = datetime.now().isoformat()
        
        try:
            file_path = Path(project.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info("项目已保存: %s (%s)", project.project_info.name, file_path)
            
        except (OSError, json.JSONDecodeError) as e:
            raise ProjectError(f"保存项目失败: {e}")
    
    def load_project(self, name: str) -> Project:
        """加载现有项目。
        
        Args:
            name: 项目名称
        
        Returns:
            加载的 Project 对象
        
        Raises:
            ProjectError: 项目不存在或加载失败
        """
        file_path = self._get_project_path(name)
        
        if not file_path.exists():
            raise ProjectError(f"项目不存在: {name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = Project.from_dict(data)
            project.file_path = str(file_path)
            
            logger.info(
                "项目已加载: %s (%d 个灯具)",
                project.project_info.name, len(project.fixtures)
            )
            return project
            
        except (OSError, json.JSONDecodeError, KeyError) as e:
            raise ProjectError(f"加载项目失败: {e}")
    
    def list_projects(self) -> List[str]:
        """列出所有项目名称。
        
        Returns:
            项目名称列表 (按修改时间倒序)
        """
        project_files = list(self.projects_dir.glob("*.json"))
        
        # 按修改时间排序 (最新的在前)
        project_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        return [p.stem for p in project_files]
    
    def delete_project(self, name: str) -> bool:
        """删除项目。
        
        Args:
            name: 项目名称
        
        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_project_path(name)
        
        if file_path.exists():
            file_path.unlink()
            logger.info("项目已删除: %s", name)
            return True
        
        return False
    
    def project_exists(self, name: str) -> bool:
        """检查项目是否存在"""
        return self._get_project_path(name).exists()
    
    def _get_project_path(self, name: str) -> Path:
        """获取项目文件路径"""
        # 使用项目名称作为文件名 (移除非法字符)
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-'))
        return self.projects_dir / f"{safe_name}.json"
    
    def get_project_info(self, name: str) -> Optional[ProjectInfo]:
        """获取项目信息 (不加载完整项目)。
        
        Args:
            name: 项目名称
        
        Returns:
            ProjectInfo 或 None (项目不存在)
        """
        file_path = self._get_project_path(name)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProjectInfo(**data["project_info"])
        except (OSError, json.JSONDecodeError, KeyError):
            return None
