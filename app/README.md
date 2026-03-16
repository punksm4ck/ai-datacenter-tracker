# ⬡ AI Data Center Tracker — USA

A fully-featured desktop GUI application for tracking active and planned AI data
centers across the United States, with an integrated Claude AI assistant and live
session water-consumption meter.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green)
![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey)
![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen)

---

## Features

| Feature | Details |
|---|---|
| 🗺 Interactive dark map | 60+ US facilities, color-coded by status, size-scaled by MW |
| 🎛 Filter panel | Filter by status, operator, state; full-text search |
| 🤖 Claude AI sidebar | Streaming chat with `claude-sonnet-4-20250514`, dataset-aware |
| 💧 Water meter | Live session water/CO₂ consumption tracking (16 oz / 100 words) |
| 🖥 Desktop launcher | One-click KDE/GNOME `.desktop` file creator/remover |
| 📦 System tray | Minimizes to tray on close; double-click or menu to restore |
| 📋 Structured logging | Writes to `~/.local/share/ai-datacenter-tracker/app.log` |

---

## Tracked Operators (sample)

Microsoft · Amazon/AWS · Google · Meta · OpenAI/Stargate · xAI · CoreWeave ·
Oracle · Apple · Equinix · Switch · QTS · CyrusOne · Vantage · Crusoe · IBM · more

**60 facilities · 20 operators · 28 states · 17,930 MW+ tracked · $162B+ investment**

---

## Requirements

- Python 3.10+
- Kubuntu / Ubuntu 22.04+ (or any distro with Qt6 packages)
- An [Anthropic API key](https://console.anthropic.com) for the AI chat feature

---

## Installation

### 1. System packages

```bash
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine
```

### 2. Python packages

```bash
pip3 install anthropic --break-system-packages
```

### 3. API key

```bash
echo "export ANTHROPIC_API_KEY='sk-ant-...'" >> ~/.bashrc
source ~/.bashrc
```

> The app works without an API key — the map, filters, and all data are fully
> functional. The AI chat sidebar requires the key.

---

## Usage

```bash
git clone https://github.com/YOUR_USERNAME/ai-datacenter-tracker.git
cd ai-datacenter-tracker
python3 main.py
```

Or silently (suppresses Qt/Chromium diagnostic output):

```bash
python3 main.py 2>/dev/null
```

### App icon (optional)

Place a PNG at `~/Pictures/Icons/AIDataCenterTracker.png` to use a custom icon
in the window, taskbar, tray, and desktop launcher. The app runs fine without it.

---

## Project Structure

```
ai-datacenter-tracker/
├── main.py                   Entry point, tray setup, logging
├── requirements.txt          Python dependencies
├── setup.sh                  One-command dependency installer
├── .gitignore
├── LICENSE
└── app/
    ├── __init__.py
    ├── main_window.py        Main window, toolbar, layout, filters
    ├── chat_sidebar.py       Claude AI streaming chat panel
    ├── data_store.py         60+ datacenter dataset + stats
    ├── map_widget.html       Leaflet map (dark theme, custom markers)
    └── water_meter.py        Session water/CO₂ consumption tracker
```

---

## Data Sources

Compiled from public sources including company press releases, investor filings,
Data Center Dynamics, The Register, Bloomberg, CBRE/JLL market reports, and state
economic development announcements.

To add a new facility, append a `DataCenter(...)` entry to `app/data_store.py`.

---

## Water Consumption Metric

Based on published estimates: **100 AI-generated words ≈ 16 fl oz of water** for
data center cooling. The meter tracks your Claude chat session in real time,
displaying bottle count (16 oz), fluid ounces, CO₂ equivalent, and Olympic pool
fraction.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
