#!/usr/bin/env python3
"""
AI Data Center Tracker — USA  (Enterprise Edition)
Real-time map of active and planned AI data centers with Claude AI assistant.

Usage:
    python3 main.py
    ANTHROPIC_API_KEY=sk-ant-... python3 main.py
"""

import logging
import os
import sys
from pathlib import Path

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR  = Path.home() / ".local/share/ai-datacenter-tracker"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("main")

ICON_PATH = str(Path.home() / "Pictures/Icons/AIDataCenterTracker.png")


def _check_deps():
    missing = []
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6  →  sudo apt install python3-pyqt6")
    try:
        import PyQt6.QtWebEngineWidgets
    except ImportError:
        missing.append("PyQt6-WebEngine  →  sudo apt install python3-pyqt6.qtwebengine")
    try:
        import anthropic
    except ImportError:
        missing.append("anthropic  →  pip3 install anthropic --break-system-packages")
    if missing:
        print("ERROR: missing dependencies:\n  " + "\n  ".join(missing))
        sys.exit(1)


def main():
    _check_deps()

    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    # WebEngine MUST be imported before QApplication is instantiated
    from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401

    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS",
                          "--disable-gpu --no-sandbox --disable-dev-shm-usage")
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setApplicationName("AI Data Center Tracker")
    app.setApplicationDisplayName("AI Data Center Tracker — USA")
    app.setOrganizationName("AITracker")
    app.setQuitOnLastWindowClosed(False)   # keep alive in tray

    icon = QIcon(ICON_PATH)
    app.setWindowIcon(icon)

    # ── Main window ───────────────────────────────────────────────────────
    from app.main_window import MainWindow
    window = MainWindow(app_icon=icon)

    # ── System tray ───────────────────────────────────────────────────────
    tray = QSystemTrayIcon(icon, parent=app)
    tray.setToolTip("AI Data Center Tracker — USA")

    menu = QMenu()
    menu.setStyleSheet("""
        QMenu {
            background:#0a0e1a;
            border:1px solid rgba(100,200,255,0.25);
            color:#c0d8f0;
            font-family:monospace; font-size:11px;
            padding:4px;
        }
        QMenu::item            { padding:6px 20px; border-radius:4px; }
        QMenu::item:selected   { background:rgba(50,100,180,0.50); }
        QMenu::separator       { background:rgba(100,200,255,0.10);
                                  height:1px; margin:4px 8px; }
    """)
    act_show = menu.addAction("⬡  Show Tracker")
    act_show.triggered.connect(lambda: (window.showNormal(), window.activateWindow()))
    menu.addSeparator()
    act_quit = menu.addAction("✕  Quit")
    act_quit.triggered.connect(app.quit)

    tray.setContextMenu(menu)

    def _on_tray_activated(reason):
        if int(reason) == 2:    # QSystemTrayIcon.ActivationReason.DoubleClick == 2
            window.showNormal()
            window.activateWindow()
    tray.activated.connect(_on_tray_activated)
    tray.show()

    window.tray_icon = tray     # give window a reference for closeEvent
    window.show()

    log.info("Application started — PID %d", os.getpid())
    rc = app.exec()
    log.info("Application exited with code %d", rc)
    sys.exit(rc)


if __name__ == "__main__":
    main()
