#!python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QTabWidget, QVBoxLayout, QWidget

from src.client.tabs.regular_task import RegularTask
from src.client.tabs.resources import ResourceTab

backend_url = "http://127.0.0.1:8000"


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource for dev and PyInstaller exe."""
    if hasattr(sys, "_MEIPASS"):
        # Running in PyInstaller bundle
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(__file__).parent / relative_path)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROK Automation v3.0")

        self.move_top_right(450, 400)
        self.setWindowIcon(icon)

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Tab 1: Regular Task Selector
        self.task_selector_tab = RegularTask(backend_url)
        self.tabs.addTab(self.task_selector_tab, "Task Selector")

        # Tab 2: Resource
        self.tab_resource = ResourceTab()
        self.tabs.addTab(self.tab_resource, "Resources")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def move_top_right(self, w=450, h=400):
        """Place window in the top-right corner with margin."""
        screen = self.screen().availableGeometry()
        x = screen.width() - w  # right edge minus width
        y = 50  # top margin
        self.setGeometry(x, y, w, h)


if __name__ == "__main__":
    print("Starting GUI...")
    app = QApplication(sys.argv)
    icon = QIcon(resource_path("assets/ico/seondeok.ico"))
    app.setWindowIcon(icon)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
