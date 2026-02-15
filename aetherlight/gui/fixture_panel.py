"""
AetherLight Pro - 灯具列表面板

以表格形式展示 MVR 导入的灯具列表，
显示 Patch 状态，支持右键手动链接 GDTF Profile。
"""
from __future__ import annotations

import logging
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..gdtf_parser import GDTFLibrary
from ..models import Fixture, GDTFProfile
from ..mvr_importer import MVRImporter, MVRParseError

logger = logging.getLogger(__name__)


# ======================================================================
# 手动 GDTF 选择对话框
# ======================================================================

class GDTFSelectDialog(QDialog):
    """手动选择 GDTF Profile 对话框。

    当灯具无法自动匹配 GDTF Profile 时弹出，
    让用户从已加载的库中手动选择 Profile 和 Mode。
    """

    def __init__(
        self,
        fixture: Fixture,
        library: GDTFLibrary,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.fixture = fixture
        self.library = library
        self.selected_profile: Optional[GDTFProfile] = None
        self.selected_mode: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Select GDTF Profile")
        self.setMinimumSize(450, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- 情报提示 ---
        info_label = QLabel(
            f'⚠️ <b>Missing Driver</b> for fixture '
            f'"<span style="color: #53a8f9;">{self.fixture.name}</span>"'
            f'<br><br>'
            f'<span style="color: #8888aa;">需要的 GDTF Spec: '
            f'<code>{self.fixture.gdtf_spec}</code></span>'
            f'<br>'
            f'<span style="color: #8888aa;">请从库中选择一个替代 Profile:</span>'
        )
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        # --- Profile 选择 ---
        profile_label = QLabel("GDTF Profile:")
        layout.addWidget(profile_label)

        self.profile_combo = QComboBox()
        profiles = self.library.get_all_profiles()
        if not profiles:
            self.profile_combo.addItem("(库中没有可用的 Profile)")
        else:
            for p in profiles:
                self.profile_combo.addItem(
                    f"{p.display_name}  [{p.spec_key}]", p
                )
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        layout.addWidget(self.profile_combo)

        # --- Mode 选择 ---
        mode_label = QLabel("DMX Mode:")
        layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        layout.addWidget(self.mode_combo)

        # --- 通道预览 ---
        self.channel_preview = QLabel("")
        self.channel_preview.setStyleSheet(
            "color: #8888aa; font-size: 11px; background: transparent;"
        )
        self.channel_preview.setWordWrap(True)
        layout.addWidget(self.channel_preview)

        # 连接信号
        self.mode_combo.currentIndexChanged.connect(self._update_preview)
        
        # 初始化 Mode 列表 (必须在 channel_preview 创建后调用)
        self._on_profile_changed(0)

        # --- 按钮 ---
        layout.addStretch()
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_profile_changed(self, index: int) -> None:
        """Profile 下拉变化时更新 Mode 列表"""
        self.mode_combo.clear()
        profile = self.profile_combo.currentData()
        if profile and isinstance(profile, GDTFProfile):
            for mode_name in profile.mode_names:
                ch_count = len(profile.modes.get(mode_name, {}))
                self.mode_combo.addItem(
                    f"{mode_name} ({ch_count} ch)", mode_name
                )
        self._update_preview()

    def _update_preview(self) -> None:
        """更新通道预览"""
        profile = self.profile_combo.currentData()
        mode = self.mode_combo.currentData()

        if not profile or not mode:
            self.channel_preview.setText("")
            return

        channel_map = profile.get_channel_map(mode)
        if channel_map:
            channels = ", ".join(
                f"CH{v}:{k}"
                for k, v in sorted(channel_map.items(), key=lambda x: x[1])
            )
            self.channel_preview.setText(f"通道: {channels}")
        else:
            self.channel_preview.setText("无通道数据")

    def _on_accept(self) -> None:
        """确认选择"""
        self.selected_profile = self.profile_combo.currentData()
        self.selected_mode = self.mode_combo.currentData()
        if self.selected_profile:
            self.accept()

    def get_selection(self):
        """返回选择结果: (GDTFProfile, mode_name) 或 (None, None)"""
        return self.selected_profile, self.selected_mode


# ======================================================================
# 灯具列表面板
# ======================================================================

class FixturePanel(QWidget):
    """灯具列表面板 — 展示 MVR 导入的灯具和 Patch 状态。

    功能:
    - 表格显示灯具信息 (Name, UUID, Address, Position, Status)
    - 右键菜单: 手动链接 GDTF Profile
    - 支持 MVR 文件导入

    Signals:
        fixtures_changed: 灯具列表或状态发生变化
        create_group_requested: 请求创建分组 (选中的fixtures)
    """

    fixtures_changed = pyqtSignal()
    create_group_requested = pyqtSignal(list)  # List[Fixture]

    def __init__(
        self,
        library: GDTFLibrary,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.library = library
        self.fixtures: List[Fixture] = []
        self.filtered_fixtures: List[Fixture] = []  # 搜索过滤后的灯具
        self.search_text = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # --- 标题 ---
        header_layout = QHBoxLayout()

        title = QLabel("灯具管理")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)

        header_layout.addStretch()

        layout.addLayout(header_layout)
        
        # --- 搜索和操作栏 ---
        control_layout = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索灯具名称...")
        self.search_input.textChanged.connect(self._on_search_changed)
        control_layout.addWidget(self.search_input, 2)
        
        # 全选复选框
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.stateChanged.connect(self._on_select_all_changed)
        control_layout.addWidget(self.select_all_checkbox)
        
        # 反选按钮
        self.invert_btn = QPushButton("🔁 反选")
        self.invert_btn.clicked.connect(self._on_invert_selection)
        control_layout.addWidget(self.invert_btn)
        
        # 创建分组按钮
        self.create_group_btn = QPushButton("📋 创建分组")
        self.create_group_btn.setObjectName("accentButton")
        self.create_group_btn.clicked.connect(self._on_create_group)
        control_layout.addWidget(self.create_group_btn)
        
        layout.addLayout(control_layout)

        # --- 灯具表格 ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Fixture ID", "Universe", "Address",
            "Position (X, Y, Z)", "Fixture Type", "Status",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        # 支持多选
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self.table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table, 1)

        # --- 统计栏 ---
        self.stats_label = QLabel("无灯具")
        self.stats_label.setObjectName("statusLabel")
        layout.addWidget(self.stats_label)

    def _on_import_mvr(self) -> None:
        """打开文件对话框导入 MVR 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入 MVR 文件",
            "",
            "MVR XML (*.xml);;All Files (*)",
        )
        if not file_path:
            return

        try:
            self.fixtures = MVRImporter.parse(file_path)
        except MVRParseError as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "MVR 导入失败", str(e))
            return

        # 自动链接
        self._relink_all()

    def _relink_all(self) -> None:
        """重新链接所有灯具到 GDTF 库"""
        if not self.fixtures:
            return

        # 先取消所有链接
        for f in self.fixtures:
            f.unlink_profile()

        patched, unpatched = MVRImporter.link_fixtures(
            self.fixtures, self.library
        )

        self._refresh_table()
        self.fixtures_changed.emit()

        logger.info(
            "链接完成: %d patched / %d unpatched",
            len(patched), len(unpatched)
        )

    def _refresh_table(self) -> None:
        """刷新灯具表格"""
        # 应用搜索过滤
        self._apply_search_filter()
        
        # 使用过滤后的灯具列表
        display_fixtures = self.filtered_fixtures
        self.table.setRowCount(len(display_fixtures))

        patched_count = 0
        for row, fixture in enumerate(display_fixtures):
            # Name
            name_item = QTableWidgetItem(fixture.name)
            name_item.setData(Qt.ItemDataRole.UserRole, fixture)
            self.table.setItem(row, 0, name_item)

            # Fixture ID
            self.table.setItem(
                row, 1, QTableWidgetItem(fixture.fixture_id)
            )

            # Universe
            self.table.setItem(
                row, 2, QTableWidgetItem(str(fixture.universe))
            )

            # Address
            self.table.setItem(
                row, 3, QTableWidgetItem(str(fixture.address))
            )

            # Position
            pos = fixture.position
            pos_text = f"({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})"
            self.table.setItem(row, 4, QTableWidgetItem(pos_text))

            # Fixture Type - 显示链接的 Profile 名称,如果未链接显示灰色的 spec
            if fixture.is_patched and fixture.gdtf_profile:
                type_text = fixture.gdtf_profile.name
                type_item = QTableWidgetItem(type_text)
                type_item.setForeground(QColor("#00b894"))
            else:
                type_item = QTableWidgetItem(fixture.gdtf_spec)
                type_item.setForeground(QColor("#8888aa"))
            self.table.setItem(row, 5, type_item)

            # Status
            if fixture.is_patched:
                status_item = QTableWidgetItem("✅ Patched")
                status_item.setForeground(QColor("#00b894"))
                patched_count += 1
            else:
                status_item = QTableWidgetItem("⚠️ Unpatched")
                status_item.setForeground(QColor("#e94560"))
            self.table.setItem(row, 6, status_item)

        # 更新统计
        total = len(self.fixtures)
        filtered_total = len(display_fixtures)
        unpatched = total - patched_count
        
        if self.search_text:
            self.stats_label.setText(
                f"共 {total} 个灯具 (显示 {filtered_total}) | "
                f"✅ {patched_count} Patched | "
                f"⚠️ {unpatched} Unpatched"
            )
        else:
            self.stats_label.setText(
                f"共 {total} 个灯具 | "
                f"✅ {patched_count} Patched | "
                f"⚠️ {unpatched} Unpatched"
            )

    def _show_context_menu(self, pos) -> None:
        """右键菜单"""
        row = self.table.rowAt(pos.y())
        if row < 0 or row >= len(self.fixtures):
            return

        fixture = self.fixtures[row]
        menu = QMenu(self)

        if not fixture.is_patched:
            link_action = QAction("🔗 Select GDTF Profile...", self)
            link_action.triggered.connect(
                lambda: self._manual_link(fixture)
            )
            menu.addAction(link_action)
        else:
            unlink_action = QAction("❌ Unlink Profile", self)
            unlink_action.triggered.connect(
                lambda: self._unlink(fixture)
            )
            menu.addAction(unlink_action)

            relink_action = QAction("🔄 Change Profile...", self)
            relink_action.triggered.connect(
                lambda: self._manual_link(fixture)
            )
            menu.addAction(relink_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _manual_link(self, fixture: Fixture) -> None:
        """打开手动 GDTF 选择对话框"""
        dialog = GDTFSelectDialog(fixture, self.library, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            profile, mode = dialog.get_selection()
            if profile:
                MVRImporter.manual_link(fixture, profile, mode)
                self._refresh_table()
                self.fixtures_changed.emit()

    def _unlink(self, fixture: Fixture) -> None:
        """取消灯具链接"""
        fixture.unlink_profile()
        self._refresh_table()
        self.fixtures_changed.emit()

    def set_fixtures(self, fixtures: List[Fixture]) -> None:
        """外部设置灯具列表"""
        self.fixtures = fixtures
        self._refresh_table()

    def get_patched_fixtures(self) -> List[Fixture]:
        """获取所有已 patch 的灯具"""
        return [f for f in self.fixtures if f.is_patched]
    
    def get_selected_fixtures(self) -> List[Fixture]:
        """获取当前选中的灯具"""
        selected = []
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).isSelected():
                fixture = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                if fixture:
                    selected.append(fixture)
        return selected
    
    def _on_search_changed(self, text: str) -> None:
        """搜索文本改变时过滤灯具"""
        self.search_text = text.strip().lower()
        self._apply_search_filter()
        self._refresh_table()
    
    def _apply_search_filter(self) -> None:
        """应用搜索过滤"""
        if not self.search_text:
            self.filtered_fixtures = self.fixtures
        else:
            self.filtered_fixtures = [
                f for f in self.fixtures
                if self.search_text in f.name.lower()
            ]
    
    def _on_select_all_changed(self, state: int) -> None:
        """全选复选框状态改变"""
        if state == Qt.CheckState.Checked.value:
            self.table.selectAll()
        else:
            self.table.clearSelection()
    
    def _on_invert_selection(self) -> None:
        """反选当前选中的行"""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setSelected(not item.isSelected())
    
    def _on_create_group(self) -> None:
        """创建新分组"""
        selected_fixtures = self.get_selected_fixtures()
        
        if not selected_fixtures:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "无选中灯具",
                "请先选择要添加到分组的灯具"
            )
            return
        
        # 发出信号请求主窗口创建分组
        self.create_group_requested.emit(selected_fixtures)

