"""
AetherLight Pro - 分组创建对话框

提供创建新灯具分组的UI对话框。
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ..models import Fixture, FixtureGroup


class CreateGroupDialog(QDialog):
    """创建分组对话框。
    
    允许用户为选中的灯具创建新的分组。
    
    Args:
        fixtures: 要添加到分组的灯具列表
        existing_groups: 现有分组列表（用于验证名称唯一性）
        parent: 父窗口
    """
    
    def __init__(
        self,
        fixtures: List[Fixture],
        existing_groups: List[FixtureGroup],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.fixtures = fixtures
        self.existing_groups = existing_groups
        self.created_group: Optional[FixtureGroup] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        self.setWindowTitle("创建灯具分组")
        self.setMinimumSize(400, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # --- 标题 ---
        title = QLabel("创建新分组")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #53a8f9;")
        layout.addWidget(title)
        
        # --- 分组名称输入 ---
        name_label = QLabel("分组名称:")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入分组名称...")
        layout.addWidget(self.name_input)
        
        # --- 灯具数量提示 ---
        fixture_count = len(self.fixtures)
        count_label = QLabel(f"将添加 <b>{fixture_count}</b> 个灯具到此分组:")
        count_label.setTextFormat(Qt.TextFormat.RichText)
        count_label.setStyleSheet("color: #8888aa; margin-top: 10px;")
        layout.addWidget(count_label)
        
        # --- 灯具列表预览 ---
        self.fixture_list = QListWidget()
        self.fixture_list.setMaximumHeight(150)
        for fixture in self.fixtures:
            item_text = f"{fixture.name} ({fixture.universe}.{fixture.address})"
            self.fixture_list.addItem(item_text)
        layout.addWidget(self.fixture_list)
        
        # --- 按钮 ---
        layout.addStretch()
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_accept(self) -> None:
        """确认创建分组"""
        group_name = self.name_input.text().strip()
        
        # 验证分组名称
        if not group_name:
            QMessageBox.warning(
                self,
                "无效名称",
                "分组名称不能为空"
            )
            return
        
        # 检查名称是否重复
        if any(g.group_name == group_name for g in self.existing_groups):
            QMessageBox.warning(
                self,
                "名称重复",
                f"分组名称\"{group_name}\"已存在，请使用其他名称"
            )
            return
        
        # 创建分组
        self.created_group = FixtureGroup(
            group_id=str(uuid.uuid4()),
            group_name=group_name,
            fixture_ids=[f.uuid for f in self.fixtures],
        )
        
        self.accept()
    
    def get_group(self) -> Optional[FixtureGroup]:
        """获取创建的分组"""
        return self.created_group
