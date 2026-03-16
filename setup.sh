#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# AI Data Center Tracker — Kubuntu Setup Script
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║    AI Data Center Tracker — Dependency Installer          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.10+ first."
    exit 1
fi
PYTHON=$(python3 --version)
echo "✓  Python: $PYTHON"

# 1. System packages
echo ""
echo "── Installing system packages (may require sudo password)…"
sudo apt-get update -qq
sudo apt-get install -y \
    python3-pyqt6 \
    python3-pyqt6.qtwebengine \
    python3-pip \
    libqt6webenginewidgets6 \
    2>/dev/null || true

# 2. Python packages
echo ""
echo "── Installing Python packages…"
pip3 install --break-system-packages --quiet anthropic requests 2>/dev/null || \
pip3 install anthropic requests

echo ""
echo "✓  All dependencies installed."
echo ""

# 3. API key check
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠  ANTHROPIC_API_KEY is not set."
    echo ""
    echo "   To enable the AI Chat sidebar, add to your ~/.bashrc:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
    echo "   Or run the app with:"
    echo "   ANTHROPIC_API_KEY='sk-ant-...' python3 main.py"
else
    echo "✓  ANTHROPIC_API_KEY is set."
fi

echo ""
echo "── Ready! Launch with:"
echo "   cd $(dirname "$0")"
echo "   python3 main.py"
echo ""
