"""
AetherLight Pro - Effect 编辑页面

左侧列表显示所有 effects，右侧显示编辑表单
"""
from typing import Optional, Dict, List, Any
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFormLayout, QGroupBox,
    QScrollArea, QDoubleSpinBox, QComboBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QStackedWidget, QFrame
)

from ..database.database import (
    list_effects, get_effect, create_effect, update_effect, delete_effect,
    get_fixture_profile
)
from ..primitives import ANIMATIONS

# 定义动画参数元数据
ANIMATION_PARAMS = {
    "static": [("value", "float", 0.0, 1.0)],
    "wave": [
        ("speed", "float", 0.0, 10.0),
        ("min", "float", 0.0, 1.0),
        ("max", "float", 0.0, 1.0),
        ("phase", "float", 0.0, 1.0) # Special case: 'auto' is string, handle later if needed
    ],
    "pulse": [
        ("speed", "float", 0.0, 10.0),
        ("min", "float", 0.0, 1.0),
        ("max", "float", 0.0, 1.0),
        ("duty_cycle", "float", 0.0, 1.0),
        ("phase", "float", 0.0, 1.0)
    ],
    "ramp": [
        ("speed", "float", 0.0, 10.0),
        ("min", "float", 0.0, 1.0),
        ("max", "float", 0.0, 1.0),
        ("phase", "float", 0.0, 1.0)
    ],
    "step": [
        ("values", "list", 0.0, 1.0), # Comma separated
        ("hold_time", "float", 0.1, 60.0)
    ]
}

class EffectEditorPage(QWidget):
    """Effect 编辑页面"""
    
    effects_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.current_effect_id: Optional[str] = None
        self.effects: List[Dict] = []

        
        # 存储当前编辑的通道配置
        # Structure: { "channel_name": { "animation": "type", "params": {...} } }
        self.channel_configs: Dict[str, Dict] = {} 
        
        self._setup_ui()
        self._load_effects()
        
    def _get_active_profile_channels(self) -> Dict:
        """获取当前激活的灯具 Profile 通道配置"""
        # 优先尝试获取通用配置
        # 这里暂时使用 hardcoded default fallback，实际应从 Project 或 Config 获取
        default_channels = {
            "pan": {"type": "continuous", "default_value": 0.5},
            "tilt": {"type": "continuous", "default_value": 0.5},
            "dimmer": {"type": "continuous", "default_value": 0.0},
            "shutter": {"type": "continuous", "default_value": 1.0},
            "color_wheel": {"type": "discrete", "default_value": "white"},
            "gobo_wheel": {"type": "discrete", "default_value": "open"},
            "zoom": {"type": "continuous", "default_value": 0.5},
        }
        return default_channels
    
    def _setup_ui(self) -> None:
        """创建UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("➕ 新建 Effect")
        self.new_btn.clicked.connect(self._on_new_effect)
        toolbar_layout.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self._on_delete_effect)
        self.delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.delete_btn)
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self._on_save_effect)
        self.save_btn.setEnabled(False)
        toolbar_layout.addWidget(self.save_btn)
        
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # 2. 主体分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 2.1 左侧: Effect 列表
        self.effect_list = QListWidget()
        self.effect_list.setMaximumWidth(250)
        self.effect_list.currentItemChanged.connect(self._on_effect_selected)
        splitter.addWidget(self.effect_list)
        
        # 2.2 右侧: 编辑区域
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # 2.2.1 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._mark_modified)
        info_layout.addRow("名称:", self.name_edit)
        
        self.description_edit = QLineEdit()
        self.description_edit.textChanged.connect(self._mark_modified)
        info_layout.addRow("描述:", self.description_edit)
        
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 3600.0)
        self.duration_spin.setSuffix(" 秒")
        self.duration_spin.valueChanged.connect(self._mark_modified)
        info_layout.addRow("时长:", self.duration_spin)
        
        info_group.setLayout(info_layout)
        editor_layout.addWidget(info_group)
        
        # 2.2.2 Channel 列表 (表格)
        channel_group = QGroupBox("通道动画配置")
        channel_layout = QVBoxLayout()
        
        self.channel_table = QTableWidget()
        self.channel_table.setColumnCount(2)
        self.channel_table.setHorizontalHeaderLabels(["Channel", "Animation Type"])
        self.channel_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.channel_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.channel_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.channel_table.itemSelectionChanged.connect(self._on_channel_selected)
        
        channel_layout.addWidget(self.channel_table)
        channel_group.setLayout(channel_layout)
        editor_layout.addWidget(channel_group)
        
        # 2.2.3 参数编辑区
        self.param_group = QGroupBox("参数设置 (未选择通道)")
        self.param_layout = QFormLayout()
        self.param_group.setLayout(self.param_layout)
        editor_layout.addWidget(self.param_group)
        
        splitter.addWidget(editor_widget)
        splitter.setStretchFactor(1, 3)
        main_layout.addWidget(splitter)
        
        # 初始化通道配置缓存
        self._init_channel_configs()
        self._populate_channel_table()

    def _init_channel_configs(self):
        """初始化默认通道配置"""
        self.channel_configs = {}
        channels = self._get_active_profile_channels()
        for ch_name, config in channels.items():
            default_val = config.get("default_value", 0.0)
            self.channel_configs[ch_name] = {
                "animation": "static",
                "params": {"value": default_val}
            }

    def _populate_channel_table(self) -> None:
        """根据 Profile 填充表格行"""
        self.channel_table.blockSignals(True)
        self.channel_table.setRowCount(0)
        
        channels = self._get_active_profile_channels()
        sorted_channels = sorted(channels.keys())
        
        for row, ch_name in enumerate(sorted_channels):
            self.channel_table.insertRow(row)
            
            # Col 0: Name
            name_item = QTableWidgetItem(ch_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.channel_table.setItem(row, 0, name_item)
            
            # Col 1: Animation Type Combo
            combo = QComboBox()
            combo.setMinimumHeight(26)

            combo.setStyleSheet("""


                QComboBox QAbstractItemView {
                    min-height: 28px;
                }
                """)

            combo.addItems(ANIMATIONS.keys())
            # Set current value from config
            current_anim = self.channel_configs.get(ch_name, {}).get("animation", "static")
            combo.setCurrentText(current_anim)
            
            # Use a closure/lambda to capture channel name
            combo.currentTextChanged.connect(lambda text, ch=ch_name: self._on_animation_type_changed(ch, text))
            
            self.channel_table.setCellWidget(row, 1, combo)
            
        self.channel_table.blockSignals(False)

    def _on_animation_type_changed(self, channel_name: str, new_anim: str):
        """当表格中的动画类型改变时"""
        if channel_name in self.channel_configs:
            self.channel_configs[channel_name]["animation"] = new_anim
            # 重置 params 为默认值? 或者保留共有的 params?
            # 这里简单起见，仅保留 value 如果切回 static，其他重置
            # 实际应用中可能需要更智能的保留策略
            
            # 如果是当前选中的行，刷新参数面板
            selected_items = self.channel_table.selectedItems()
            if selected_items:
                selected_row = selected_items[0].row()
                selected_ch = self.channel_table.item(selected_row, 0).text()
                if selected_ch == channel_name:
                    self._refresh_param_editor(channel_name)
            
            self._mark_modified()

    def _on_channel_selected(self):
        """当选中表格某一行时"""
        selected_items = self.channel_table.selectedItems()
        if not selected_items:
            self.param_group.setTitle("参数设置 (未选择通道)")
            self._clear_layout(self.param_layout)
            return
        
        row = selected_items[0].row()
        channel_name = self.channel_table.item(row, 0).text()
        self._refresh_param_editor(channel_name)

    def _refresh_param_editor(self, channel_name: str):
        """刷新下方参数编辑区域"""
        self.param_group.setTitle(f"参数设置: {channel_name}")
        self._clear_layout(self.param_layout)
        
        if channel_name not in self.channel_configs:
            return
            
        config = self.channel_configs[channel_name]
        anim_type = config.get("animation", "static")
        current_params = config.get("params", {})
        
        # 获取该动画类型的参数定义
        param_defs = ANIMATION_PARAMS.get(anim_type, [])
        
        for p_name, p_type, p_min, p_max in param_defs:
            label = QLabel(f"{p_name}:")
            
            val = current_params.get(p_name)
            
            if p_type == "float":
                widget = QDoubleSpinBox()
                widget.setRange(p_min, p_max)
                widget.setSingleStep(0.1)
                # Set value, default to min if not set (or 0 for value)
                if val is None:
                    val = 0.5 if p_name == "value" else p_min
                try:
                    widget.setValue(float(val))
                except:
                    widget.setValue(p_min)
                
                widget.valueChanged.connect(lambda v, p=p_name, ch=channel_name: self._on_param_changed(ch, p, v))
                
            elif p_type == "list":
                widget = QLineEdit()
                if isinstance(val, list):
                    widget.setText(",".join(map(str, val)))
                elif val:
                    widget.setText(str(val))
                widget.textChanged.connect(lambda text, p=p_name, ch=channel_name: self._update_list_param(ch, p, text))
            
            else:
                widget = QLabel("Unknown type")
            
            self.param_layout.addRow(label, widget)

    def _on_param_changed(self, channel_name: str, param_name: str, value: float):
        """参数值改变"""
        if channel_name in self.channel_configs:
            if "params" not in self.channel_configs[channel_name]:
                self.channel_configs[channel_name]["params"] = {}
            self.channel_configs[channel_name]["params"][param_name] = value
            self._mark_modified()

    def _update_list_param(self, channel_name: str, param_name: str, text: str):
        """列表类型参数改变"""
        # Parse comma separated values
        values = [v.strip() for v in text.split(",") if v.strip()]
        # Convert to numbers if possible (optional, logic depends on usage)
        # primitive.py logic just returns values[index], so strings are fine for gobos
        
        if channel_name in self.channel_configs:
            if "params" not in self.channel_configs[channel_name]:
                self.channel_configs[channel_name]["params"] = {}
            self.channel_configs[channel_name]["params"][param_name] = values
            self._mark_modified()

    def _clear_layout(self, layout: QFormLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _load_effects(self) -> None:
        """从数据库加载所有 effects"""
        self.effects = list_effects()
        self._refresh_effect_list()
    
    def _refresh_effect_list(self) -> None:
        """刷新 effect 列表"""
        self.effect_list.clear()
        for effect in self.effects:
            item = QListWidgetItem(effect["effect_name"])
            item.setData(Qt.ItemDataRole.UserRole, effect["id"])
            self.effect_list.addItem(item)
    
    def _on_effect_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """Effect 被选中"""
        if not current:
            self.current_effect_id = None
            self.delete_btn.setEnabled(False)
            self._reset_form()
            return
        
        effect_id = current.data(Qt.ItemDataRole.UserRole)
        self.current_effect_id = effect_id
        self.delete_btn.setEnabled(True)
        
        effect = get_effect(effect_id=effect_id)
        if effect:
            self._load_effect_to_form(effect)
            
    def _reset_form(self):
        """重置表单到初始状态"""
        self.name_edit.clear()
        self.description_edit.clear()
        self.duration_spin.setValue(10.0)
        self._init_channel_configs()
        self._populate_channel_table()
        self.param_group.setTitle("参数设置 (未选择通道)")
        self._clear_layout(self.param_layout)
        self.save_btn.setEnabled(False)

    def _load_effect_to_form(self, effect: Dict) -> None:
        """将 effect 数据加载到表单"""
        # 1. Basic Info
        self.name_edit.setText(effect.get("effect_name", ""))
        self.description_edit.setText(effect.get("description", ""))
        self.duration_spin.setValue(float(effect.get("duration", 10.0)))
        
        # 2. Primitives -> Channel Configs
        # Reset to default first
        self._init_channel_configs()
        
        primitives = effect.get("primitives", [])
        for prim in primitives:
            ch_name = prim.get("channel")
            if ch_name and ch_name in self.channel_configs:
                self.channel_configs[ch_name]["animation"] = prim.get("animation", "static")
                self.channel_configs[ch_name]["params"] = prim.get("params", {})
        
        # 3. Refresh UI
        self._populate_channel_table()
        
        # Clear param selection
        self.param_group.setTitle("参数设置 (请在上方表格选择通道)")
        self._clear_layout(self.param_layout)
        
        self.save_btn.setEnabled(False)
    
    def _mark_modified(self) -> None:
        """标记为已修改"""
        self.save_btn.setEnabled(True)
    
    def _on_new_effect(self) -> None:
        """创建新的 effect"""
        self._reset_form()
        
        # Create dummy initial data
        primitives = []
        for ch, conf in self.channel_configs.items():
            primitives.append({
                "channel": ch,
                "animation": conf["animation"],
                "params": conf["params"]
            })
            
        effect = create_effect(
            effect_name="New Effect",
            description="Description",
            primitives=primitives,
            duration=10.0
        )
        
        if effect:
            self._load_effects()
            # Select new
            for i in range(self.effect_list.count()):
                if self.effect_list.item(i).data(Qt.ItemDataRole.UserRole) == effect["id"]:
                    self.effect_list.setCurrentRow(i)
                    break
    
    def _on_delete_effect(self) -> None:
        """删除当前 effect"""
        if not self.current_effect_id:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个 Effect 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if delete_effect(self.current_effect_id):
                self._load_effects()
                self.current_effect_id = None
                self._reset_form()
    
    def _on_save_effect(self) -> None:
        """保存当前 effect"""
        if not self.current_effect_id:
            return
        
        effect_name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        duration = self.duration_spin.value()
        
        if not effect_name:
            QMessageBox.warning(self, "错误", "名称不能为空")
            return
            
        # Reconstruct primitives list
        primitives = []
        for ch_name, conf in self.channel_configs.items():
            primitives.append({
                "channel": ch_name,
                "animation": conf["animation"],
                "params": conf["params"]
            })
            
        result = update_effect(
            self.current_effect_id,
            effect_name=effect_name,
            description=description,
            primitives=primitives,
            duration=duration
        )
        
        if result:
            self._load_effects()
            # Restore selection
            for i in range(self.effect_list.count()):
                if self.effect_list.item(i).data(Qt.ItemDataRole.UserRole) == self.current_effect_id:
                    self.effect_list.setCurrentRow(i)
                    break
            self.save_btn.setEnabled(False)
            self.effects_changed.emit()
            QMessageBox.information(self, "保存成功", "Effect 已保存")
        else:
            QMessageBox.warning(self, "保存失败", "无法保存 Effect")
