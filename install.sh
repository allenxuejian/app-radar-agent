#!/bin/bash

# App Radar Agent Installation Script
# This script installs the App Radar Agent for Claude Code

set -e

echo "🚀 Installing App Radar Agent for Claude Code..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Claude agents directory exists
CLAUDE_DIR="$HOME/.claude/agents"
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "${YELLOW}Creating Claude agents directory...${NC}"
    mkdir -p "$CLAUDE_DIR"
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "${GREEN}✓${NC} Found Python $PYTHON_VERSION"

# Check pip installation
if ! command -v pip3 &> /dev/null; then
    echo "${RED}Error: pip3 is not installed.${NC}"
    echo "Please install pip3 and try again."
    exit 1
fi

echo "${GREEN}✓${NC} Found pip3"

# Install the agent
echo ""
echo "📦 Installing agent files..."

# Copy main agent file
cp app-radar-agent.md "$CLAUDE_DIR/"
echo "${GREEN}✓${NC} Installed app-radar-agent.md"

# Create scripts directory
SCRIPTS_DIR="$CLAUDE_DIR/app-radar-agent-scripts"
mkdir -p "$SCRIPTS_DIR"

# Copy scripts
cp -r scripts/* "$SCRIPTS_DIR/"
cp config.yaml "$SCRIPTS_DIR/"
echo "${GREEN}✓${NC} Installed supporting scripts"

# Install Python dependencies
echo ""
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet
echo "${GREEN}✓${NC} Installed Python packages"

# Create data directory
DATA_DIR="$HOME/.claude/agents/app-radar-agent-data"
mkdir -p "$DATA_DIR/results"
echo "${GREEN}✓${NC} Created data directory"

# Update config to use the correct data directory
sed -i.bak "s|./data/results|$DATA_DIR/results|g" "$SCRIPTS_DIR/config.yaml"
rm "$SCRIPTS_DIR/config.yaml.bak" 2>/dev/null || true

echo ""
echo "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "📍 Installed to: $CLAUDE_DIR"
echo "📂 Scripts location: $SCRIPTS_DIR"
echo "💾 Data directory: $DATA_DIR"
echo ""
echo "🎉 You can now use the agent in Claude Code!"
echo ""
echo "Try asking Claude:"
echo "  • 'Show me metrics for Lemon8'"
echo "  • 'Generate an app research report'"
echo "  • 'Analyze CapCut's growth trends'"
echo ""
echo "To customize monitored apps, edit:"
echo "  $SCRIPTS_DIR/config.yaml"
echo ""
