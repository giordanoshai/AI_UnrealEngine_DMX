"""
AetherLight Pro - 分组管理页面

集中管理灯具分组功能。
"""
from __future__ import annotations

import logging
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..gdtf_parser import GDTFLibrary
from ..models import Fixture, FixtureGroup
from .fixture_panel import FixturePanel
from .group_panel import GroupPanel
from .group_dialog import CreateGroupDialog

logger = logging.getLogger(__name__)


class GroupManagementPage(QWidget):
    """分组管理页面 - 管理灯具分组。
    
    布局:
    ┌─────────────────────────────────────┐
    │  分组管理                            │
    ├──────────────┬──────────────────────┤
    │  Group Panel │   Fixture Panel      │
    │  (分组列表)  │   (灯具列表+选择)    │
    └──────────────┴──────────────────────┘
    
    Signals:
        groups_changed: 分组列表变化
    """
    
    groups_changed = pyqtSignal()
    
    def __init__(
        self,
        library: GDTFLibrary,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.library = library
        self.groups: List[FixtureGroup] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # --- 标题 ---
        header_layout = QHBoxLayout()
        
        title = QLabel("分组管理")
        title.setObjectName("sectionTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #53a8f9;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # --- 主内容区域 - 两栏布局 ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧: 分组面板
        self.group_panel = GroupPanel()
        self.group_panel.setMinimumWidth(250)
        self.group_panel.setMaximumWidth(400)
        splitter.addWidget(self.group_panel)
        
        # 右侧: 灯具列表面板（带搜索和选择功能）
        self.fixture_panel = FixturePanel(self.library)
        splitter.addWidget(self.fixture_panel)
        
        # 设置初始分割比例 (3:7)
        splitter.setSizes([350, 850])
        
        layout.addWidget(splitter, 1)
        
        # --- 连接信号 ---
        self._connect_signals()
    
    def _connect_signals(self) -> None:
        """连接信号"""
        self.fixture_panel.fixtures_changed.connect(self._on_fixtures_changed)
        self.fixture_panel.create_group_requested.connect(self._on_create_group_requested)
        # 当分组面板的分组变化时（如删除），同步到本页面并发出信号
        self.group_panel.groups_changed.connect(self._on_group_panel_changed)
    
    def set_fixtures(self, fixtures: List[Fixture]) -> None:
        """设置灯具列表"""
        self.fixture_panel.fixtures = fixtures
        self.fixture_panel._refresh_table()
        self.group_panel.set_fixtures(fixtures)
    
    def set_groups(self, groups: List[FixtureGroup]) -> None:
        """设置分组列表"""
        self.groups = groups
        self.group_panel.set_groups(groups)
    
    def _on_fixtures_changed(self) -> None:
        """灯具列表变化时同步到分组面板"""
        self.group_panel.set_fixtures(self.fixture_panel.fixtures)
    
    def _on_group_panel_changed(self) -> None:
        """分组面板变化时（如删除分组），同步到页面的groups列表"""
        # 同步分组面板的groups到页面的groups
        self.groups = self.group_panel.groups
        # 发出信号通知主窗口
        self.groups_changed.emit()
    
    def _on_create_group_requested(self, fixtures: List[Fixture]) -> None:
        """处理创建分组请求"""
        dialog = CreateGroupDialog(
            fixtures,
            self.groups,
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_group = dialog.get_group()
            if new_group:
                # 添加到分组列表
                self.groups.append(new_group)
                # 同步到分组面板（使用set_groups而不是add_group，避免重复添加）
                self.group_panel.set_groups(self.groups)
                # 发出信号
                self.groups_changed.emit()
                logger.info(f"创建分组: {new_group.group_name} ({new_group.fixture_count} 个灯具)")
