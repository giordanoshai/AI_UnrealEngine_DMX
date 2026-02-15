"""
AetherLight Pro - Cue List 编辑页面

左侧列表显示所有 cue lists，右侧显示编辑表单
"""
from typing import Optional, Dict, List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QFormLayout, QGroupBox,
    QCheckBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QComboBox
)

from ..database.database import (
    list_cue_lists, get_cue_list, create_cue_list, update_cue_list, 
    delete_cue_list, list_effects
)


class CueListEditorPage(QWidget):
    """Cue List 编辑页面
    
    布局:
    ┌─────────────────────────────────────┐
    │  [新建] [删除] [保存]               │
    ├──────────────┬──────────────────────┤
    │  Cue List    │   编辑区域           │
    │   - List1    │   名称: [______]      │
    │   - List2    │   项目: [______]      │
    │   - List3    │   循环: [✓]           │
    │              │                       │
    │              │   [Cue 配置表格]      │
    │              │   [添加][删除][上移]  │
    │              │                       │
    └──────────────┴──────────────────────┘
    """
    
    cue_lists_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.current_cue_list_id: Optional[str] = None
        self.current_project_id: Optional[str] = None
        self.current_project_name: str = ""
        self.cue_lists: List[Dict] = []
        self.effects: List[Dict] = []
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self) -> None:
        """创建UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("➕ 新建 Cue List")
        self.new_btn.clicked.connect(self._on_new_cue_list)
        toolbar_layout.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self._on_delete_cue_list)
        self.delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_btn)
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self._on_save_cue_list)
        self.save_btn.setEnabled(False)
        toolbar_layout.addWidget(self.save_btn)
        
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # 分割器: 左侧列表 + 右侧编辑区
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧: Cue List 列表
        self.cue_list_widget = QListWidget()
        self.cue_list_widget.setMaximumWidth(300)
        self.cue_list_widget.currentItemChanged.connect(self._on_cue_list_selected)
        splitter.addWidget(self.cue_list_widget)
        
        # 右侧: 编辑区域
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # 基本信息表单
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入 Cue List 名称")
        self.name_edit.textChanged.connect(self._mark_modified)
        info_layout.addRow("名称:", self.name_edit)
        
        self.project_label = QLabel("未选择项目")
        self.project_label.setStyleSheet("color: #888;")
        info_layout.addRow("项目:", self.project_label)
        
        self.loop_checkbox = QCheckBox("循环播放")
        self.loop_checkbox.stateChanged.connect(self._mark_modified)
        info_layout.addRow("", self.loop_checkbox)
        
        info_group.setLayout(info_layout)
        editor_layout.addWidget(info_group)
        
        # Cue 配置表格
        cue_group = QGroupBox("Cue 配置")
        cue_layout = QVBoxLayout()
        
        # Cue 表格工具栏
        cue_toolbar = QHBoxLayout()
        
        self.add_cue_btn = QPushButton("➕ 添加 Cue")
        self.add_cue_btn.clicked.connect(self._on_add_cue)
        cue_toolbar.addWidget(self.add_cue_btn)
        
        self.remove_cue_btn = QPushButton("➖ 删除 Cue")
        self.remove_cue_btn.clicked.connect(self._on_remove_cue)
        cue_toolbar.addWidget(self.remove_cue_btn)
        
        self.move_up_btn = QPushButton("⬆️ 上移")
        self.move_up_btn.clicked.connect(self._on_move_cue_up)
        cue_toolbar.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇️ 下移")
        self.move_down_btn.clicked.connect(self._on_move_cue_down)
        cue_toolbar.addWidget(self.move_down_btn)
        
        cue_toolbar.addStretch()
        cue_layout.addLayout(cue_toolbar)
        
        # Cue 表格
        self.cue_table = QTableWidget()
        self.cue_table.setColumnCount(3)
        self.cue_table.setHorizontalHeaderLabels(["Start Effect", "Trans.", "Time (s)"])
        
        header = self.cue_table.horizontalHeader()
        # Effect 列交互式调整 (避免过度拉伸)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.cue_table.setColumnWidth(0, 240)
        # Transition 列自适应内容
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # Fade Time 列自适应内容
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # 增加行高
        self.cue_table.verticalHeader().setDefaultSectionSize(36)
        
        # 设置全局样式增加下拉框和输入框高度
        self.cue_table.setStyleSheet("""
            QComboBox, QLineEdit {
                min-height: 26px;
                padding: 2px;
                margin: 2px;
            }
            QComboBox::item {
                min-height: 26px;
            }
        """)
        
        self.cue_table.cellChanged.connect(self._mark_modified)
        
        cue_layout.addWidget(self.cue_table)
        cue_group.setLayout(cue_layout)
        editor_layout.addWidget(cue_group)
        
        splitter.addWidget(editor_widget)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def set_current_project(self, project: Dict) -> None:
        """设置当前激活的项目"""
        if not project:
            self.current_project_id = None
            self.current_project_name = "未选择项目"
            self.project_label.setText("未选择项目")
            return

        if hasattr(project, "project_info"):
            # It's a Project object
            self.current_project_id = project.project_info.uuid
            self.current_project_name = project.project_info.name
        elif isinstance(project, dict):
            # Try to find uuid
            if "project_info" in project:
                 self.current_project_id = project["project_info"].get("uuid")
                 self.current_project_name = project["project_info"].get("name")
            else:
                 # Fallback
                 self.current_project_name = project.get("project_name", "Unknown")
                 self.current_project_id = project.get("id")
        
        self.project_label.setText(self.current_project_name)
    
    def _load_data(self) -> None:
        """从数据库加载所有数据"""
        self.effects = list_effects()
        self.cue_lists = list_cue_lists()
        self._refresh_cue_list()
    
    def _refresh_cue_list(self) -> None:
        """刷新 cue list 列表"""
        self.cue_list_widget.clear()
        
        for cue_list in self.cue_lists:
            # Optionally filter by current project
            item = QListWidgetItem(cue_list["cue_list_name"])
            item.setData(Qt.ItemDataRole.UserRole, cue_list["id"])
            self.cue_list_widget.addItem(item)
    
    def _on_cue_list_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """Cue List 被选中"""
        if not current:
            self.current_cue_list_id = None
            self.delete_btn.setEnabled(False)
            return
        
        cue_list_id = current.data(Qt.ItemDataRole.UserRole)
        self.current_cue_list_id = cue_list_id
        self.delete_btn.setEnabled(True)
        
        # 加载 cue list 详情
        cue_list = get_cue_list(cue_list_id)
        if cue_list:
            self._load_cue_list_to_form(cue_list)
    
    def _load_cue_list_to_form(self, cue_list: Dict) -> None:
        """将 cue list 数据加载到表单"""
        self.name_edit.blockSignals(True)
        self.loop_checkbox.blockSignals(True)
        self.cue_table.blockSignals(True)
        
        self.name_edit.setText(cue_list.get("cue_list_name", ""))
        
        pid = cue_list.get("project_id")
        if pid == self.current_project_id:
             self.project_label.setText(self.current_project_name)
        else:
             self.project_label.setText(f"Project ID: {pid}" if pid else "无项目")

        self.loop_checkbox.setChecked(cue_list.get("loop", False))
        
        # 加载 cues
        self.cue_table.setRowCount(0)
        cues = cue_list.get("cues", [])
        for cue in cues:
            self._add_cue_row(cue)
        
        self.name_edit.blockSignals(False)
        self.loop_checkbox.blockSignals(False)
        self.cue_table.blockSignals(False)
        
        self.save_btn.setEnabled(False)
    
    def _add_cue_row(self, cue: Optional[Dict] = None) -> None:
        """添加一行 cue 到表格"""
        row = self.cue_table.rowCount()
        self.cue_table.insertRow(row)
        
        # Effect 下拉框
        effect_combo = QComboBox()
        for effect in self.effects:
            effect_combo.addItem(effect["effect_name"], effect["id"])
        
        if cue:
            effect_id = cue.get("effect_id", "")
            for i in range(effect_combo.count()):
                if effect_combo.itemData(i) == effect_id:
                    effect_combo.setCurrentIndex(i)
                    break
        
        effect_combo.currentIndexChanged.connect(self._mark_modified)
        self.cue_table.setCellWidget(row, 0, effect_combo)
        
        # Transition 下拉框
        transition_combo = QComboBox()
        transition_combo.addItem("CUT", "CUT")
        transition_combo.addItem("FADE", "FADE")
        
        if cue:
            transition = cue.get("transition", "CUT")
            idx = 0 if transition == "CUT" else 1
            transition_combo.setCurrentIndex(idx)
        
        transition_combo.currentIndexChanged.connect(self._mark_modified)
        self.cue_table.setCellWidget(row, 1, transition_combo)
        
        # Fade Time
        fade_time = cue.get("fade_time", 1.0) if cue else 1.0
        fade_item = QTableWidgetItem(str(fade_time))
        self.cue_table.setItem(row, 2, fade_item)

    def _mark_modified(self) -> None:
        """标记为已修改"""
        self.save_btn.setEnabled(True)
    
    def _on_new_cue_list(self) -> None:
        """创建新的 cue list"""
        if not self.current_project_id:
            QMessageBox.warning(self, "无法创建", "当前未打开任何项目")
            return
        
        project_id = self.current_project_id
        
        cue_list = create_cue_list(
            cue_list_name="新 Cue List",
            project_id=project_id,
            cues=[],
            loop=False
        )
        
        if cue_list:
            self.cue_lists.append(cue_list)
            self._refresh_cue_list()
            
            # 选中新创建的 cue list
            for i in range(self.cue_list_widget.count()):
                item = self.cue_list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == cue_list["id"]:
                    self.cue_list_widget.setCurrentItem(item)
                    break
            
            self.cue_lists_changed.emit()
    
    def _on_delete_cue_list(self) -> None:
        """删除当前 cue list"""
        if not self.current_cue_list_id:
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个 Cue List 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if delete_cue_list(self.current_cue_list_id):
                self._load_data()
                self.current_cue_list_id = None
                self.cue_lists_changed.emit()
            else:
                QMessageBox.warning(self, "删除失败", "无法删除 Cue List")
    
    def _on_save_cue_list(self) -> None:
        """保存当前 cue list"""
        if not self.current_cue_list_id:
            return
        
        # 从表单收集数据
        cue_list_name = self.name_edit.text().strip()
        loop = self.loop_checkbox.isChecked()
        
        if not cue_list_name:
            QMessageBox.warning(self, "验证失败", "Cue List 名称不能为空")
            return
        
        # 从表格收集 cues
        cues = []
        for row in range(self.cue_table.rowCount()):
            effect_combo = self.cue_table.cellWidget(row, 0)
            transition_combo = self.cue_table.cellWidget(row, 1)
            fade_item = self.cue_table.item(row, 2)
            
            if effect_combo and transition_combo and fade_item:
                cue = {
                    "effect_id": effect_combo.currentData(),
                    "transition": transition_combo.currentData(),
                    "fade_time": float(fade_item.text() or "1.0"),
                }
                cues.append(cue)
        
        # 更新数据库
        result = update_cue_list(
            self.current_cue_list_id,
            cue_list_name=cue_list_name,
            cues=cues,
            loop=loop
        )
        
        if result:
            self._load_data()
            self.save_btn.setEnabled(False)
            self.cue_lists_changed.emit()
            QMessageBox.information(self, "保存成功", "Cue List 已保存")
        else:
            QMessageBox.warning(self, "保存失败", "无法保存 Cue List")
    
    def _on_add_cue(self) -> None:
        """添加新的 cue"""
        self._add_cue_row()
        self._mark_modified()
    
    def _on_remove_cue(self) -> None:
        """删除选中的 cue"""
        current_row = self.cue_table.currentRow()
        if current_row >= 0:
            self.cue_table.removeRow(current_row)
            self._mark_modified()
    
    def _on_move_cue_up(self) -> None:
        """上移选中的 cue"""
        current_row = self.cue_table.currentRow()
        if current_row > 0:
            self._swap_rows(current_row, current_row - 1)
            self.cue_table.setCurrentCell(current_row - 1, 0)
            self._mark_modified()
    
    def _on_move_cue_down(self) -> None:
        """下移选中的 cue"""
        current_row = self.cue_table.currentRow()
        if current_row >= 0 and current_row < self.cue_table.rowCount() - 1:
            self._swap_rows(current_row, current_row + 1)
            self.cue_table.setCurrentCell(current_row + 1, 0)
            self._mark_modified()
    
    def _swap_rows(self, row1: int, row2: int) -> None:
        """交换两行"""
        # 获取 row1 的数据
        effect_combo1 = self.cue_table.cellWidget(row1, 0)
        transition_combo1 = self.cue_table.cellWidget(row1, 1)
        fade_text1 = self.cue_table.item(row1, 2).text()
        
        effect_idx1 = effect_combo1.currentIndex() if effect_combo1 else 0
        transition_idx1 = transition_combo1.currentIndex() if transition_combo1 else 0
        
        # 获取 row2 的数据
        effect_combo2 = self.cue_table.cellWidget(row2, 0)
        transition_combo2 = self.cue_table.cellWidget(row2, 1)
        fade_text2 = self.cue_table.item(row2, 2).text()
        
        effect_idx2 = effect_combo2.currentIndex() if effect_combo2 else 0
        transition_idx2 = transition_combo2.currentIndex() if transition_combo2 else 0
        
        # 交换 row1 和 row2
        if effect_combo1:
            effect_combo1.setCurrentIndex(effect_idx2)
        if transition_combo1:
            transition_combo1.setCurrentIndex(transition_idx2)
        self.cue_table.item(row1, 2).setText(fade_text2)
        
        if effect_combo2:
            effect_combo2.setCurrentIndex(effect_idx1)
        if transition_combo2:
            transition_combo2.setCurrentIndex(transition_idx1)
        self.cue_table.item(row2, 2).setText(fade_text1)
