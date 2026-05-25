#!/usr/bin/env python3
"""AI Datacenter Tracker — entry point."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AI Datacenter Tracker")
    app.setOrganizationName("Punksm4ck")

    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
