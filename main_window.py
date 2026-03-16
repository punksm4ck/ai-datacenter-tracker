"""
Main Window — AI Data Center Tracker
"""

import json
import os
import stat
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QLabel, QPushButton,
    QComboBox, QCheckBox, QFrame, QLineEdit, QSpacerItem,
    QSizePolicy, QMessageBox, QGroupBox, QScrollArea
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSlot, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QAction, QKeySequence, QCloseEvent

from app.data_store import get_datacenters_as_json, get_stats, DATACENTERS
from app.chat_sidebar import AIChatSidebar

ICON_PATH = "/home/tsann/Pictures/Icons/AIDataCenterTracker.png"
DESKTOP_FILE = Path.home() / ".local/share/applications/ai-datacenter-tracker.desktop"

STYLE = """
QMainWindow {
    background: #080c16;
}
QSplitter::handle {
    background: rgba(100, 200, 255, 0.12);
    width: 3px;
}
QSplitter::handle:hover {
    background: rgba(100, 200, 255, 0.3);
}
QToolBar {
    background: rgba(10, 14, 28, 0.98);
    border-bottom: 1px solid rgba(100, 200, 255, 0.2);
    spacing: 8px;
    padding: 4px 8px;
}
QStatusBar {
    background: rgba(8, 12, 20, 0.98);
    border-top: 1px solid rgba(100, 200, 255, 0.12);
    color: #4a7090;
    font-family: monospace;
    font-size: 11px;
}
QLabel { color: #c0d8f0; font-family: monospace; }
QPushButton {
    background: rgba(20, 40, 80, 0.6);
    border: 1px solid rgba(100, 200, 255, 0.25);
    border-radius: 5px;
    color: #80c0e0;
    font-family: monospace;
    font-size: 11px;
    padding: 5px 14px;
}
QPushButton:hover { background: rgba(30, 60, 110, 0.8); border-color: rgba(100,200,255,0.5); }
QPushButton:pressed { background: rgba(50, 100, 160, 0.8); }
QComboBox {
    background: rgba(15, 25, 50, 0.7);
    border: 1px solid rgba(100, 200, 255, 0.2);
    border-radius: 5px;
    color: #90c8e8;
    font-family: monospace;
    font-size: 11px;
    padding: 4px 10px;
    min-width: 140px;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #0a1428;
    border: 1px solid rgba(100,200,255,0.3);
    color: #90c8e8;
    selection-background-color: rgba(50,100,180,0.6);
}
QLineEdit {
    background: rgba(15, 25, 50, 0.7);
    border: 1px solid rgba(100, 200, 255, 0.2);
    border-radius: 5px;
    color: #90c8e8;
    font-family: monospace;
    font-size: 11px;
    padding: 4px 10px;
}
QLineEdit:focus { border-color: rgba(100,200,255,0.5); }
QCheckBox { color: #80c0e0; font-family: monospace; font-size: 10px; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid rgba(100,200,255,0.3);
    border-radius: 3px;
    background: rgba(20,40,80,0.5);
}
QCheckBox::indicator:checked {
    background: rgba(100,200,255,0.6);
    border-color: #64c8ff;
}
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: rgba(10,20,40,0.4); width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: rgba(100,200,255,0.25); border-radius: 3px; }
"""


def _desktop_exists() -> bool:
    return DESKTOP_FILE.exists()


def _create_desktop_launcher():
    """Write a .desktop file for the current script location."""
    # Find main.py relative to this file: app/../main.py
    main_py = Path(__file__).parent.parent / "main.py"
    python  = __import__("sys").executable
    DESKTOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=AI Data Center Tracker
GenericName=AI Infrastructure Map
Comment=Real-time USA AI Data Center tracker with Claude AI assistant
Exec={python} {main_py}
Icon={ICON_PATH}
Terminal=false
Categories=Science;Network;Education;
Keywords=AI;DataCenter;Infrastructure;Claude;Map;
StartupNotify=true
StartupWMClass=AI Data Center Tracker
"""
    DESKTOP_FILE.write_text(content)
    DESKTOP_FILE.chmod(DESKTOP_FILE.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    # Notify KDE/GNOME shell
    os.system("update-desktop-database ~/.local/share/applications/ 2>/dev/null &")


def _remove_desktop_launcher():
    if DESKTOP_FILE.exists():
        DESKTOP_FILE.unlink()
    os.system("update-desktop-database ~/.local/share/applications/ 2>/dev/null &")


class FilterPanel(QFrame):
    """Left-side filter / statistics panel."""
    filter_changed = None  # will be set by MainWindow

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QFrame {
                background: rgba(8, 12, 22, 0.98);
                border-right: 1px solid rgba(100, 200, 255, 0.12);
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        title = QLabel("⬡  FILTERS")
        title.setFont(QFont("Monospace", 10))
        title.setStyleSheet("color: #64c8ff; letter-spacing: 3px; font-weight: bold;")
        layout.addWidget(title)

        # ── Status ────────────────────────────────────────────────────────
        grp_status = self._section("STATUS")
        s_layout = QVBoxLayout(grp_status)
        s_layout.setContentsMargins(6, 8, 6, 8)
        s_layout.setSpacing(6)
        self.status_checks = {}
        for key, color, label in [
            ("active",       "#32ff96", "Active"),
            ("construction", "#ffb400", "Under Construction"),
            ("planned",      "#64b4ff", "Planned"),
            ("announced",    "#c864ff", "Announced"),
        ]:
            cb = QCheckBox(label)
            cb.setChecked(True)
            cb.setStyleSheet(f"""
                QCheckBox {{ color: {color}; }}
                QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}
            """)
            cb.stateChanged.connect(self._on_filter_change)
            s_layout.addWidget(cb)
            self.status_checks[key] = cb
        layout.addWidget(grp_status)

        # ── Operator ──────────────────────────────────────────────────────
        grp_op = self._section("OPERATOR")
        op_layout = QVBoxLayout(grp_op)
        op_layout.setContentsMargins(6, 8, 6, 8)
        self.operator_combo = QComboBox()
        operators = sorted(set(dc.operator for dc in DATACENTERS))
        self.operator_combo.addItem("All Operators")
        for op in operators:
            self.operator_combo.addItem(op)
        self.operator_combo.currentTextChanged.connect(self._on_operator_change)
        op_layout.addWidget(self.operator_combo)
        layout.addWidget(grp_op)

        # ── State ─────────────────────────────────────────────────────────
        grp_state = self._section("STATE")
        state_layout = QVBoxLayout(grp_state)
        state_layout.setContentsMargins(6, 8, 6, 8)
        self.state_combo = QComboBox()
        states = sorted(set(dc.state for dc in DATACENTERS))
        self.state_combo.addItem("All States")
        for st in states:
            self.state_combo.addItem(st)
        self.state_combo.currentTextChanged.connect(self._on_state_change)
        state_layout.addWidget(self.state_combo)
        layout.addWidget(grp_state)

        # ── Stats ─────────────────────────────────────────────────────────
        grp_stats = self._section("LIVE STATS")
        stats_layout = QVBoxLayout(grp_stats)
        stats_layout.setContentsMargins(6, 8, 6, 8)
        stats_layout.setSpacing(8)
        stats = get_stats()
        self._stat_labels = {}
        for key, label, value in [
            ("total",        "Total Facilities",   str(stats["total"])),
            ("active",       "Active",             str(stats["active"])),
            ("construction", "Construction",        str(stats["construction"])),
            ("planned",      "Planned",            str(stats["planned"])),
            ("total_mw",     "Total Capacity",     f"{stats['total_mw']:,} MW"),
            ("total_inv",    "Tracked Investment", f"${stats['total_investment_bn']}B+"),
            ("operators",    "Operators",          str(stats["operators"])),
            ("states",       "States",             str(stats["states"])),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(QFont("Monospace", 8))
            lbl.setStyleSheet("color: #4a7090;")
            val = QLabel(value)
            val.setFont(QFont("Monospace", 9))
            val.setStyleSheet("color: #64c8ff; font-weight: bold;")
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(lbl)
            row.addWidget(val)
            stats_layout.addLayout(row)
            self._stat_labels[key] = val
        layout.addWidget(grp_stats)
        layout.addStretch()

        reset_btn = QPushButton("↺  Reset Filters")
        reset_btn.clicked.connect(self._reset_filters)
        layout.addWidget(reset_btn)

    def _section(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(20, 30, 60, 0.4);
                border: 1px solid rgba(100, 200, 255, 0.1);
                border-radius: 6px;
            }
        """)
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)
        hdr = QLabel(title)
        hdr.setFont(QFont("Monospace", 8))
        hdr.setStyleSheet("""
            color: #3a6080;
            background: rgba(30, 60, 100, 0.3);
            padding: 4px 8px;
            letter-spacing: 2px;
            border-radius: 5px 5px 0 0;
        """)
        inner.addWidget(hdr)
        return frame

    def _on_filter_change(self):
        if self.filter_changed:
            active = [k for k, cb in self.status_checks.items() if cb.isChecked()]
            self.filter_changed("status", active)

    def _on_operator_change(self, text):
        if self.filter_changed:
            self.filter_changed("operator", "" if text == "All Operators" else text)

    def _on_state_change(self, text):
        if self.filter_changed:
            self.filter_changed("state", "" if text == "All States" else text)

    def _reset_filters(self):
        for cb in self.status_checks.values():
            cb.setChecked(True)
        self.operator_combo.setCurrentIndex(0)
        self.state_combo.setCurrentIndex(0)


class MainWindow(QMainWindow):
    def __init__(self, app_icon: QIcon = None):
        super().__init__()
        self._app_icon = app_icon or QIcon(ICON_PATH)
        self.tray_icon = None   # set by main.py after construction
        self.setWindowTitle("⬡  AI Data Center Tracker — USA")
        self.setWindowIcon(self._app_icon)
        self.resize(1600, 900)
        self.setMinimumSize(1100, 650)
        self.setStyleSheet(STYLE)
        self._map_loaded = False
        self._setup_toolbar()
        self._setup_central()
        self._setup_statusbar()

    # ── Close → minimise to tray ──────────────────────────────────────────
    def closeEvent(self, event: QCloseEvent):
        if self.tray_icon and self.tray_icon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "AI Data Center Tracker",
                "Minimised to tray — double-click to restore.",
                QIcon(ICON_PATH),
                2500,
            )
        else:
            event.accept()

    # ── Toolbar ───────────────────────────────────────────────────────────
    def _setup_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        title = QLabel("  ⬡  AI DATA CENTER TRACKER — USA  ")
        title.setFont(QFont("Monospace", 12))
        title.setStyleSheet("color: #64c8ff; font-weight: bold; letter-spacing: 2px;")
        tb.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background: rgba(100,200,255,0.15); margin: 6px 4px;")
        tb.addWidget(sep)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search facilities…")
        self.search_box.setFixedWidth(220)
        self.search_box.textChanged.connect(self._on_search)
        tb.addWidget(self.search_box)

        tb.addSeparator()

        refresh_btn = QPushButton("↻  Refresh Data")
        refresh_btn.setToolTip("Reload data from the embedded dataset")
        refresh_btn.clicked.connect(self._reload_data)
        tb.addWidget(refresh_btn)

        reset_view_btn = QPushButton("🗺  Reset View")
        reset_view_btn.clicked.connect(self._reset_view)
        tb.addWidget(reset_view_btn)

        tb.addSeparator()

        # ── Desktop launcher button ───────────────────────────────────────
        self.launcher_btn = QPushButton()
        self.launcher_btn.setFont(QFont("Monospace", 10))
        self.launcher_btn.clicked.connect(self._toggle_desktop_launcher)
        self._refresh_launcher_btn()
        tb.addWidget(self.launcher_btn)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self.ts_label = QLabel()
        self.ts_label.setFont(QFont("Monospace", 9))
        self.ts_label.setStyleSheet("color: #304050;")
        tb.addWidget(self.ts_label)
        self._update_timestamp()

        # Toggle chat — starts UNCHECKED (hidden)
        self.toggle_chat_btn = QPushButton("◧  AI Chat")
        self.toggle_chat_btn.setCheckable(True)
        self.toggle_chat_btn.setChecked(False)
        self.toggle_chat_btn.toggled.connect(self._toggle_chat)
        self.toggle_chat_btn.setStyleSheet("""
            QPushButton:checked {
                background: rgba(100,50,200,0.5);
                border-color: rgba(160,100,255,0.5);
                color: #c090ff;
            }
        """)
        tb.addWidget(self.toggle_chat_btn)

    # ── Desktop launcher helpers ──────────────────────────────────────────
    def _refresh_launcher_btn(self):
        if _desktop_exists():
            self.launcher_btn.setText("🗑  Remove Desktop Launcher")
            self.launcher_btn.setToolTip(f"Remove {DESKTOP_FILE}")
            self.launcher_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(80, 20, 20, 0.55);
                    border: 1px solid rgba(255, 80, 80, 0.35);
                    border-radius: 5px;
                    color: #ff7070;
                    font-family: monospace;
                    font-size: 11px;
                    padding: 5px 14px;
                }
                QPushButton:hover { background: rgba(110,30,30,0.8); border-color: rgba(255,100,100,0.6); }
            """)
        else:
            self.launcher_btn.setText("🖥  Create Desktop Launcher")
            self.launcher_btn.setToolTip("Add this app to your KDE/GNOME application menu")
            self.launcher_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(20, 70, 30, 0.55);
                    border: 1px solid rgba(50, 200, 80, 0.35);
                    border-radius: 5px;
                    color: #50e878;
                    font-family: monospace;
                    font-size: 11px;
                    padding: 5px 14px;
                }
                QPushButton:hover { background: rgba(30,100,40,0.8); border-color: rgba(80,220,100,0.6); }
            """)

    def _toggle_desktop_launcher(self):
        if _desktop_exists():
            _remove_desktop_launcher()
            self._update_status("Desktop launcher removed")
        else:
            _create_desktop_launcher()
            self._update_status(f"Desktop launcher created → {DESKTOP_FILE}")
        self._refresh_launcher_btn()

    # ── Central widget ────────────────────────────────────────────────────
    def _setup_central(self):
        central = QWidget()
        central.setStyleSheet("background: #080c16;")
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.filter_panel = FilterPanel()
        self.filter_panel.filter_changed = self._on_filter_changed
        main_layout.addWidget(self.filter_panel)

        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.setStyleSheet("QSplitter::handle { background: rgba(100,200,255,0.1); }")

        self.web_view = QWebEngineView()
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        map_html = Path(__file__).parent / "map_widget.html"
        self.web_view.loadFinished.connect(self._on_map_loaded)
        self.web_view.setUrl(QUrl.fromLocalFile(str(map_html.resolve())))
        self.h_splitter.addWidget(self.web_view)

        self.chat_sidebar = AIChatSidebar()
        self.chat_sidebar.setVisible(False)   # hidden at startup
        self.h_splitter.addWidget(self.chat_sidebar)

        self.h_splitter.setSizes([1600, 0])
        self.h_splitter.setCollapsible(0, False)

        main_layout.addWidget(self.h_splitter)

    # ── Status bar ────────────────────────────────────────────────────────
    def _setup_statusbar(self):
        sb = self.statusBar()
        stats = get_stats()
        self.sb_total        = QLabel(f"  {stats['total']} facilities")
        self.sb_active       = QLabel(f"  ● {stats['active']} active")
        self.sb_construction = QLabel(f"  ◐ {stats['construction']} construction")
        self.sb_planned      = QLabel(f"  ○ {stats['planned']} planned")
        self.sb_mw           = QLabel(f"  ⚡ {stats['total_mw']:,} MW tracked")
        self.sb_active.setStyleSheet("color: #32ff96;")
        self.sb_construction.setStyleSheet("color: #ffb400;")
        self.sb_planned.setStyleSheet("color: #64b4ff;")
        self.sb_mw.setStyleSheet("color: #4a7090;")
        for w in [self.sb_total, self.sb_active, self.sb_construction, self.sb_planned, self.sb_mw]:
            sb.addWidget(w)
        sb.addPermanentWidget(QLabel("  Data: embedded dataset + public sources  "))

    # ── Map callbacks ─────────────────────────────────────────────────────
    def _on_map_loaded(self, ok):
        if ok:
            self._map_loaded = True
            self._push_data_to_map()
            self._update_status("Map loaded — data injected")

    def _push_data_to_map(self):
        if not self._map_loaded:
            return
        js_data = get_datacenters_as_json().replace("\\", "\\\\").replace("`", "\\`")
        self.web_view.page().runJavaScript(f"loadDatacenters({js_data});")

    def _reload_data(self):
        self._push_data_to_map()
        self._update_timestamp()
        self._update_status("Data refreshed")

    def _reset_view(self):
        self.web_view.page().runJavaScript("map.flyTo([38.5, -96.0], 4, {animate:true, duration:1.2});")

    # ── Search ────────────────────────────────────────────────────────────
    def _on_search(self, text: str):
        if not self._map_loaded:
            return
        text = text.strip().lower()
        if not text:
            self._on_filter_changed("operator", "")
            return
        matches = [
            dc for dc in DATACENTERS
            if text in dc.name.lower()
            or text in dc.operator.lower()
            or text in dc.city.lower()
            or text in dc.state.lower()
            or any(text in t for t in dc.tags)
        ]
        if len(matches) == 1:
            self.web_view.page().runJavaScript(f"highlightMarker('{matches[0].id}');")
        elif len(matches) > 1:
            ids = json.dumps([m.id for m in matches])
            self.web_view.page().runJavaScript(f"""
            allMarkers.forEach(function(m) {{
                var ids = {ids};
                var grp = layerGroups[m.dc.status];
                if (ids.indexOf(m.dc.id) !== -1) {{
                    if (!grp.hasLayer(m)) grp.addLayer(m);
                }} else {{ grp.removeLayer(m); }}
            }});
            """)
        self._update_status(f"Search: '{text}' — {len(matches)} results")

    # ── Filters ───────────────────────────────────────────────────────────
    def _on_filter_changed(self, filter_type: str, value):
        if not self._map_loaded:
            return
        if filter_type == "status":
            self.web_view.page().runJavaScript(f"filterByStatus({json.dumps(value)});")
        elif filter_type == "operator":
            op = value.replace("'", "\\'")
            self.web_view.page().runJavaScript(f"filterByOperator('{op}');")
        elif filter_type == "state":
            if value:
                self.web_view.page().runJavaScript(f"zoomToState('{value.replace(chr(39), chr(92)+chr(39))}');")
            else:
                self._reset_view()

    # ── Chat toggle ───────────────────────────────────────────────────────
    def _toggle_chat(self, visible: bool):
        self.chat_sidebar.setVisible(visible)
        if visible:
            self.h_splitter.setSizes([1200, 380])
        else:
            self.h_splitter.setSizes([1600, 0])

    # ── Helpers ───────────────────────────────────────────────────────────
    def _update_timestamp(self):
        self.ts_label.setText(f"Updated: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}  ")
        QTimer.singleShot(60000, self._update_timestamp)

    def _update_status(self, msg: str):
        self.statusBar().showMessage(f"  {msg}", 4000)
