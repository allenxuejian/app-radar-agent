"""
App Radar Agent - Configuration Management
使用 pydantic-settings 实现类型安全的配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    """应用配置 - 支持从环境变量和 .env 文件读取"""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # === 数据库配置 ===
    database_url: str = "sqlite:///./data/app_radar.db"

    # === Slack 配置 ===
    slack_webhook_url: Optional[str] = None

    # === API Keys ===
    anthropic_api_key: Optional[str] = None
    crunchbase_api_key: Optional[str] = None
    github_token: Optional[str] = None

    # === 数据源配置 ===
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour

    # === 目标应用列表 (新兴应用 - 1-2年内，DAU 50万-200万) ===
    target_apps: List[str] = [
        # 社交类新兴应用
        "Lemon8",           # TikTok 旗下图文社交 (2023)
        "BeReal",           # 真实社交 (2022 爆发)
        "Gas",              # 匿名夸赞社交 (2023)
        "Poparazzi",        # 反自拍社交 (2021)
        "Bluesky",          # 去中心化社交 (2023)

        # AI 类新兴应用
        "Poe",              # AI 聊天平台 (2023)
        "Character.AI",     # AI 角色对话 (2022)
        "Perplexity",       # AI 搜索引擎 (2022)

        # 生产力工具
        "Linear",           # 项目管理 (2020-2024 快速增长)
        "Raycast",          # 生产力启动器 (2020-2024 增长)
        "Notion Calendar",  # 日历工具 (2022 被 Notion 收购)
        "Superhuman",       # 高效邮件客户端 (2019-2023 增长)

        # 创作者经济
        "Beehiiv",          # Newsletter 平台 (2021)
        "Substack",         # 内容订阅平台 (仍在增长)

        # 其他新兴应用
        "CapCut",           # 视频编辑 (2020-2023 爆发)
        "Temu",             # 电商 (2022)
        "Threads",          # Meta 的 Twitter 竞品 (2023)
        "Artifact",         # AI 新闻阅读 (2023)
        "Farcaster",        # 去中心化社交协议 (2023)
        "Damus"             # Nostr 客户端 (2023)
    ]

    # === 应用分析文章 URL 映射 ===
    analysis_url_mapping: dict = {
        "Lemon8": "https://techcrunch.com/2023/02/22/tiktoks-new-app-lemon8-is-a-blend-of-instagram-and-pinterest/",
        "BeReal": "https://www.theverge.com/2022/8/22/23315675/bereal-authenticity-social-media-apps",
        "Poe": "https://techcrunch.com/2023/02/21/poe-quoras-ai-chatbot-app/",
        "Character.AI": "https://www.theverge.com/2023/3/23/23653571/character-ai-chatbot-mobile-app-launch",
        "Linear": "https://www.theverge.com/2023/1/31/23579373/linear-project-management-software-funding",
        "Raycast": "https://techcrunch.com/2022/12/08/raycast-raises-15m-series-a/",
        "Beehiiv": "https://techcrunch.com/2023/04/04/newsletter-platform-beehiiv-raises-33m/",
        "CapCut": "https://www.theverge.com/2023/3/9/23632632/capcut-video-editing-app-tiktok-bytedance",
        "Temu": "https://techcrunch.com/2023/02/01/temu-shopping-app-super-bowl/",
        "Threads": "https://www.theverge.com/2023/7/5/23784263/instagram-threads-app-launch-twitter-competitor",
        "Bluesky": "https://www.theverge.com/2023/4/20/23690490/bluesky-social-app-invite-twitter-jack-dorsey",
        "Perplexity": "https://techcrunch.com/2023/03/28/perplexity-ai-raises-25-7m/",
        "Notion Calendar": "https://techcrunch.com/2022/06/21/notion-acquires-calendar-app-cron/",
        "Substack": "https://techcrunch.com/2023/04/04/substack-notes-launch/",
        "Gas": "https://techcrunch.com/2023/01/24/discord-acquires-gas-app/",
        "Poparazzi": "https://techcrunch.com/2021/05/24/poparazzi-app/",
        "Superhuman": "https://techcrunch.com/2023/01/17/superhuman-ai-email/",
        "Artifact": "https://www.theverge.com/2023/1/31/23579552/instagram-co-founders-artifact-personalized-news-app-ai",
        "Farcaster": "https://www.theverge.com/2023/5/16/23726132/farcaster-decentralized-social-network",
        "Damus": "https://techcrunch.com/2023/02/01/twitter-alternative-nostr/"
    }

    # === 调度配置 ===
    schedule_interval_hours: int = 8

    # === 项目路径 ===
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    results_dir: Path = data_dir / "results"
    charts_dir: Path = data_dir / "charts"


# 全局配置实例
settings = Settings()


def ensure_directories():
    """确保必要的目录存在"""
    settings.data_dir.mkdir(exist_ok=True)
    settings.results_dir.mkdir(exist_ok=True)
    settings.charts_dir.mkdir(exist_ok=True)
