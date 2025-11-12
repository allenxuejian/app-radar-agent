#!/bin/bash
# App Radar Agent - Cron Setup Script
# Sets up automatic report sending every 8 hours

set -e

echo "🚀 App Radar Agent - Cron Setup"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
AGENT_DIR="$HOME/.claude/agents/app-radar-agent-data"
SCRIPT_PATH="$AGENT_DIR/scripts/send_to_slack.py"
FETCH_SCRIPT="$AGENT_DIR/scripts/fetch_data.py"
ANALYZE_SCRIPT="$AGENT_DIR/scripts/analyze.py"

# Check if scripts exist
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Script not found: $SCRIPT_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found send_to_slack.py"

# Check if webhook is configured
WEBHOOK_FILE="$AGENT_DIR/.slack_webhook"
if [ ! -f "$WEBHOOK_FILE" ]; then
    echo -e "${YELLOW}⚠️  Slack webhook not configured yet${NC}"
    echo ""
    echo "Please run the following commands first:"
    echo ""
    echo "  1. Get your Slack Webhook URL from: https://api.slack.com/apps"
    echo "  2. Save it by running:"
    echo "     echo 'YOUR_WEBHOOK_URL' > $WEBHOOK_FILE"
    echo "     chmod 600 $WEBHOOK_FILE"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Webhook configured"
echo ""

# Ask user for schedule preference
echo "📅 Choose your schedule:"
echo "  1) Every 8 hours (0:00, 8:00, 16:00)"
echo "  2) Twice daily (9:00, 21:00)"
echo "  3) Once daily (9:00)"
echo "  4) Custom schedule"
echo ""
read -p "Enter your choice (1-4): " schedule_choice

case $schedule_choice in
    1)
        CRON_SCHEDULE="0 */8 * * *"
        DESCRIPTION="every 8 hours (0:00, 8:00, 16:00)"
        ;;
    2)
        CRON_SCHEDULE="0 9,21 * * *"
        DESCRIPTION="twice daily (9:00 AM, 9:00 PM)"
        ;;
    3)
        CRON_SCHEDULE="0 9 * * *"
        DESCRIPTION="once daily (9:00 AM)"
        ;;
    4)
        echo ""
        echo "Enter cron schedule (e.g., '0 */8 * * *'):"
        read -p "> " CRON_SCHEDULE
        DESCRIPTION="custom schedule"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}📋 Will create the following cron jobs:${NC}"
echo ""
echo "  # Fetch data and send to Slack - $DESCRIPTION"
echo "  $CRON_SCHEDULE cd $AGENT_DIR && /usr/bin/python3 $FETCH_SCRIPT && /usr/bin/python3 $ANALYZE_SCRIPT && /usr/bin/python3 $SCRIPT_PATH >> /tmp/app-radar-slack.log 2>&1"
echo ""
read -p "Continue? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Get current crontab
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Remove old app-radar entries
sed -i.bak '/app-radar-agent/d' "$TEMP_CRON" 2>/dev/null || sed -i '' '/app-radar-agent/d' "$TEMP_CRON"

# Add new entry
echo "" >> "$TEMP_CRON"
echo "# App Radar Agent - Auto report sending" >> "$TEMP_CRON"
echo "$CRON_SCHEDULE cd $AGENT_DIR && /usr/bin/python3 $FETCH_SCRIPT > /dev/null 2>&1 && /usr/bin/python3 $ANALYZE_SCRIPT > /dev/null 2>&1 && /usr/bin/python3 $SCRIPT_PATH >> /tmp/app-radar-slack.log 2>&1" >> "$TEMP_CRON"

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON" "$TEMP_CRON.bak" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Cron job installed successfully!${NC}"
echo ""
echo "📋 Current crontab:"
echo "-------------------"
crontab -l | grep -A1 "App Radar"
echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "You will now receive reports $DESCRIPTION"
echo ""
echo "📝 Useful commands:"
echo "  • View cron jobs:    crontab -l"
echo "  • Remove cron job:   crontab -e  (then delete the App Radar line)"
echo "  • View logs:         tail -f /tmp/app-radar-slack.log"
echo "  • Manual trigger:    python3 $SCRIPT_PATH"
echo ""
