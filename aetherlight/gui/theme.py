"""
AetherLight Pro - 暗色主题

专业灯光控制应用的视觉主题系统。
深灰背景 + 蓝色强调色 + 自定义控件样式。
"""


def get_dark_stylesheet() -> str:
    """返回完整的暗色主题 QSS 样式表"""
    return """
    /* ================================================================
       AetherLight Pro — Dark Theme
       ================================================================ */

    /* --- 全局基础 --- */
    QWidget {
        background-color: #1a1a2e;
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 13px;
    }

    /* --- 主窗口 --- */
    QMainWindow {
        background-color: #0f0f23;
    }

    QMainWindow::separator {
        background-color: #16213e;
        width: 2px;
        height: 2px;
    }

    /* --- 菜单栏 & 工具栏 --- */
    QMenuBar {
        background-color: #0f0f23;
        border-bottom: 1px solid #16213e;
        padding: 2px;
    }

    QMenuBar::item {
        padding: 6px 12px;
        border-radius: 4px;
    }

    QMenuBar::item:selected {
        background-color: #16213e;
    }

    QMenu {
        background-color: #1a1a2e;
        border: 1px solid #16213e;
        border-radius: 6px;
        padding: 4px;
    }

    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
    }

    QMenu::item:selected {
        background-color: #0f3460;
    }

    QToolBar {
        background-color: #0f0f23;
        border-bottom: 1px solid #16213e;
        padding: 4px 8px;
        spacing: 6px;
    }

    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 6px 14px;
        color: #b0b0d0;
        font-weight: 500;
    }

    QToolButton:hover {
        background-color: #16213e;
        border-color: #0f3460;
        color: #e0e0e0;
    }

    QToolButton:pressed {
        background-color: #0f3460;
    }

    /* --- 状态栏 --- */
    QStatusBar {
        background-color: #0f0f23;
        border-top: 1px solid #16213e;
        color: #8888aa;
        font-size: 12px;
    }

    /* --- 分组框 --- */
    QGroupBox {
        background-color: #16213e;
        border: 1px solid #1a1a4e;
        border-radius: 8px;
        margin-top: 16px;
        padding-top: 24px;
        font-weight: bold;
        color: #53a8f9;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
    }

    /* --- 标签 --- */
    QLabel {
        color: #c0c0d0;
        background-color: transparent;
    }

    QLabel#sectionTitle {
        color: #53a8f9;
        font-size: 15px;
        font-weight: bold;
    }

    QLabel#statusLabel {
        font-size: 12px;
        color: #8888aa;
    }

    /* --- 按钮 --- */
    QPushButton {
        background-color: #0f3460;
        color: #e0e0e0;
        border: 1px solid #1a4a8a;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: 500;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #1a4a8a;
        border-color: #53a8f9;
    }

    QPushButton:pressed {
        background-color: #53a8f9;
        color: #0f0f23;
    }

    QPushButton:disabled {
        background-color: #1a1a2e;
        color: #555577;
        border-color: #1a1a2e;
    }

    QPushButton#accentButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #e94560, stop:1 #ff6b6b);
        color: white;
        border: none;
        font-weight: bold;
    }

    QPushButton#accentButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff6b6b, stop:1 #e94560);
    }

    QPushButton#successButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #00b894, stop:1 #00cec9);
        color: white;
        border: none;
        font-weight: bold;
    }

    /* --- 表格 --- */
    QTableWidget, QTableView {
        background-color: #16213e;
        alternate-background-color: #1a1a3e;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
        gridline-color: #1a1a4e;
        selection-background-color: #0f3460;
        selection-color: #ffffff;
    }

    QHeaderView::section {
        background-color: #0f0f23;
        color: #53a8f9;
        border: none;
        border-bottom: 2px solid #0f3460;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 12px;
    }

    QTableWidget::item {
        padding: 6px 10px;
        border-bottom: 1px solid #1a1a3e;
    }

    /* --- 树形视图 --- */
    QTreeWidget, QTreeView {
        background-color: #16213e;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
        alternate-background-color: #1a1a3e;
        selection-background-color: #0f3460;
    }

    QTreeWidget::item {
        padding: 4px 8px;
        border-radius: 3px;
    }

    QTreeWidget::item:hover {
        background-color: #1a1a4e;
    }

    QTreeWidget::item:selected {
        background-color: #0f3460;
        color: #ffffff;
    }

    /* --- 列表视图 --- */
    QListWidget, QListView {
        background-color: #16213e;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
        selection-background-color: #0f3460;
    }

    QListWidget::item {
        padding: 8px 12px;
        border-bottom: 1px solid #1a1a3e;
    }

    QListWidget::item:hover {
        background-color: #1a1a4e;
    }

    /* --- 输入框 --- */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #0f0f23;
        color: #e0e0e0;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: #0f3460;
    }

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #53a8f9;
    }

    /* --- 下拉框 --- */
    QComboBox {
        background-color: #16213e;
        color: #e0e0e0;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 100px;
    }

    QComboBox:hover {
        border-color: #0f3460;
    }

    QComboBox::drop-down {
        border: none;
        width: 24px;
    }

    QComboBox QAbstractItemView {
        background-color: #1a1a2e;
        border: 1px solid #1a1a4e;
        selection-background-color: #0f3460;
    }

    /* --- 滚动条 --- */
    QScrollBar:vertical {
        background-color: #0f0f23;
        width: 10px;
        border-radius: 5px;
        margin: 0;
    }

    QScrollBar::handle:vertical {
        background-color: #1a1a4e;
        border-radius: 5px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #0f3460;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }

    QScrollBar:horizontal {
        background-color: #0f0f23;
        height: 10px;
        border-radius: 5px;
        margin: 0;
    }

    QScrollBar::handle:horizontal {
        background-color: #1a1a4e;
        border-radius: 5px;
        min-width: 30px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #0f3460;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }

    /* --- 对话框 --- */
    QDialog {
        background-color: #1a1a2e;
    }

    /* --- 分割器 --- */
    QSplitter::handle {
        background-color: #16213e;
    }

    QSplitter::handle:horizontal {
        width: 3px;
    }

    QSplitter::handle:vertical {
        height: 3px;
    }

    /* --- 拖放区域 --- */
    QFrame#dropZone {
        background-color: #16213e;
        border: 2px dashed #1a1a4e;
        border-radius: 12px;
    }

    QFrame#dropZone:hover {
        border-color: #53a8f9;
        background-color: #1a1a3e;
    }

    /* --- 自定义标签 --- */
    QLabel#patchedBadge {
        background-color: #00b894;
        color: white;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
    }

    QLabel#unpatchedBadge {
        background-color: #e94560;
        color: white;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
    }

    /* --- Tab 标签页 --- */
    QTabWidget::pane {
        background-color: #16213e;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
    }

    QTabBar::tab {
        background-color: #0f0f23;
        color: #8888aa;
        border: 1px solid #1a1a4e;
        border-bottom: none;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }

    QTabBar::tab:selected {
        background-color: #16213e;
        color: #53a8f9;
        border-color: #0f3460;
    }

    QTabBar::tab:hover:!selected {
        background-color: #1a1a2e;
        color: #c0c0d0;
    }

    /* --- 进度条 --- */
    QProgressBar {
        background-color: #0f0f23;
        border: 1px solid #1a1a4e;
        border-radius: 6px;
        text-align: center;
        color: #e0e0e0;
        height: 20px;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #0f3460, stop:1 #53a8f9);
        border-radius: 5px;
    }
    """
