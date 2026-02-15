"""
AetherLight Pro - MVR 导入器 (Task 2)

解析 MVR (My Virtual Rig) XML 文件，提取灯具列表，
并自动将灯具与 GDTF Library 中的 Profile 进行链接。

MVR 文件结构 (GeneralSceneDescription):
  <GeneralSceneDescription>
    <Scene>
      <Layers>
        <Layer uuid="...">
          <ChildList>
            <Fixture name="..." uuid="...">
              <Matrix>{r11,r12,r13}{r21,r22,r23}{r31,r32,r33}{tx,ty,tz}</Matrix>
              <GDTFSpec>Manufacturer@Name@Version</GDTFSpec>
              <GDTFMode>Mode</GDTFMode>
              <FixtureID>1</FixtureID>
              <Addresses>
                <Address break="0">1</Address>
              </Addresses>
            </Fixture>
          </ChildList>
        </Layer>
      </Layers>
    </Scene>
  </GeneralSceneDescription>
"""
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .gdtf_parser import GDTFLibrary
from .models import Fixture, GDTFProfile

logger = logging.getLogger(__name__)


class MVRParseError(Exception):
    """MVR 文件解析异常"""
    pass


class MVRImporter:
    """MVR 文件导入器。

    解析 MVR 的 GeneralSceneDescription XML 文件，
    提取灯具列表并支持自动链接 GDTF Profile。

    Example:
        >>> fixtures = MVRImporter.parse("path/to/GeneralSceneDescription.xml")
        >>> library = GDTFLibrary()
        >>> library.add_from_file("path/to/fixture.gdtf")
        >>> patched, unpatched = MVRImporter.link_fixtures(fixtures, library)
    """

    @staticmethod
    def parse(file_path: str) -> List[Fixture]:
        """解析 MVR XML 文件，返回灯具列表。

        Args:
            file_path: MVR XML 文件路径
                       (GeneralSceneDescription.xml)

        Returns:
            解析出的 Fixture 列表

        Raises:
            MVRParseError: 文件不存在或 XML 格式错误
        """
        file_path = str(Path(file_path).resolve())

        if not Path(file_path).exists():
            raise MVRParseError(f"MVR 文件不存在: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise MVRParseError(f"MVR XML 解析失败: {e}")

        fixtures: List[Fixture] = []

        # 遍历所有 Layer → ChildList → Fixture
        for layer in root.iter('Layer'):
            layer_uuid = layer.get('uuid', '')
            logger.debug("解析 Layer: %s", layer_uuid)

            child_list = layer.find('ChildList')
            if child_list is None:
                continue

            for fixture_elem in child_list.findall('Fixture'):
                fixture = MVRImporter._parse_fixture(fixture_elem)
                if fixture:
                    fixtures.append(fixture)

        logger.info("MVR 解析完成: 共 %d 个灯具", len(fixtures))
        for f in fixtures:
            logger.info(
                "  - %s (UUID: %s, Addr: %d.%d, Spec: %s)",
                f.name, f.uuid[:8], f.universe, f.address, f.gdtf_spec
            )

        return fixtures

    @staticmethod
    def _parse_fixture(elem: ET.Element) -> Optional[Fixture]:
        """解析单个 <Fixture> 元素。

        Args:
            elem: <Fixture> XML 元素

        Returns:
            Fixture 对象或 None (解析失败时)
        """
        name = elem.get('name', 'Unknown')
        uuid = elem.get('uuid', '')

        if not uuid:
            logger.warning("灯具 '%s' 缺少 UUID，已跳过", name)
            return None

        # GDTFSpec 和 GDTFMode
        gdtf_spec = MVRImporter._get_text(elem, 'GDTFSpec', '')
        gdtf_mode = MVRImporter._get_text(elem, 'GDTFMode', '')
        fixture_id = MVRImporter._get_text(elem, 'FixtureID', '')
        unit_number_str = MVRImporter._get_text(elem, 'UnitNumber', '0')

        try:
            unit_number = int(unit_number_str)
        except ValueError:
            unit_number = 0

        # 解析 Matrix → 位置
        position = MVRImporter._parse_matrix(elem)

        # 解析 DMX 地址
        universe, address = MVRImporter._parse_address(elem)

        fixture = Fixture(
            uuid=uuid,
            name=name,
            fixture_id=fixture_id,
            unit_number=unit_number,
            universe=universe,
            address=address,
            position=position,
            gdtf_spec=gdtf_spec,
            gdtf_mode=gdtf_mode,
        )

        logger.debug("解析灯具: %r", fixture)
        return fixture

    @staticmethod
    def _parse_matrix(elem: ET.Element) -> Tuple[float, float, float]:
        """从 <Matrix> 元素解析 3D 位置。

        MVR Matrix 格式:
          {r11,r12,r13}{r21,r22,r23}{r31,r32,r33}{tx,ty,tz}

        我们提取第 4 组花括号中的 (tx, ty, tz) 作为世界坐标。

        Returns:
            (x, y, z) 坐标元组
        """
        matrix_elem = elem.find('Matrix')
        if matrix_elem is None or not matrix_elem.text:
            return (0.0, 0.0, 0.0)

        matrix_text = matrix_elem.text.strip()

        # 用正则提取所有 {a,b,c} 组
        groups = re.findall(r'\{([^}]+)\}', matrix_text)
        if len(groups) < 4:
            logger.warning(
                "Matrix 格式异常 (组数=%d): %s", len(groups), matrix_text
            )
            return (0.0, 0.0, 0.0)

        # 第 4 组是位移向量 (tx, ty, tz)
        try:
            values = [float(v.strip()) for v in groups[3].split(',')]
            if len(values) >= 3:
                return (values[0], values[1], values[2])
        except ValueError as e:
            logger.warning("Matrix 位移解析失败: %s", e)

        return (0.0, 0.0, 0.0)

    @staticmethod
    def _parse_address(elem: ET.Element) -> Tuple[int, int]:
        """从 <Addresses> 元素解析 DMX Universe 和 Address。

        MVR 格式:
          <Addresses>
            <Address break="0">1</Address>
          </Addresses>

        其中 break 属性为 Universe 编号，文本值为 DMX 地址。

        Returns:
            (universe, address) 元组
        """
        addresses_elem = elem.find('Addresses')
        if addresses_elem is None:
            return (0, 1)

        address_elem = addresses_elem.find('Address')
        if address_elem is None:
            return (0, 1)

        # Universe 从 break 属性获取
        try:
            universe = int(address_elem.get('break', '0'))
        except ValueError:
            universe = 0

        # DMX 地址从文本获取
        try:
            address = int(address_elem.text.strip()) if address_elem.text else 1
        except ValueError:
            address = 1

        return (universe, address)

    @staticmethod
    def _get_text(
        elem: ET.Element, tag: str, default: str = ''
    ) -> str:
        """安全获取子元素文本"""
        child = elem.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    # ------------------------------------------------------------------
    # GDTF 链接逻辑 (Task 2 核心)
    # ------------------------------------------------------------------

    @staticmethod
    def link_fixtures(
        fixtures: List[Fixture],
        library: GDTFLibrary,
    ) -> Tuple[List[Fixture], List[Fixture]]:
        """自动链接灯具与 GDTF Library。

        对每个灯具，检查其 gdtf_spec 是否匹配库中的某个 Profile。
        匹配成功则链接 Profile 并标记为 patched，否则标记为 unpatched。

        Args:
            fixtures: 解析出的灯具列表
            library: GDTF 配置文件库

        Returns:
            (patched_list, unpatched_list) — 已链接和未链接灯具的列表
        """
        patched: List[Fixture] = []
        unpatched: List[Fixture] = []

        # 统计需要的 GDTF spec
        needed_specs: Set[str] = set()

        for fixture in fixtures:
            # 尝试按 spec_key 精确匹配
            profile = library.get_profile(fixture.gdtf_spec)

            if profile is not None:
                success = fixture.link_profile(profile)
                if success:
                    patched.append(fixture)
                    logger.info(
                        "✅ 已链接: %s → %s (Mode: %s)",
                        fixture.name, profile.display_name, fixture.gdtf_mode
                    )
                else:
                    # Profile 存在但指定的 Mode 不存在
                    unpatched.append(fixture)
                    logger.warning(
                        "⚠️ 模式不匹配: %s 需要 Mode '%s', "
                        "但 Profile 只有: %s",
                        fixture.name, fixture.gdtf_mode,
                        profile.mode_names
                    )
            else:
                unpatched.append(fixture)
                needed_specs.add(fixture.gdtf_spec)
                logger.warning(
                    "⚠️ 未找到 GDTF Profile: %s (需要: %s)",
                    fixture.name, fixture.gdtf_spec
                )

        logger.info(
            "链接结果: %d 已链接, %d 未链接",
            len(patched), len(unpatched)
        )

        if needed_specs:
            logger.warning(
                "缺失的 GDTF Profiles: %s",
                ", ".join(sorted(needed_specs))
            )

        return patched, unpatched

    @staticmethod
    def manual_link(
        fixture: Fixture,
        profile: GDTFProfile,
        mode_name: Optional[str] = None,
    ) -> bool:
        """手动链接单个灯具到指定 GDTF Profile。

        用于 UI 中用户手动选择 GDTF Profile 时调用。

        Args:
            fixture: 要链接的灯具
            profile: 用户选择的 GDTF Profile
            mode_name: 可选，指定模式名。不指定则使用灯具的 gdtf_mode

        Returns:
            True if linked successfully
        """
        if mode_name:
            fixture.gdtf_mode = mode_name

        # 如果灯具没有指定 mode，使用 Profile 的第一个 mode
        if not fixture.gdtf_mode and profile.mode_names:
            fixture.gdtf_mode = profile.mode_names[0]

        success = fixture.link_profile(profile)
        if success:
            logger.info(
                "手动链接成功: %s → %s (Mode: %s)",
                fixture.name, profile.display_name, fixture.gdtf_mode
            )
        else:
            logger.error(
                "手动链接失败: %s → %s (Mode: %s 不存在)",
                fixture.name, profile.display_name, fixture.gdtf_mode
            )

        return success
