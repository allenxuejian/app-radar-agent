#!/usr/bin/env python3
"""
App Radar Agent - Slack Reporter
Sends beautifully formatted app research reports to Slack
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = Path.home() / ".claude/agents/app-radar-agent-data"
WEBHOOK_FILE = CONFIG_DIR / ".slack_webhook"
DATA_FILE = CONFIG_DIR / "data/results/raw_data.json"

def load_webhook_url():
    """Load Slack Webhook URL from config file"""
    if not WEBHOOK_FILE.exists():
        print(f"❌ Webhook file not found: {WEBHOOK_FILE}")
        print("\n📝 Please create it by running:")
        print(f'   echo "YOUR_WEBHOOK_URL" > {WEBHOOK_FILE}')
        print(f'   chmod 600 {WEBHOOK_FILE}')
        sys.exit(1)

    with open(WEBHOOK_FILE, 'r') as f:
        url = f.read().strip()

    if not url or not url.startswith('https://hooks.slack.com'):
        print(f"❌ Invalid webhook URL in {WEBHOOK_FILE}")
        sys.exit(1)

    return url

def load_app_data():
    """Load app data from JSON file"""
    if not DATA_FILE.exists():
        print(f"❌ Data file not found: {DATA_FILE}")
        print("\n📝 Please run data fetch first:")
        print("   cd ~/.claude/agents/app-radar-agent-data")
        print("   python3 scripts/fetch_data.py")
        sys.exit(1)

    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def format_number(num):
    """Format number with K/M suffix"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.0f}K"
    return str(num)

def get_rating_emoji(rating):
    """Get emoji based on rating"""
    if rating >= 4.8:
        return "🌟"
    elif rating >= 4.7:
        return "⭐️"
    elif rating >= 4.5:
        return "✨"
    else:
        return "⚡️"

def get_engagement_level(reviews):
    """Determine engagement level based on reviews"""
    if reviews >= 3_000_000:
        return "🔥 极高"
    elif reviews >= 1_000_000:
        return "🚀 高"
    elif reviews >= 100_000:
        return "📈 中"
    else:
        return "💡 成长期"

def create_slack_message(data):
    """Create formatted Slack message using Block Kit"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Sort apps by review count
    sorted_apps = sorted(data, key=lambda x: x['store_data'].get('userRatingCount', 0), reverse=True)

    # Calculate statistics
    total_reviews = sum(app['store_data'].get('userRatingCount', 0) for app in data)
    avg_rating = sum(app['store_data'].get('averageUserRating', 0) for app in data) / len(data)

    # Build blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📱 App Radar 商业产品调研报告",
                "emoji": True
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕐 更新时间: {timestamp} | 📊 监测应用: {len(data)} 款 | 💬 总评论数: {format_number(total_reviews)}"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📈 核心指标*\n• 平均评分: *{avg_rating:.2f}/5.0*\n• 参与度冠军: *{sorted_apps[0]['app']}* ({format_number(sorted_apps[0]['store_data']['userRatingCount'])} 评论)\n• 满意度最高: *{max(data, key=lambda x: x['store_data']['averageUserRating'])['app']}* ({max(app['store_data']['averageUserRating'] for app in data):.2f} 分)"
            }
        },
        {
            "type": "divider"
        }
    ]

    # Add each app as a rich block
    for i, app in enumerate(sorted_apps, 1):
        store_data = app['store_data']
        app_name = app['app']
        rating = store_data.get('averageUserRating', 0)
        reviews = store_data.get('userRatingCount', 0)
        company = store_data.get('sellerName', 'Unknown')
        version = store_data.get('version', 'N/A')
        genres = ', '.join(store_data.get('genres', [])[:2])
        url = store_data.get('trackViewUrl', '')

        emoji = get_rating_emoji(rating)
        engagement = get_engagement_level(reviews)

        # Create app block
        app_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {emoji} {app_name}*\n"
                        f"• 评分: `{rating:.2f}` | 评论: `{format_number(reviews)}`\n"
                        f"• 参与度: {engagement}\n"
                        f"• 公司: {company}\n"
                        f"• 类别: {genres} | 版本: {version}"
            }
        }

        # Add button if URL exists
        if url:
            app_block["accessory"] = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "查看详情",
                    "emoji": True
                },
                "url": url,
                "action_id": f"view_{app_name.lower().replace(' ', '_')}"
            }

        blocks.append(app_block)

    # Add insights section
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💡 核心洞察*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "• 🎮 *游戏化教育*: Duolingo 展现 Streak 机制威力\n"
                        "• 🎨 *创作工具*: Canva/CapCut 平民化趋势明显\n"
                        "• 🛍️ *社交电商*: Temu 裂变增长模式值得研究\n"
                        "• 📝 *生产力*: Notion All-in-One 整合趋势\n"
                        "• 🤖 *AI 整合*: 所有头部应用都在加入 AI 功能"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎯 可执行策略*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "1. *Freemium 模式*: 免费核心功能 + Pro 订阅\n"
                        "2. *模板市场*: 降低门槛 + 社区生态\n"
                        "3. *Streak 打卡*: 连续使用奖励提升留存\n"
                        "4. *AI 辅助*: 智能推荐/自动优化"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📊 数据来源: iTunes Search API | 🤖 生成工具: App Radar Agent v1.0"
                }
            ]
        }
    ])

    return {
        "blocks": blocks,
        "text": f"App Radar 报告 - {timestamp}"  # Fallback text for notifications
    }

def send_to_slack(webhook_url, message):
    """Send message to Slack"""
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send to Slack: {e}")
        return False

def send_test_message(webhook_url):
    """Send a test message to verify webhook"""
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🧪 App Radar Agent 测试",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ Slack 集成配置成功！\n\n接下来你将每 8 小时收到自动生成的 App 调研报告。"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ],
        "text": "App Radar Agent 测试消息"
    }
    return send_to_slack(webhook_url, message)

def main():
    """Main function"""
    print("🚀 App Radar Agent - Slack Reporter")
    print("=" * 50)

    # Check if this is a test
    is_test = '--test' in sys.argv or '-t' in sys.argv

    # Load webhook URL
    print("📡 Loading Slack webhook URL...")
    webhook_url = load_webhook_url()
    print(f"✅ Webhook loaded: {webhook_url[:50]}...")

    if is_test:
        print("\n🧪 Sending test message...")
        if send_test_message(webhook_url):
            print("✅ Test message sent successfully!")
            print("📱 Check your Slack channel")
        else:
            print("❌ Failed to send test message")
            sys.exit(1)
        return

    # Load app data
    print("\n📊 Loading app data...")
    data = load_app_data()
    print(f"✅ Loaded data for {len(data)} apps")

    # Create message
    print("\n✍️  Creating formatted message...")
    message = create_slack_message(data)
    print(f"✅ Message created with {len(message['blocks'])} blocks")

    # Send to Slack
    print("\n📤 Sending to Slack...")
    if send_to_slack(webhook_url, message):
        print("✅ Report sent successfully!")
        print(f"📱 Check your Slack channel")

        # Log success
        log_file = Path("/tmp/app-radar-slack.log")
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - SUCCESS - Report sent\n")
    else:
        print("❌ Failed to send report")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("🎉 Done!")

if __name__ == "__main__":
    main()
