"""
App Radar Agent - Slack Block Kit 报告生成
将应用数据转换为精美的 Slack 消息
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from app_radar.config.settings import settings


class SlackReporter:
    """Slack 报告生成器"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def format_number(self, num: int) -> str:
        """格式化数字为 K/M 后缀"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.0f}K"
        return str(num)

    def get_rating_emoji(self, rating: float) -> str:
        """根据评分获取 emoji"""
        if rating >= 4.8:
            return "🌟"
        elif rating >= 4.7:
            return "⭐️"
        elif rating >= 4.5:
            return "✨"
        else:
            return "⚡️"

    def get_engagement_level(self, reviews: int) -> str:
        """评估参与度等级"""
        if reviews >= 3_000_000:
            return "🔥 极高"
        elif reviews >= 1_000_000:
            return "🚀 高"
        elif reviews >= 100_000:
            return "📈 中"
        else:
            return "💡 成长期"

    def create_header_blocks(self) -> List[Dict]:
        """创建消息头部"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        return [
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
                        "text": f"🕐 更新时间: {timestamp} | 🤖 App Radar Agent v2.0"
                    }
                ]
            },
            {"type": "divider"}
        ]

    def create_kpi_blocks(self, apps: List[Dict]) -> List[Dict]:
        """创建 KPI 概览"""
        if not apps:
            return []

        # 计算统计数据
        valid_ratings = [app['rating'] for app in apps if app.get('rating')]
        total_reviews = sum(app.get('rating_count', 0) for app in apps)
        avg_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0

        # 找出最佳应用
        top_engagement = max(apps, key=lambda x: x.get('rating_count', 0))
        top_rating = max(apps, key=lambda x: x.get('rating', 0))

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 核心指标*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*平均评分*\n{avg_rating:.2f}/5.0"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*总评论数*\n{self.format_number(total_reviews)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*参与度冠军*\n{top_engagement['name']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*满意度最高*\n{top_rating['name']} ({top_rating.get('rating', 0):.1f}分)"
                    }
                ]
            },
            {"type": "divider"}
        ]

    def create_app_blocks(self, apps: List[Dict], limit: int = 10) -> List[Dict]:
        """创建应用列表卡片"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🏆 TOP {min(limit, len(apps))} 应用*"
                }
            }
        ]

        # 按评论数排序
        sorted_apps = sorted(apps, key=lambda x: x.get('rating_count', 0), reverse=True)

        for i, app in enumerate(sorted_apps[:limit], 1):
            rating = app.get('rating', 0)
            reviews = app.get('rating_count', 0)
            emoji = self.get_rating_emoji(rating)
            engagement = self.get_engagement_level(reviews)
            url = app.get('url', '')

            # 应用卡片
            app_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{i}. {emoji} {app['name']}*\n"
                        f"• 评分: `{rating:.2f}` | 评论: `{self.format_number(reviews)}`\n"
                        f"• 参与度: {engagement}\n"
                        f"• 公司: {app.get('developer', 'Unknown')}\n"
                        f"• 类别: {app.get('category', 'Unknown')}"
                    )
                }
            }

            # 添加按钮 - 优先使用商业分析文章 URL
            analysis_url = settings.analysis_url_mapping.get(app['name'])
            button_url = analysis_url if analysis_url else url

            if button_url:
                app_block["accessory"] = {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📰 商业分析" if analysis_url else "🔗 查看详情",
                        "emoji": True
                    },
                    "url": button_url
                    # 不使用 action_id - Incoming Webhooks 不支持交互
                }

            blocks.append(app_block)

        return blocks

    def create_insights_blocks(self, apps: List[Dict]) -> List[Dict]:
        """创建洞察分析"""
        # 简单的洞察逻辑
        insights = []

        # 高评分应用
        high_rated = [app for app in apps if app.get('rating', 0) >= 4.7]
        if high_rated:
            insights.append(
                f"• 🌟 **高评分趋势**: {len(high_rated)} 款应用评分超过 4.7，用户满意度整体优秀"
            )

        # 参与度分析
        high_engagement = [app for app in apps if app.get('rating_count', 0) > 1_000_000]
        if high_engagement:
            insights.append(
                f"• 🔥 **用户参与度**: {len(high_engagement)} 款应用评论数超过 100 万，社区活跃度高"
            )

        # 类别分析
        categories = {}
        for app in apps:
            cat = app.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        top_category = max(categories.items(), key=lambda x: x[1])
        insights.append(
            f"• 📊 **类别分布**: {top_category[0]} 类应用占比最高 ({top_category[1]} 款)"
        )

        # 开发者分析
        developers = {}
        for app in apps:
            dev = app.get('developer', 'Unknown')
            developers[dev] = developers.get(dev, 0) + 1

        multi_app_devs = [(d, c) for d, c in developers.items() if c > 1]
        if multi_app_devs:
            top_dev = max(multi_app_devs, key=lambda x: x[1])
            insights.append(
                f"• 🏢 **头部开发者**: {top_dev[0]} 有 {top_dev[1]} 款应用上榜"
            )

        return [
            {"type": "divider"},
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
                    "text": "\n".join(insights)
                }
            }
        ]

    def create_action_blocks(self) -> List[Dict]:
        """
        创建操作按钮 (已禁用)

        注意: Slack Incoming Webhooks 不支持交互式按钮 (action_id)
        如需交互功能，需要:
        1. 创建 Slack App 并启用 Socket Mode
        2. 或者使用 URL 按钮链接到 Web 仪表板

        当前已移除非功能性的交互按钮，避免用户困惑
        """
        # 返回空列表 - 暂时移除非功能性按钮
        # TODO: 部署 Web 仪表板后，可添加 URL 类型的按钮
        return []

    def create_footer_blocks(self) -> List[Dict]:
        """创建页脚"""
        return [
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📊 数据来源: iTunes Search API | 🤖 生成工具: App Radar Agent v2.0"
                    }
                ]
            }
        ]

    def create_message(self, apps: List[Dict], top_n: int = 10) -> Dict:
        """创建完整的 Slack 消息"""
        blocks = []

        # 添加各个部分
        blocks.extend(self.create_header_blocks())
        blocks.extend(self.create_kpi_blocks(apps))
        blocks.extend(self.create_app_blocks(apps, limit=top_n))
        blocks.extend(self.create_insights_blocks(apps))
        blocks.extend(self.create_action_blocks())
        blocks.extend(self.create_footer_blocks())

        return {
            "blocks": blocks,
            "text": f"App Radar 报告 - {datetime.now().strftime('%Y-%m-%d')}"
        }

    def send_report(self, apps: List[Dict], top_n: int = 10) -> bool:
        """发送报告到 Slack"""
        if not self.webhook_url:
            print("❌ Slack webhook URL not configured")
            return False

        message = self.create_message(apps, top_n)

        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            print(f"✅ Report sent to Slack successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send to Slack: {e}")
            return False

    def upload_chart(self, chart_path: Path, channel: str = None) -> Optional[str]:
        """
        上传图表到 Slack（需要 Slack App Token）
        这个功能需要额外的 Slack API 配置
        """
        # TODO: 实现图表上传功能
        # 需要使用 files.upload API 和 Bot Token
        pass
