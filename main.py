"""
AetherLight Pro — 应用入口

运行此文件启动 AetherLight Pro 灯光控制应用。
"""
import logging
import sys

from PyQt6.QtWidgets import QApplication
    
from aetherlight.gui.main_window import MainWindow


def setup_logging() -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("启动 AetherLight Pro v0.1.0")

    app = QApplication(sys.argv)
    app.setApplicationName("AetherLight Pro")
    app.setOrganizationName("AetherLight")

    # 高 DPI 支持
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    logger.info("AetherLight Pro 窗口已显示")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
