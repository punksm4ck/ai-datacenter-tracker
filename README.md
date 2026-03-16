# ⬡ AI Data Center Tracker — USA

A fully-featured desktop GUI application for tracking active and planned AI data centers across the United States, with an integrated Claude AI chat assistant.

![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-32ff96)
![Platform: Kubuntu Linux](https://img.shields.io/badge/platform-Kubuntu%20Linux-0078d4)
![AI: Claude Sonnet 4.6](https://img.shields.io/badge/AI-Claude%20Sonnet%204.6-a064ff)

---

## Features

### 🗺 Interactive Map
- Dark-themed Leaflet map (CartoDB Dark Matter tiles)
- 60+ data centers plotted across the USA
- Color-coded by status: **Active** (green) · **Construction** (amber) · **Planned** (blue) · **Announced** (purple)
- Marker size proportional to MW capacity
- Rich popup cards with operator, capacity, investment, and timeline data

### 🎛 Filtering & Search
- Filter by **Status** (checkboxes with per-status colors)
- Filter by **Operator** (Microsoft, Google, Amazon, Meta, xAI, OpenAI/Stargate, CoreWeave, etc.)
- Filter by **State** (with map auto-zoom)
- Full-text **search** across names, operators, cities, states, and tags

### 🤖 AI Chat Sidebar (Claude claude-sonnet-4-20250514)
- Streaming responses via Anthropic API
- Pre-loaded with live dataset stats as context
- Quick-action suggestion buttons
- Retains conversation history per session
- Markdown-style rendering of responses

### 📊 Live Statistics Panel
- Real-time counts by status
- Total tracked capacity (MW)
- Total tracked investment ($B)
- Operator and state counts

---

## Installation (Kubuntu / Ubuntu)

### Quick Setup

```bash
cd ai_datacenter_tracker
chmod +x setup.sh
./setup.sh
```

### Manual Installation

```bash
# System packages
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine

# Python packages
pip install anthropic requests --break-system-packages
```

### Set API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

Add to `~/.bashrc` for persistence.

---

## Usage

```bash
ANTHROPIC_API_KEY='sk-ant-...' python3 main.py
```

Or if you've exported the key in `.bashrc`:

```bash
python3 main.py
```

---

## Tracked Operators

| Operator | Facilities | Notable Sites |
|---|---|---|
| Microsoft | 9 | WI mega-campus ($3.3B), OH, PA |
| Amazon / AWS | 7 | IN ($11B), us-east-1 VA, TN |
| Google | 8 | OR, IA, NV, TX |
| Meta | 7 | Colossus (TX), OR, NC |
| OpenAI / Stargate | 2 | TX ($100B), PA |
| xAI | 2 | Colossus Memphis (100k+ H100s) |
| CoreWeave | 3 | NJ, IL, TX |
| Oracle | 4 | TX, IL, WA |
| Apple | 4 | NC, OR, NV, IA |
| Equinix | 3 | VA, CA, NY |
| + more | ... | ... |

---

## Architecture

```
ai_datacenter_tracker/
├── main.py                  # Entry point
├── setup.sh                 # Kubuntu installer
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main_window.py       # PyQt6 main window + toolbar + layout
    ├── chat_sidebar.py      # Claude AI chat panel (streaming)
    ├── data_store.py        # 60+ datacenter dataset + stats
    └── map_widget.html      # Leaflet map (dark theme, custom markers)
```

---

## Data Sources

The embedded dataset is compiled from public sources including:
- Company press releases and investor filings
- Data Center Dynamics, The Register, Bloomberg
- State economic development announcements
- CBRE / JLL data center market reports

The app is designed to be extended — add new entries to `app/data_store.py` to track new facilities as they are announced.

---

## License

MIT — free for personal and commercial use.
