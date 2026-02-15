"""
AetherLight Pro - 分组管理面板

在左侧面板显示所有灯具分组，支持树形结构展示分组和分组内的灯具。
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..models import Fixture, FixtureGroup

logger = logging.getLogger(__name__)


class GroupPanel(QWidget):
    """分组管理面板 — 显示和管理灯具分组。
    
    功能:
    - 树形显示所有分组
    - 每个分组显示名称和灯具数量
    - 展开分组显示灯具列表
    - 支持选择分组
    
    Signals:
        group_selected: 选择分组时发出 (group_id)
        groups_changed: 分组列表变化时发出
    """
    
    group_selected = pyqtSignal(str)  # group_id
    groups_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.groups: List[FixtureGroup] = []
        self.fixtures: List[Fixture] = []  # 用于查找灯具名称
        self._fixture_map: Dict[str, Fixture] = {}  # uuid -> Fixture
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # --- 标题栏 ---
        header_layout = QHBoxLayout()
        
        title = QLabel("分组管理")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # --- 分组树 ---
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        # 启用右键菜单
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.tree, 1)
        
        # --- 统计信息 ---
        self.stats_label = QLabel("无分组")
        self.stats_label.setObjectName("statusLabel")
        layout.addWidget(self.stats_label)
    
    def set_fixtures(self, fixtures: List[Fixture]) -> None:
        """设置灯具列表"""
        self.fixtures = fixtures
        self._fixture_map = {f.uuid: f for f in fixtures}
        self._refresh_tree()
    
    def set_groups(self, groups: List[FixtureGroup]) -> None:
        """设置分组列表"""
        self.groups = groups
        self._refresh_tree()
    
    def add_group(self, group: FixtureGroup) -> None:
        """添加新分组"""
        self.groups.append(group)
        self._refresh_tree()
        self.groups_changed.emit()
        logger.info(f"添加分组: {group.group_name} ({group.fixture_count} fixtures)")
    
    def remove_group(self, group_id: str) -> None:
        """移除分组"""
        self.groups = [g for g in self.groups if g.group_id != group_id]
        self._refresh_tree()
        self.groups_changed.emit()
    
    def _refresh_tree(self) -> None:
        """刷新分组树"""
        self.tree.clear()
        
        for group in self.groups:
            # 创建分组节点
            group_item = QTreeWidgetItem(self.tree)
            group_text = f"📁 {group.group_name} ({group.fixture_count})"
            group_item.setText(0, group_text)
            group_item.setData(0, Qt.ItemDataRole.UserRole, group.group_id)
            
            # 设置分组节点样式
            font = QFont()
            font.setBold(True)
            group_item.setFont(0, font)
            group_item.setForeground(0, QColor("#53a8f9"))
            
            # 添加灯具子节点
            for fixture_id in group.fixture_ids:
                fixture = self._fixture_map.get(fixture_id)
                if fixture:
                    fixture_item = QTreeWidgetItem(group_item)
                    fixture_text = f"💡 {fixture.name}"
                    fixture_item.setText(0, fixture_text)
                    fixture_item.setData(0, Qt.ItemDataRole.UserRole, fixture.uuid)
                    fixture_item.setForeground(0, QColor("#8888aa"))
        
        # 更新统计
        total_groups = len(self.groups)
        total_fixtures = sum(g.fixture_count for g in self.groups)
        self.stats_label.setText(
            f"{total_groups} 个分组 | {total_fixtures} 个灯具"
        )
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """点击树节点时"""
        group_id = item.data(0, Qt.ItemDataRole.UserRole)
        if group_id and not item.parent():  # 是分组节点（非灯具节点）
            self.group_selected.emit(group_id)
    
    def _show_context_menu(self, position) -> None:
        """显示右键菜单"""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        # 创建右键菜单
        menu = QMenu(self)
        
        # 判断是分组节点还是灯具节点
        if item.parent():
            # 灯具节点 - 提供从分组中移除的选项
            fixture_id = item.data(0, Qt.ItemDataRole.UserRole)
            group_item = item.parent()
            group_id = group_item.data(0, Qt.ItemDataRole.UserRole)
            
            if fixture_id and group_id:
                remove_from_group_action = menu.addAction("🔻 从分组中移除")
                
                # 显示菜单并获取选择的动作
                action = menu.exec(self.tree.viewport().mapToGlobal(position))
                
                if action == remove_from_group_action:
                    self._remove_fixture_from_group(group_id, fixture_id)
        else:
            # 分组节点 - 提供删除分组的选项
            group_id = item.data(0, Qt.ItemDataRole.UserRole)
            if not group_id:
                return
            
            delete_action = menu.addAction("🗑️ 删除分组")
            
            # 显示菜单并获取选择的动作
            action = menu.exec(self.tree.viewport().mapToGlobal(position))
            
            if action == delete_action:
                self._delete_group(group_id)
    
    def _delete_group(self, group_id: str) -> None:
        """删除分组"""
        # 查找分组
        group = self.get_group_by_id(group_id)
        if not group:
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除分组 \"{group.group_name}\" 吗？\n"
            f"这将移除分组，但不会删除灯具本身。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从列表中移除
            self.remove_group(group_id)
            logger.info(f"已删除分组: {group.group_name}")
    
    def _remove_fixture_from_group(self, group_id: str, fixture_id: str) -> None:
        """从分组中移除灯具"""
        # 查找分组
        group = self.get_group_by_id(group_id)
        if not group:
            return
        
        # 查找灯具
        fixture = self._fixture_map.get(fixture_id)
        if not fixture:
            return
        
        # 确认移除
        reply = QMessageBox.question(
            self,
            "确认移除",
            f"确定要从分组 \"{group.group_name}\" 中移除灯具 \"{fixture.name}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从分组中移除灯具
            group.remove_fixture(fixture_id)
            # 刷新树显示
            self._refresh_tree()
            # 发出信号通知变化
            self.groups_changed.emit()
            logger.info(f"已从分组 {group.group_name} 中移除灯具: {fixture.name}")
    
    def get_group_by_id(self, group_id: str) -> Optional[FixtureGroup]:
        """根据ID查找分组"""
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None
