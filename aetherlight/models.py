"""
AetherLight Pro - 核心数据模型

定义 GDTFProfile 和 Fixture 数据类，
是 GDTF 解析和 MVR 导入的基础数据结构。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class GDTFProfile:
    """GDTF 灯具配置文件 — 从 .gdtf 文件解析而来。

    描述一个灯具类型的所有 DMX 模式及其通道映射，
    是从"高层属性名"到"DMX 通道偏移量"的字典。

    Attributes:
        name: 灯具类型短名称 (e.g. "RotaHead")
        manufacturer: 制造商名称 (e.g. "Epic Games")
        long_name: 灯具完整名称 (e.g. "DMXL_huzhou RotaHead")
        spec_key: 完整 GDTF spec 名, 对应文件名无扩展名,
                  用于与 MVR 中的 <GDTFSpec> 匹配
        modes: {mode_name: {attribute_name: channel_offset}}
               例: {"Mode": {"Pan": 1, "Tilt": 2, "Dimmer": 5}}
        file_path: GDTF 文件的磁盘路径
    """
    name: str
    manufacturer: str
    long_name: str
    spec_key: str
    modes: Dict[str, Dict[str, int]] = field(default_factory=dict)
    file_path: str = ""

    @property
    def display_name(self) -> str:
        """用于 UI 展示的名称"""
        return f"{self.manufacturer} — {self.name}"

    @property
    def mode_names(self) -> List[str]:
        """所有可用模式名"""
        return list(self.modes.keys())

    def get_channel_map(self, mode_name: str) -> Optional[Dict[str, int]]:
        """获取指定模式的通道映射"""
        return self.modes.get(mode_name)

    def get_channel_count(self, mode_name: str) -> int:
        """获取指定模式的通道数"""
        channel_map = self.get_channel_map(mode_name)
        if not channel_map:
            return 0
        return max(channel_map.values()) if channel_map else 0

    def __repr__(self) -> str:
        mode_info = ", ".join(
            f"{m}({len(ch)}ch)" for m, ch in self.modes.items()
        )
        return f"<GDTFProfile '{self.display_name}' [{mode_info}]>"


@dataclass
class Fixture:
    """灯具实例 — 从 MVR 文件解析而来。

    代表舞台上一个具体的灯具，包含其位置、DMX 地址，
    以及与 GDTF Profile 的运行时链接。

    Attributes:
        uuid: MVR 中的唯一 ID
        name: 灯具名称 (e.g. "RotaHead_Mid")
        fixture_id: MVR 中的 FixtureID 编号
        unit_number: 单元编号
        universe: DMX Universe 编号 (从 Address break 提取)
        address: DMX 起始地址 (1-based)
        position: (x, y, z) 世界坐标 (从 Matrix 第4列提取)
        gdtf_spec: MVR 中的 GDTFSpec 名 (用于匹配 GDTF Profile)
        gdtf_mode: MVR 中指定的 GDTF Mode 名
        gdtf_profile: 运行时链接的 GDTFProfile 对象
        is_patched: 是否已成功链接 GDTF Profile
        current_attributes: 当前属性值 (归一化 0.0-1.0)
    """
    uuid: str
    name: str
    fixture_id: str = ""
    unit_number: int = 0
    universe: int = 0
    address: int = 1
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    gdtf_spec: str = ""
    gdtf_mode: str = ""
    gdtf_profile: Optional[GDTFProfile] = field(default=None, repr=False)
    is_patched: bool = False
    current_attributes: Dict[str, float] = field(default_factory=dict)

    def link_profile(self, profile: GDTFProfile) -> bool:
        """链接 GDTF Profile 并初始化属性状态。

        Returns:
            True if linked successfully, False if mode not found.
        """
        channel_map = profile.get_channel_map(self.gdtf_mode)
        if channel_map is None:
            return False

        self.gdtf_profile = profile
        self.is_patched = True
        # 初始化所有属性为 0.0
        self.current_attributes = {attr: 0.0 for attr in channel_map}
        return True

    def unlink_profile(self) -> None:
        """取消 GDTF Profile 链接"""
        self.gdtf_profile = None
        self.is_patched = False
        self.current_attributes.clear()

    def get_dmx_values(self) -> Dict[int, int]:
        """将当前归一化属性转换为 DMX 值 (0-255)。

        Returns:
            {absolute_dmx_channel: dmx_value} 字典。
            如果灯具未 patch，返回空字典。
        """
        if not self.is_patched or not self.gdtf_profile:
            return {}

        channel_map = self.gdtf_profile.get_channel_map(self.gdtf_mode)
        if not channel_map:
            return {}

        dmx_values = {}
        for attr_name, offset in channel_map.items():
            normalized_value = self.current_attributes.get(attr_name, 0.0)
            # 将 0.0-1.0 映射到 0-255
            dmx_byte = max(0, min(255, int(normalized_value * 255)))
            absolute_channel = self.address + offset - 1  # offset 是 1-based
            dmx_values[absolute_channel] = dmx_byte

        return dmx_values

    @property
    def status_text(self) -> str:
        """用于 UI 展示的状态文本"""
        if self.is_patched:
            return "✅ Patched"
        return "⚠️ Unpatched"

    @property
    def channel_count(self) -> int:
        """当前模式的通道数"""
        if self.is_patched and self.gdtf_profile:
            return self.gdtf_profile.get_channel_count(self.gdtf_mode)
        return 0

    def __repr__(self) -> str:
        return (
            f"<Fixture '{self.name}' addr={self.universe}.{self.address} "
            f"{self.status_text}>"
        )


@dataclass
class FixtureGroup:
    """灯具分组 — 用于组织和管理多个灯具。
    
    将多个灯具组织在一起，便于批量操作和管理。
    
    Attributes:
        group_id: 分组唯一标识符
        group_name: 分组显示名称
        fixture_ids: 分组中包含的灯具 UUID 列表
        color: 分组颜色标识 (可选，用于 UI 显示)
    """
    group_id: str
    group_name: str
    fixture_ids: List[str] = field(default_factory=list)
    color: str = "#53a8f9"  # 默认蓝色
    
    def add_fixture(self, fixture_uuid: str) -> None:
        """添加灯具到分组"""
        if fixture_uuid not in self.fixture_ids:
            self.fixture_ids.append(fixture_uuid)
    
    def remove_fixture(self, fixture_uuid: str) -> None:
        """从分组移除灯具"""
        if fixture_uuid in self.fixture_ids:
            self.fixture_ids.remove(fixture_uuid)
    
    @property
    def fixture_count(self) -> int:
        """分组中的灯具数量"""
        return len(self.fixture_ids)
    
    def to_dict(self) -> Dict:
        """转换为可序列化的字典"""
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "fixture_ids": self.fixture_ids,
            "color": self.color,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> FixtureGroup:
        """从字典恢复 FixtureGroup 对象"""
        return FixtureGroup(
            group_id=data.get("group_id", ""),
            group_name=data.get("group_name", ""),
            fixture_ids=data.get("fixture_ids", []),
            color=data.get("color", "#53a8f9"),
        )
    
    def __repr__(self) -> str:
        return f"<FixtureGroup '{self.group_name}' ({self.fixture_count} fixtures)>"
