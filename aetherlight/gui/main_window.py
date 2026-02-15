"""
AetherLight Pro - 主窗口

应用的顶级窗口，组合 GDTF 库面板和灯具列表面板。
"""
from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..gdtf_parser import GDTFLibrary
from ..models import Fixture
from ..project_manager import ProjectManager, Project
from .import_page import ImportPage
from .group_management_page import GroupManagementPage
from .effect_editor_page import EffectEditorPage
from .cue_list_editor_page import CueListEditorPage
from .cue_list_editor_page import CueListEditorPage
from .theme import get_dark_stylesheet
# from .login_dialog import LoginDialog
from ..database.auth_manager import get_auth_manager
# from ..database.sync_manager import get_sync_manager
from PyQt6.QtCore import QTimer

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """AetherLight Pro 主窗口。

    布局:
    ┌──────────────────────────────────────────────┐
    │  Toolbar: [Import GDTF] [Import MVR]         │
    ├──────────────┬───────────────────────────────┤
    │  GDTF Panel  │      Fixture Panel            │
    │  (Library)   │      (Patch Table)             │
    │              │                               │
    ├──────────────┴───────────────────────────────┤
    │  Status Bar                                   │
    └──────────────────────────────────────────────┘
    """

    def __init__(self) -> None:
        super().__init__()

        # --- 核心数据 ---
        # 启用数据库模式的 GDTF Library (实际上现在使用 LocalCache)
        self.library = GDTFLibrary()
        
        # 项目管理器
        self.project_manager = ProjectManager("projects")
        self.current_project: Optional[Project] = None
        self.project_modified = False

        # --- 认证与同步 ---
        # --- 认证与同步 ---
        # self.auth_manager = get_auth_manager()
        # self.sync_manager = get_sync_manager()
        # self.sync_timer = QTimer(self)
        # self.sync_timer.timeout.connect(self._auto_sync)
        # 每 30 秒自动同步一次
        # self.sync_timer.start(30000)  

        # --- UI 初始化 ---
        self._setup_window()
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_panels()
        self._setup_statusbar()
        self._connect_signals()

        # --- 应用暗色主题 ---
        self.setStyleSheet(get_dark_stylesheet())
        
        # --- 自动加载上次项目或创建默认项目 ---
        self._load_or_create_project()

        logger.info("AetherLight Pro 主窗口已初始化")

    def _setup_window(self) -> None:
        """配置窗口属性"""
        self.setWindowTitle("AetherLight Pro — Lighting Control")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)

        # 居中显示
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            x = (screen_rect.width() - 1400) // 2
            y = (screen_rect.height() - 800) // 2
            self.move(max(0, x), max(0, y))

    def showEvent(self, event) -> None:
        """窗口显示事件"""
        super().showEvent(event)
        # 单机模式不再检查登录

    
    def _setup_menubar(self) -> None:
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # --- File 菜单 ---
        file_menu = menubar.addMenu("&File")
        
        # New Project
        new_project_action = QAction("&New Project...", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        # Open Project
        open_project_action = QAction("&Open Project...", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        # Save Project
        self.save_project_action = QAction("&Save Project", self)
        self.save_project_action.setShortcut("Ctrl+S")
        self.save_project_action.triggered.connect(self._save_project)
        file_menu.addAction(self.save_project_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # --- Auth 菜单 (移除) ---
        # auth_menu = menubar.addMenu("&Auth")
        
        # self.login_action = QAction("登录...", self)
        # self.login_action.triggered.connect(self._show_login_dialog)
        # auth_menu.addAction(self.login_action)
        
        # self.logout_action = QAction("登出", self)
        # self.logout_action.triggered.connect(self._logout)
        # auth_menu.addAction(self.logout_action)
        
        # --- Import 菜单 ---
        import_menu = menubar.addMenu("&Import")
        
        # Import GDTF
        import_gdtf_action = QAction("📁 Import &GDTF...", self)
        import_gdtf_action.setShortcut("Ctrl+G")
        import_gdtf_action.triggered.connect(self._import_gdtf)
        import_menu.addAction(import_gdtf_action)
        
        # Import MVR
        import_mvr_action = QAction("📦 Import &MVR...", self)
        import_mvr_action.setShortcut("Ctrl+M")
        import_mvr_action.triggered.connect(self._import_mvr)
        import_menu.addAction(import_mvr_action)
        
        import_menu.addSeparator()
        
        # Re-Link All
        relink_action = QAction("🔗 &Re-Link All", self)
        relink_action.setShortcut("Ctrl+R")
        relink_action.triggered.connect(self._relink_all)
        import_menu.addAction(relink_action)

    def _setup_toolbar(self) -> None:
        """创建工具栏 - 页面切换按钮"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        # --- Logo / 标题 ---
        logo_label = QLabel("  ✦ AetherLight Pro  ")
        logo_label.setStyleSheet(
            "color: #53a8f9; font-size: 16px; font-weight: bold; "
            "background: transparent; margin-right: 30px; "
            "font-family: 'Segoe UI', sans-serif;"
        )
        toolbar.addWidget(logo_label)
        toolbar.addWidget(logo_label)
        toolbar.addSeparator()
        
        # --- 同步按钮 (移除) ---
        # self.sync_action = QAction("🔄 同步", self)
        # self.sync_action.triggered.connect(self._manual_sync)
        # toolbar.addAction(self.sync_action)
        # toolbar.addSeparator()
        
        # --- 页面切换按钮 ---
        # 导入管理按钮
        import_page_action = QAction("📁 导入管理", self)
        import_page_action.setCheckable(True)
        import_page_action.setChecked(True)
        import_page_action.triggered.connect(lambda: self._switch_page(0))
        toolbar.addAction(import_page_action)
        self.import_page_action = import_page_action
        
        # 分组管理按钮
        group_page_action = QAction("📋 分组管理", self)
        group_page_action.setCheckable(True)
        group_page_action.triggered.connect(lambda: self._switch_page(1))
        toolbar.addAction(group_page_action)
        self.group_page_action = group_page_action
        
        # Effect 编辑按钮
        effect_page_action = QAction("✨ Effect 编辑", self)
        effect_page_action.setCheckable(True)
        effect_page_action.triggered.connect(lambda: self._switch_page(2))
        toolbar.addAction(effect_page_action)
        self.effect_page_action = effect_page_action
        
        # Cue List 编辑按钮
        cue_list_page_action = QAction("🎬 Cue List 编辑", self)
        cue_list_page_action.setCheckable(True)
        cue_list_page_action.triggered.connect(lambda: self._switch_page(3))
        toolbar.addAction(cue_list_page_action)
        self.cue_list_page_action = cue_list_page_action
        
        self.addToolBar(toolbar)

    def _setup_panels(self) -> None:
        """创建主面板布局 - 页面切换"""
        # 使用 QStackedWidget 实现页面切换
        self.stacked_widget = QStackedWidget()

        # 页面 0: 导入管理页面
        self.import_page = ImportPage(self.library)
        self.stacked_widget.addWidget(self.import_page)

        # 页面 1: 分组管理页面
        self.group_management_page = GroupManagementPage(self.library)
        self.stacked_widget.addWidget(self.group_management_page)
        
        # 页面 2: Effect 编辑页面
        self.effect_editor_page = EffectEditorPage()
        self.stacked_widget.addWidget(self.effect_editor_page)
        
        # 页面 3: Cue List 编辑页面
        self.cue_list_editor_page = CueListEditorPage()
        self.stacked_widget.addWidget(self.cue_list_editor_page)

        self.setCentralWidget(self.stacked_widget)

    def _setup_statusbar(self) -> None:
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8888aa;")
        self.status_bar.addWidget(self.status_label, 1)

        self.fixture_count_label = QLabel("Fixtures: 0")
        self.fixture_count_label.setStyleSheet("color: #53a8f9;")
        self.status_bar.addPermanentWidget(self.fixture_count_label)

        self.profile_count_label = QLabel("Profiles: 0")
        self.profile_count_label.setStyleSheet("color: #00b894;")
        self.status_bar.addPermanentWidget(self.profile_count_label)

        # self.auth_status_label = QLabel("未登录")
        # self.auth_status_label.setStyleSheet("color: #ff5555;")
        # self.status_bar.addPermanentWidget(self.auth_status_label)
        
        # 初始检查认证状态
        # self._update_auth_status()

    def _connect_signals(self) -> None:
        """连接信号与槽"""
        # 导入页面信号
        self.import_page.gdtf_panel.library_changed.connect(self._on_library_changed)
        self.import_page.fixtures_imported.connect(self._on_fixtures_imported)
        self.import_page.fixture_panel.fixtures_changed.connect(self._mark_project_modified)
        
        # 分组管理页面信号
        self.group_management_page.groups_changed.connect(self._on_groups_changed)
        self.group_management_page.groups_changed.connect(self._mark_project_modified)

    # ------------------------------------------------------------------
    # 页面切换
    # ------------------------------------------------------------------
    
    def _switch_page(self, index: int) -> None:
        """切换页面"""
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮状态
        self.import_page_action.setChecked(index == 0)
        self.group_page_action.setChecked(index == 1)
        self.effect_page_action.setChecked(index == 2)
        self.cue_list_page_action.setChecked(index == 3)
        
        # 更新状态栏
        if index == 0:
            self.status_label.setText("导入管理")
        elif index == 1:
            self.status_label.setText("分组管理")
            # 切换到分组页面时，同步灯具数据
            self.group_management_page.set_fixtures(self.import_page.fixture_panel.fixtures)
        elif index == 2:
            self.status_label.setText("Effect 编辑")
        elif index == 3:
            self.status_label.setText("Cue List 编辑")

    # ------------------------------------------------------------------
    # 工具栏动作
    # ------------------------------------------------------------------

    def _import_gdtf(self) -> None:
        """从菜单桥导入 GDTF"""
        self._switch_page(0)  # 切换到导入页面
        self.import_page.gdtf_panel._on_import_clicked()

    def _import_mvr(self) -> None:
        """从菜单栏导入 MVR"""
        self._switch_page(0)  # 切换到导入页面
        self.import_page.fixture_panel._on_import_mvr()

    def _relink_all(self) -> None:
        """从菜单栏重新链接"""
        self._switch_page(0)  # 切换到导入页面
        self.import_page.fixture_panel._relink_all()

    # ------------------------------------------------------------------
    # 信号处理
    # ------------------------------------------------------------------

    def _on_library_changed(self) -> None:
        """هDTF 库变化时"""
        self.profile_count_label.setText(
            f"Profiles: {self.library.count}"
        )
        self.status_label.setText(
            f"GDTF 库已更新 — {self.library.count} 个 Profile 已加载"
        )
    
    def _on_fixtures_imported(self) -> None:
        """灯具导入完成时"""
        fixtures = self.import_page.fixture_panel.fixtures
        total = len(fixtures)
        patched = len(self.import_page.fixture_panel.get_patched_fixtures())
        self.fixture_count_label.setText(
            f"Fixtures: {patched}/{total}"
        )
        self.status_label.setText(
            f"灯具已更新 — {patched}/{total} Patched"
        )
    
    def _on_groups_changed(self) -> None:
        """分组变化时"""
        groups = self.group_management_page.groups
        self.status_label.setText(
            f"分组已更新 — {len(groups)} 个分组"
        )
    
    # ------------------------------------------------------------------
    # 项目管理
    # ------------------------------------------------------------------
    
    def _load_or_create_project(self) -> None:
        """启动时加载上次项目或创建默认项目"""
        try:
            # 从本地缓存加载所有 GDTF Profile
            count = self.library.load_from_cache()
            logger.info(f"从本地缓存加载了 {count} 个 GDTF Profile")
            self.import_page.gdtf_panel._refresh_tree()
            
            # 尝试加载默认项目
            projects = self.project_manager.list_projects()
            if projects:
                # 加载最近的项目
                self.current_project = self.project_manager.load_project(projects[0])
                self._apply_project()
                logger.info(f"已加载项目: {self.current_project.project_info.name}")
            else:
                # 创建默认项目
                self.current_project = self.project_manager.create_project("默认项目")
                logger.info("创建了默认项目")
            
            self._update_window_title()
            self.project_modified = False
            
        except Exception as e:
            logger.error(f"加载项目失败: {e}")
            # 创建新项目作为后备
            self.current_project = self.project_manager.create_project("新项目")
            self._update_window_title()
    
    def _apply_project(self) -> None:
        """将项目配置应用到界面"""
        if not self.current_project:
            return
        
        # 从项目恢复 fixtures 到导入页面
        self.import_page.fixture_panel.fixtures = self.current_project.fixtures
        
        # 重新链接 GDTF
        from ..mvr_importer import MVRImporter
        patched, unpatched = MVRImporter.link_fixtures(
            self.current_project.fixtures, self.library
        )
        
        # 刷新导入页面
        self.import_page.fixture_panel._refresh_table()
        self.import_page.fixtures_imported.emit()
        
        # 加载分组数据到分组管理页面
        self.group_management_page.set_groups(self.current_project.groups)
        self.group_management_page.set_fixtures(self.current_project.fixtures)
        
        # 更新 Cue List 编辑页面的当前项目
        self.cue_list_editor_page.set_current_project(self.current_project)
    
    def _new_project(self) -> None:
        """创建新项目"""
        from PyQt6.QtWidgets import QInputDialog
        
        # 检查是否需要保存当前项目
        if self.project_modified and not self._confirm_discard_changes():
            return
        
        name, ok = QInputDialog.getText(
            self, "新建项目", "项目名称:"
        )
        
        if ok and name:
            try:
                self.current_project = self.project_manager.create_project(name)
                self.import_page.fixture_panel.fixtures.clear()
                self.import_page.fixture_panel._refresh_table()
                self._update_window_title()
                self.project_modified = False
                
                # Update Cue List Page
                self.cue_list_editor_page.set_current_project(self.current_project)
                
                logger.info(f"创建新项目: {name}")
            except Exception as e:
                QMessageBox.warning(self, "创建失败", f"无法创建项目: {e}")
    
    def _open_project(self) -> None:
        """打开现有项目"""
        from PyQt6.QtWidgets import QInputDialog
        
        # 检查是否需要保存当前项目
        if self.project_modified and not self._confirm_discard_changes():
            return
        
        projects = self.project_manager.list_projects()
        if not projects:
            QMessageBox.information(self, "无项目", "还没有任何项目")
            return
        
        name, ok = QInputDialog.getItem(
            self, "打开项目", "选择项目:", projects, 0, False
        )
        
        if ok and name:
            try:
                self.current_project = self.project_manager.load_project(name)
                self._apply_project()
                self._update_window_title()
                self.project_modified = False
                logger.info(f"打开项目: {name}")
            except Exception as e:
                QMessageBox.warning(self, "打开失败", f"无法打开项目: {e}")
    
    def _save_project(self) -> None:
        """保存当前项目"""
        if not self.current_project:
            return
        
        try:
            # 更新项目数据
            self.current_project.fixtures = self.import_page.fixture_panel.fixtures
            self.current_project.groups = self.group_management_page.groups
            
            # 保存到文件
            self.project_manager.save_project(self.current_project)
            
            self.project_modified = False
            self._update_window_title()
            self.status_label.setText(f"项目已保存: {self.current_project.project_info.name}")
            logger.info(f"项目已保存: {self.current_project.project_info.name}")
            
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"无法保存项目: {e}")
    
    def _mark_project_modified(self) -> None:
        """标记项目已修改"""
        if not self.project_modified:
            self.project_modified = True
            self._update_window_title()
    
    def _update_window_title(self) -> None:
        """更新窗口标题"""
        if self.current_project:
            title = f"AetherLight Pro — {self.current_project.project_info.name}"
            if self.project_modified:
                title += " *"
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("AetherLight Pro — Lighting Control")
    
    def _confirm_discard_changes(self) -> bool:
        """确认是否放弃未保存的更改"""
        reply = QMessageBox.question(
            self,
            "未保存的更改",
            "当前项目有未保存的更改,是否继续?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        # 自动保存当前项目
        if self.current_project:
            try:
                self.current_project.fixtures = self.import_page.fixture_panel.fixtures
                self.current_project.groups = self.group_management_page.groups
                self.project_manager.save_project(self.current_project)
                logger.info("关闭前已自动保存项目")
            except Exception as e:
                logger.error(f"自动保存失败: {e}")
        
        event.accept()

    # ------------------------------------------------------------------
    # 认证与同步
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # 认证与同步 (已移除)
    # ------------------------------------------------------------------

    # def _show_login_dialog(self):
    #     ...

    # def _logout(self):
    #     ...

    # def _update_auth_status(self):
    #     ...

    # def _auto_sync(self):
    #     ...

    # def _manual_sync(self):
    #     ...
