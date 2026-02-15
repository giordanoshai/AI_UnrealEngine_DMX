"""
测试 Effect 和 Cue List 编辑器页面

验证新页面能否正常启动和运行
"""
import sys
from PyQt6.QtWidgets import QApplication
from aetherlight.gui.main_window import MainWindow


def main():
    print("启动 AetherLight Pro - 测试 Effect 和 Cue List 编辑器")
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    print("主窗口已启动")
    print("可用页面:")
    print("  - 页面 0: 导入管理")
    print("  - 页面 1: 分组管理")
    print("  - 页面 2: Effect 编辑")
    print("  - 页面 3: Cue List 编辑")
    print("\n请在工具栏中点击相应按钮切换到 Effect 编辑或 Cue List 编辑页面")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
