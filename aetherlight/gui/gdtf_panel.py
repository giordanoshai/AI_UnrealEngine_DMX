"""
AetherLight Pro - GDTF 库面板

支持拖放 .gdtf 文件导入，以树形结构展示已加载的 GDTF Profile，
包括模式信息和通道映射详情。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..gdtf_parser import GDTFLibrary, GDTFParseError, GDTFParser
from ..models import GDTFProfile

logger = logging.getLogger(__name__)


class GDTFDropZone(QWidget):
    """拖放区域 — 接受 .gdtf 文件"""

    files_dropped = pyqtSignal(list)  # List[str]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setMinimumHeight(80)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("📂")
        icon_label.setStyleSheet("font-size: 28px; background: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel("拖放 .gdtf 文件到此处\n或点击下方按钮导入")
        text_label.setStyleSheet(
            "color: #8888aa; font-size: 12px; background: transparent;"
        )
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            # 检查是否包含 .gdtf 文件
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.gdtf'):
                    event.acceptProposedAction()
                    self.setStyleSheet(
                        "#dropZone { border-color: #53a8f9; "
                        "background-color: #1a1a4e; }"
                    )
                    return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent) -> None:
        self.setStyleSheet("")
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.gdtf'):
                files.append(path)

        if files:
            self.files_dropped.emit(files)
            event.acceptProposedAction()


class GDTFPanel(QWidget):
    """GDTF 库面板 — 管理和展示 GDTF Profile 集合。

    功能:
    - 拖放 .gdtf 文件导入
    - 按钮点击导入
    - 树形展示 Profile 详情
    - 发射信号通知库变更

    Signals:
        library_changed: 库内容发生变化时发射
        profile_selected: 用户选择了某个 Profile
    """

    library_changed = pyqtSignal()
    profile_selected = pyqtSignal(object)  # GDTFProfile

    def __init__(
        self,
        library: GDTFLibrary,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.library = library
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # --- 标题 ---
        title = QLabel("GDTF Library")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # --- 拖放区域 ---
        self.drop_zone = GDTFDropZone()
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self.drop_zone)

        # --- 导入按钮 ---
        btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("📁 Import GDTF")
        self.import_btn.clicked.connect(self._on_import_clicked)
        btn_layout.addWidget(self.import_btn)

        self.clear_btn = QPushButton("🗑 Clear All")
        self.clear_btn.setStyleSheet(
            "QPushButton { background-color: #3d1a1a; }"
            "QPushButton:hover { background-color: #5a2a2a; }"
        )
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        # --- Profile 树形视图 ---
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["厂商 / 库 / 灯具", "详情"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree, 1)

        # --- 统计标签 ---
        self.stats_label = QLabel("已加载: 0 个 Profile")
        self.stats_label.setObjectName("statusLabel")
        layout.addWidget(self.stats_label)

    def _on_import_clicked(self) -> None:
        """打开文件对话框导入 GDTF 文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "导入 GDTF 文件",
            "",
            "GDTF Files (*.gdtf);;All Files (*)",
        )
        if files:
            self._load_files(files)

    def _on_files_dropped(self, files: List[str]) -> None:
        """处理拖放的文件"""
        self._load_files(files)

    def _on_clear_clicked(self) -> None:
        """清空 GDTF 库"""
        if self.library.count == 0:
            return

        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确定要清空所有 {self.library.count} 个 GDTF Profile 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.library.clear()
            self._refresh_tree()
            self.library_changed.emit()

    def _load_files(self, file_paths: List[str]) -> None:
        """加载多个 GDTF 文件"""
        success_count = 0
        errors = []

        for path in file_paths:
            try:
                self.library.add_from_file(path)
                success_count += 1
                logger.info("已加载 GDTF: %s", path)
            except GDTFParseError as e:
                errors.append(f"{Path(path).name}: {e}")
                logger.error("GDTF 加载失败: %s", e)

        if errors:
            QMessageBox.warning(
                self,
                "部分文件加载失败",
                "以下文件加载失败:\n\n" + "\n".join(errors),
            )

        if success_count > 0:
            self._refresh_tree()
            self.library_changed.emit()

    def _refresh_tree(self) -> None:
        """刷新 Profile 树形视图 - 按厂商+库名分组"""
        self.tree.clear()

        # 按 manufacturer 和 library_name 分组
        from collections import defaultdict
        
        # 结构: {(manufacturer, library_name): [profiles]}
        grouped = defaultdict(list)
        
        for profile in self.library.get_all_profiles():
            # 从 long_name 解析 library_name
            parts = profile.long_name.strip().split(maxsplit=1)
            library_name = parts[0] if parts else "Other"
            
            # 使用 (厂商, 库名) 元组作为键
            grouped[(profile.manufacturer, library_name)].append(profile)
        
        # 构建树形结构
        for (manufacturer, library_name) in sorted(grouped.keys()):
            profiles = grouped[(manufacturer, library_name)]
            
            # 顶层节点: 厂商 - 库名
            group_item = QTreeWidgetItem([
                f"[{manufacturer} - {library_name}]",
                f"{len(profiles)} 个灯具"
            ])
            
            for profile in sorted(profiles, key=lambda p: p.name):
                # 第二层: 灯具名 + channel 数量
                # 获取第一个 mode 的 channel 数量
                channel_count = 0
                if profile.modes:
                    first_mode = list(profile.modes.values())[0]
                    channel_count = max(first_mode.values()) if first_mode else 0
                
                fixture_item = QTreeWidgetItem([
                    f"  {profile.name}",
                    f"{channel_count} channels"
                ])
                fixture_item.setData(0, Qt.ItemDataRole.UserRole, profile)
                
                # 第三层: Mode 和 Channel 详细信息
                if profile.modes:
                    for mode_name, channels in profile.modes.items():
                        mode_item = QTreeWidgetItem([
                            f"    Mode: {mode_name}",
                            f"{len(channels)} ch"
                        ])
                        
                        # 显示每个 channel
                        for attr_name, offset in sorted(
                            channels.items(), key=lambda x: x[1]
                        ):
                            channel_item = QTreeWidgetItem([
                                f"      CH{offset}: {attr_name}",
                                ""
                            ])
                            mode_item.addChild(channel_item)
                        
                        fixture_item.addChild(mode_item)
                
                group_item.addChild(fixture_item)
            
            group_item.setExpanded(True)
            self.tree.addTopLevelItem(group_item)

        self.stats_label.setText(
            f"已加载: {self.library.count} 个 Profile"
        )

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """树节点点击事件"""
        profile = item.data(0, Qt.ItemDataRole.UserRole)
        if profile and isinstance(profile, GDTFProfile):
            self.profile_selected.emit(profile)
