"""
AetherLight Pro - 导入页面

集中管理 GDTF 和 MVR 的导入功能。
"""
from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt

from ..gdtf_parser import GDTFLibrary
from ..models import Fixture
from .gdtf_panel import GDTFPanel
from .fixture_panel import FixturePanel

logger = logging.getLogger(__name__)


class ImportPage(QWidget):
    """导入页面 - 管理 GDTF 和 MVR 导入。
    
    布局:
    ┌─────────────────────────────────────┐
    │  [Import GDTF] [Import MVR] [Re-Link]│
    ├──────────────┬──────────────────────┤
    │  GDTF Panel  │   Fixture Panel      │
    │  (Library)   │   (Imported Fixtures)│
    └──────────────┴──────────────────────┘
    
    Signals:
        fixtures_imported: 灯具导入完成
    """
    
    fixtures_imported = pyqtSignal()
    
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
        layout.setSpacing(12)
        
        # --- 标题和操作按钮 ---
        header_layout = QHBoxLayout()
        
        title = QLabel("导入管理")
        title.setObjectName("sectionTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #53a8f9;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Import GDTF 按钮
        self.import_gdtf_btn = QPushButton("📁 Import GDTF")
        self.import_gdtf_btn.setObjectName("accentButton")
        self.import_gdtf_btn.setMinimumWidth(150)
        header_layout.addWidget(self.import_gdtf_btn)
        
        # Import MVR 按钮
        self.import_mvr_btn = QPushButton("📦 Import MVR")
        self.import_mvr_btn.setObjectName("accentButton")
        self.import_mvr_btn.setMinimumWidth(150)
        header_layout.addWidget(self.import_mvr_btn)
        
        # Re-Link All 按钮
        self.relink_btn = QPushButton("🔗 Re-Link All")
        self.relink_btn.setObjectName("successButton")
        self.relink_btn.setMinimumWidth(150)
        header_layout.addWidget(self.relink_btn)
        
        layout.addLayout(header_layout)
        
        # --- 主内容区域 - 两栏布局 ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧: GDTF 库面板
        self.gdtf_panel = GDTFPanel(self.library)
        self.gdtf_panel.setMinimumWidth(300)
        self.gdtf_panel.setMaximumWidth(500)
        splitter.addWidget(self.gdtf_panel)
        
        # 右侧: 灯具列表面板
        self.fixture_panel = FixturePanel(self.library)
        # 隐藏创建分组按钮（这个功能在分组管理页面）
        self.fixture_panel.create_group_btn.hide()
        splitter.addWidget(self.fixture_panel)
        
        # 设置初始分割比例 (3:7)
        splitter.setSizes([350, 850])
        
        layout.addWidget(splitter, 1)
        
        # --- 连接信号 ---
        self._connect_signals()
    
    def _connect_signals(self) -> None:
        """连接信号"""
        self.import_gdtf_btn.clicked.connect(self.gdtf_panel._on_import_clicked)
        self.import_mvr_btn.clicked.connect(self.fixture_panel._on_import_mvr)
        self.relink_btn.clicked.connect(self.fixture_panel._relink_all)
        self.fixture_panel.fixtures_changed.connect(self.fixtures_imported)
