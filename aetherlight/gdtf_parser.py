"""
AetherLight Pro - GDTF 解析器 (Task 1)


解析 .gdtf 文件（ZIP 压缩包含 description.xml），
提取 DMX 模式与通道映射。

GDTF (General Device Type Format) 规范:
  - .gdtf 文件本质是一个 ZIP 归档
  - 包含 description.xml 描述灯具属性
  - DMXMode → DMXChannel → LogicalChannel 层级结构
  - 每个 DMXChannel 有 Offset 属性（1-based 通道偏移）
  - LogicalChannel 的 Attribute 描述功能名 (Pan, Tilt, Dimmer 等)
"""
from __future__ import annotations

import logging
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from .models import GDTFProfile
from .database.local_cache import get_local_cache


logger = logging.getLogger(__name__)


class GDTFParseError(Exception):
    """GDTF 文件解析异常"""
    pass


class GDTFParser:
    """GDTF 文件解析器。

    解析 .gdtf 文件，提取 FixtureType 信息和 DMX 通道映射。

    Example:
        >>> profile = GDTFParser.parse("path/to/fixture.gdtf")
        >>> print(profile.modes)
        {'Mode': {'Pan': 1, 'Tilt': 2, 'Dimmer': 5, ...}}
    """

    @staticmethod
    def parse(file_path: str) -> GDTFProfile:
        """解析 .gdtf 文件，返回 GDTFProfile。

        Args:
            file_path: .gdtf 文件路径

        Returns:
            GDTFProfile 对象，包含灯具信息和通道映射

        Raises:
            GDTFParseError: 文件无法打开、缺少 description.xml 或 XML 格式错误
        """
        file_path = str(Path(file_path).resolve())

        if not os.path.exists(file_path):
            raise GDTFParseError(f"文件不存在: {file_path}")

        # --- Step 1: 打开 ZIP 归档 ---
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                if 'description.xml' not in zf.namelist():
                    raise GDTFParseError(
                        f"GDTF 文件缺少 description.xml: {file_path}"
                    )
                xml_data = zf.read('description.xml')
        except zipfile.BadZipFile:
            raise GDTFParseError(f"无效的 ZIP 文件: {file_path}")

        # --- Step 2: 解析 XML ---
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            raise GDTFParseError(f"XML 解析失败: {e}")

        # --- Step 3: 提取 FixtureType 信息 ---
        fixture_type = root.find('FixtureType')
        if fixture_type is None:
            raise GDTFParseError("description.xml 中未找到 FixtureType 元素")

        name = fixture_type.get('Name', 'Unknown')
        manufacturer = fixture_type.get('Manufacturer', 'Unknown')
        long_name = fixture_type.get('LongName', name)

        # spec_key 从文件名提取（不含扩展名），用于与 MVR 的 GDTFSpec 匹配
        spec_key = Path(file_path).stem

        logger.info(
            "解析 GDTF: %s (制造商: %s, Spec: %s)",
            name, manufacturer, spec_key
        )

        # --- Step 4: 解析 DMX Modes ---
        modes = GDTFParser._parse_dmx_modes(fixture_type)

        if not modes:
            logger.warning("GDTF 文件中未找到任何 DMX Mode: %s", file_path)

        profile = GDTFProfile(
            name=name,
            manufacturer=manufacturer,
            long_name=long_name,
            spec_key=spec_key,
            modes=modes,
            file_path=file_path,
        )

        logger.info("GDTF 解析完成: %r", profile)
        return profile

    @staticmethod
    def _parse_dmx_modes(fixture_type: ET.Element) -> Dict[str, Dict[str, int]]:
        """解析所有 DMXMode，提取通道映射。

        XML 结构:
          <DMXModes>
            <DMXMode Name="Mode" ...>
              <DMXChannels>
                <DMXChannel Offset="1" ...>
                  <LogicalChannel Attribute="Pan" ...> ... </LogicalChannel>
                </DMXChannel>
                ...
              </DMXChannels>
            </DMXMode>
          </DMXModes>

        Returns:
            {mode_name: {attribute_name: channel_offset}} 字典
        """
        modes: Dict[str, Dict[str, int]] = {}

        dmx_modes_elem = fixture_type.find('DMXModes')
        if dmx_modes_elem is None:
            return modes

        for dmx_mode in dmx_modes_elem.findall('DMXMode'):
            mode_name = dmx_mode.get('Name', 'Default')
            channel_map: Dict[str, int] = {}

            dmx_channels = dmx_mode.find('DMXChannels')
            if dmx_channels is None:
                continue

            for dmx_channel in dmx_channels.findall('DMXChannel'):
                offset_str = dmx_channel.get('Offset', '')
                if not offset_str:
                    continue

                # Offset 可以是逗号分隔的多值 (如 "1,2" 表示 16-bit)
                # 取第一个值作为主偏移
                try:
                    offset = int(offset_str.split(',')[0])
                except ValueError:
                    logger.warning(
                        "无效的 Channel Offset '%s' in mode '%s'",
                        offset_str, mode_name
                    )
                    continue

                # 从 LogicalChannel 提取属性名
                logical_channel = dmx_channel.find('LogicalChannel')
                if logical_channel is not None:
                    attribute = logical_channel.get('Attribute', '')
                    if attribute:
                        channel_map[attribute] = offset
                        logger.debug(
                            "  Mode '%s': %s -> Offset %d",
                            mode_name, attribute, offset
                        )

            if channel_map:
                modes[mode_name] = channel_map
                logger.info(
                    "DMX Mode '%s': %d 个通道 — %s",
                    mode_name, len(channel_map),
                    ", ".join(f"{k}={v}" for k, v in sorted(
                        channel_map.items(), key=lambda x: x[1]
                    ))
                )

        return modes


class GDTFLibrary:
    """GDTF 配置文件库 — 管理所有已加载的 GDTFProfile。

    以 spec_key 为键存储 Profile，支持：
    - 从文件加载
    - 从数据库加载
    - 按 spec_key 精确查找（MVR 自动链接用）
    - 按名称模糊查找（手动选择用）

    Example:
        >>> library = GDTFLibrary()
        >>> library.add_from_file("path/to/fixture.gdtf")
        >>> profile = library.get_profile("EpicGames@UE5_6_Generated_RotaHead@12_02_26")
        
        # 使用数据库
        >>> library = GDTFLibrary(use_database=True)
        >>> library.load_from_database()  # 从数据库加载所有 Profile
    """

    def __init__(self) -> None:
        """初始化 GDTF Library。
        
        自动连接到本地缓存 (LocalCache)。
        """
        self._profiles: Dict[str, GDTFProfile] = {}
        logger.info("GDTFLibrary 已初始化 (LocalCache 模式)")

    @property
    def profiles(self) -> Dict[str, GDTFProfile]:
        """所有已加载的 Profile 字典 (spec_key -> GDTFProfile)"""
        return dict(self._profiles)

    @property
    def count(self) -> int:
        """已加载的 Profile 数量"""
        return len(self._profiles)

    def add_from_file(self, file_path: str, save_to_cache: bool = True) -> GDTFProfile:
        """从文件加载 GDTF Profile 并添加到库。

        Args:
            file_path: .gdtf 文件路径
            save_to_cache: 是否自动保存到本地缓存
        
        Returns:
            解析得到的 GDTFProfile 对象
        """
        profile = GDTFParser.parse(file_path)
        self._profiles[profile.spec_key] = profile
        
        # 保存到缓存
        if save_to_cache:
            cache = get_local_cache()
            # 构造符合 fixture_profiles 表的数据结构
            data = {
                "manufacturer": profile.manufacturer,
                "name": profile.name,
                "channels": profile.modes,  # Map modes to channels field
                "file_path": str(profile.file_path),
                "fixture_id": None # Allow user to set later?
            }
            # 使用 name 和 manufacturer 作为唯一键检查是否存在?
            # cache.upsert 可能会产生重复如果 ID 不存在.
            # 这里简单做 create, 实际应该检查重复.
            # 暂时假设 synchronize manager 会处理重复或者这里只是添加.
            # Check for existing profile with same manufacturer and name
            existing_items = cache.list(
                "fixture_profiles",
                lambda x: x.get("name") == profile.name and x.get("manufacturer") == profile.manufacturer
            )
            
            if not existing_items: 
                cache.create("fixture_profiles", data)
            else:
                logger.info("Local cache already contains profile: %s - %s", profile.manufacturer, profile.name)
        
        logger.info("GDTF Profile 已添加到库: %s", profile.spec_key)
        return profile

    def add_profile(self, profile: GDTFProfile) -> None:
        """直接添加 GDTFProfile 到库"""
        self._profiles[profile.spec_key] = profile

    def remove_profile(self, spec_key: str, remove_from_db: bool = True) -> bool:
        """从库中移除 Profile"""
        removed = False
        
        if spec_key in self._profiles:
            del self._profiles[spec_key]
            removed = True
        
        # Cache deletion logic
        # cache = get_local_cache()
        # item = cache.get_by_field("fixture_profiles", "name", ...)
        # if item: cache.delete("fixture_profiles", item['id'])
        logger.warning("Cache暂不支持通过 SpecKey 删除 Profile")
        pass
        
        return removed

    def get_profile(self, spec_key: str) -> Optional[GDTFProfile]:
        """按 spec_key 精确查找 Profile。"""
        # 先从内存查找
        if spec_key in self._profiles:
            return self._profiles[spec_key]
        
        # 尝试从缓存加载
        cache = get_local_cache()
        # 这里逻辑比较模糊，假设 spec_key == name
        # 实际应该遍历 cache 或改进 spec_key 生成
        # 暂时留空，等待 load_from_cache 填充
        pass
        
        return None

    def find_by_name(self, name: str) -> List[GDTFProfile]:
        """按名称模糊查找"""
        name_lower = name.lower()
        return [
            p for p in self._profiles.values()
            if name_lower in p.name.lower()
            or name_lower in p.long_name.lower()
            or name_lower in p.manufacturer.lower()
        ]

    def get_all_profiles(self) -> List[GDTFProfile]:
        """获取所有已加载的 Profile 列表"""
        return list(self._profiles.values())
    
    def load_from_cache(self) -> int:
        """从本地缓存加载所有 Profile 到内存。"""
        cache = get_local_cache()
        cached_profiles = cache.list("fixture_profiles")
        
        count = 0
        for row in cached_profiles:
             # 'channels' field stores the modes mapping
             modes = row.get("channels", {})
             
             name = row.get("name", "")
             manufacturer = row.get("manufacturer", "")
             
             profile = GDTFProfile(
                 name=name,
                 manufacturer=manufacturer,
                 long_name=row.get("long_name", name), # Fallback to name if long_name missing
                 spec_key=f"{manufacturer}_{name}",
                 modes=modes,
                 file_path=row.get("file_path", "")
             )
             key = profile.spec_key 
             self._profiles[key] = profile
             count += 1
        
        logger.info("从本地缓存加载了 %d 个 GDTF Profile", count)
        return count

    def clear(self) -> None:
        """清空内存中的库 (不影响数据库)"""
        self._profiles.clear()

    def __repr__(self) -> str:
        return f"<GDTFLibrary profiles={self.count}>"
