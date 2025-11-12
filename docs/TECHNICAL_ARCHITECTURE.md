# App Radar Agent - 技术架构方案 v2.0

> 从单源基础监控升级到多维度商业智能分析系统

## 📋 目录

- [1. 整体架构](#1-整体架构)
- [2. 数据源设计](#2-数据源设计)
- [3. 指标体系](#3-指标体系)
- [4. 模块化设计](#4-模块化设计)
- [5. 存储方案](#5-存储方案)
- [6. 展示层设计](#6-展示层设计)
- [7. 调度与监控](#7-调度与监控)
- [8. 实施路线图](#8-实施路线图)

---

## 1. 整体架构

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Collection Layer                   │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ iTunes   │ Google   │ AppAnnie │Crunchbase│  Web Scraping   │
│   API    │ Play API │   API    │   API    │  (Reviews/RSS)  │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
           │              │              │              │
           └──────────────┴──────────────┴──────────────┘
                              ▼
           ┌─────────────────────────────────────────┐
           │       Data Pipeline & Processing        │
           ├─────────────────────────────────────────┤
           │ • Rate Limiting & Retry                │
           │ • Data Validation & Cleaning           │
           │ • Entity Resolution & Deduplication    │
           │ • Cache Management                      │
           └─────────────────────────────────────────┘
                              ▼
           ┌─────────────────────────────────────────┐
           │         Storage Layer (SQLite)          │
           ├─────────────────────────────────────────┤
           │ apps | metrics | rankings | insights    │
           └─────────────────────────────────────────┘
                              ▼
           ┌─────────────────────────────────────────┐
           │         Analytics Engine                │
           ├─────────────────────────────────────────┤
           │ • Trend Analysis (7d/30d growth)       │
           │ • Competitive Positioning              │
           │ • Moat & Barrier Detection (LLM)       │
           │ • Strategic Pattern Recognition        │
           └─────────────────────────────────────────┘
                              ▼
           ┌─────────────────────────────────────────┐
           │         Reporting & Output              │
           ├─────────────────────────────────────────┤
           │ Slack | Email | Markdown | JSON | API   │
           └─────────────────────────────────────────┘
```

### 1.2 技术栈选型

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| **数据采集** | `httpx` + `asyncio` | 异步并发,提升采集速度 |
| **数据解析** | `pydantic` | 类型安全的数据验证 |
| **存储** | `SQLite` + `sqlalchemy` | 轻量级,无需部署,支持复杂查询 |
| **调度** | `apscheduler` | Python 原生,支持 cron/interval |
| **LLM 洞察** | `anthropic SDK` / `openai` | 战略分析、护城河识别 |
| **可视化** | `matplotlib` / `plotly` | 生成趋势图表 |
| **配置管理** | `pydantic-settings` + `.env` | 类型安全的环境变量 |
| **日志** | `loguru` | 更优雅的日志输出 |
| **测试** | `pytest` + `pytest-mock` | Mock 外部 API |

---

## 2. 数据源设计

### 2.1 多数据源策略

#### 2.1.1 核心数据源(免费/低成本)

| 数据源 | 获取内容 | API/方法 | 成本 | 限制 |
|--------|----------|----------|------|------|
| **iTunes Search API** | 评分、评论数、开发者、类别 | 官方 API | 免费 | 20 req/s |
| **Google Play Unofficial API** | Android 应用基础数据 | `google-play-scraper` | 免费 | 需控制频率 |
| **App Store Reviews** | 用户评论、情感分析 | `app-store-scraper` | 免费 | IP 限制 |
| **GitHub** | 开源应用团队规模/活跃度 | GitHub API | 免费 | 5000 req/h |
| **Product Hunt** | 新产品发布、社区反馈 | 官方 API | 免费 | 需 token |
| **RSS/Changelog** | 版本更新节奏 | `feedparser` | 免费 | - |

#### 2.1.2 高级数据源(付费/有限免费)

| 数据源 | 获取内容 | 备注 |
|--------|----------|------|
| **Crunchbase** | 融资、员工规模 | 有限免费 tier |
| **LinkedIn** | 公司团队规模、岗位分布 | 需爬虫或付费 API |
| **SimilarWeb** | 网站流量估算 | 付费 |
| **SensorTower / AppAnnie** | 下载量估算、收入数据 | 付费,价格昂贵 |

**推荐策略:**
- **Phase 1**: 只使用免费数据源
- **Phase 2**: 集成 Crunchbase 免费 tier
- **Phase 3**: 根据 ROI 决定是否购买付费数据

### 2.2 数据源抽象层设计

```python
# app_radar/data_sources/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class DataSourceResult(BaseModel):
    """统一的数据源返回格式"""
    source: str
    app_id: str
    timestamp: str
    data: Dict[str, Any]
    metadata: Optional[Dict] = None

class BaseDataSource(ABC):
    """数据源基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.cache = CacheManager(ttl=config.get('cache_ttl', 3600))

    @abstractmethod
    async def fetch(self, app_identifier: str) -> DataSourceResult:
        """获取数据的抽象方法"""
        pass

    async def fetch_with_retry(self, app_identifier: str, max_retries: int = 3):
        """带重试的获取逻辑"""
        for attempt in range(max_retries):
            try:
                # 先检查缓存
                cached = await self.cache.get(app_identifier)
                if cached:
                    return cached

                # 调用具体实现
                result = await self.fetch(app_identifier)

                # 写入缓存
                await self.cache.set(app_identifier, result)
                return result

            except RateLimitError:
                await asyncio.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                logger.error(f"Fetch failed: {e}")
                if attempt == max_retries - 1:
                    raise
```

### 2.3 具体实现示例

```python
# app_radar/data_sources/itunes.py
class ITunesDataSource(BaseDataSource):

    async def fetch(self, app_name: str) -> DataSourceResult:
        url = f"https://itunes.apple.com/search?term={app_name}&entity=software"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data.get('results'):
                raise AppNotFoundError(f"App not found: {app_name}")

            app = data['results'][0]

            return DataSourceResult(
                source="itunes",
                app_id=app['trackId'],
                timestamp=datetime.utcnow().isoformat(),
                data={
                    'name': app['trackName'],
                    'developer': app['sellerName'],
                    'rating': app.get('averageUserRating'),
                    'rating_count': app.get('userRatingCount'),
                    'version': app.get('version'),
                    'genres': app.get('genres', []),
                    'url': app.get('trackViewUrl')
                }
            )

# app_radar/data_sources/crunchbase.py
class CrunchbaseDataSource(BaseDataSource):

    async def fetch(self, company_name: str) -> DataSourceResult:
        # Crunchbase API v4
        url = "https://api.crunchbase.com/api/v4/autocompletes"
        headers = {"X-cb-user-key": self.config['api_key']}

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                params={"query": company_name, "collection_ids": "organizations"},
                headers=headers
            )
            data = resp.json()

            # 解析融资轮次、员工数等
            org = data['entities'][0] if data.get('entities') else None

            return DataSourceResult(
                source="crunchbase",
                app_id=company_name,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    'funding_total': org.get('funding_total', {}).get('value'),
                    'employee_count': org.get('num_employees_enum'),
                    'last_funding_type': org.get('last_funding_type'),
                    'investors': org.get('investor_names', [])
                }
            )
```

---

## 3. 指标体系

### 3.1 指标分层架构

```
Tier 1: 基础指标 (Raw Metrics)
├─ 评分 (Rating)
├─ 评论数 (Review Count)
├─ 版本号 (Version)
├─ 更新日期 (Last Update)
└─ 类别 (Category)

Tier 2: 增长指标 (Growth Signals)
├─ 7日评论增速 (7d Review Growth %)
├─ 30日评论增速 (30d Review Growth %)
├─ 版本更新频率 (Release Cadence)
├─ 榜单排名变化 (Ranking Trend)
└─ 情感趋势 (Sentiment Trend)

Tier 3: 竞争力指标 (Competitive Metrics)
├─ 护城河指数 (Moat Score 1-10)
│   ├─ 技术壁垒 (AI/算法/专利)
│   ├─ 网络效应 (UGC/社交图谱)
│   ├─ 品牌壁垒 (知名度/信任)
│   └─ 数据壁垒 (独家数据源)
├─ 团队规模 (Team Size)
├─ 融资情况 (Funding Stage)
└─ DAU/MAU 估算 (Estimated Active Users)

Tier 4: 战略洞察 (Strategic Insights)
├─ 商业模式 (Freemium/Subscription/Ad)
├─ 增长策略 (Viral/Paid/Organic)
├─ 目标用户 (User Persona)
└─ 核心竞争力 (Key Differentiators)
```

### 3.2 数据库 Schema 设计

```sql
-- apps 基础表
CREATE TABLE apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_identifier TEXT UNIQUE NOT NULL,  -- bundle_id 或 package_name
    name TEXT NOT NULL,
    platform TEXT CHECK(platform IN ('ios', 'android')),
    developer TEXT,
    category TEXT,
    url TEXT,
    first_tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- metrics 历史指标表
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER REFERENCES apps(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 基础指标
    rating REAL,
    rating_count INTEGER,
    version TEXT,

    -- 估算指标
    estimated_downloads INTEGER,
    estimated_dau INTEGER,
    estimated_mau INTEGER,

    -- 榜单数据
    rank_overall INTEGER,
    rank_category INTEGER,

    -- 元数据
    source TEXT,  -- 数据来源标记
    confidence REAL  -- 数据可信度 0-1
);

-- 创建时间序列索引
CREATE INDEX idx_metrics_timestamp ON metrics(app_id, timestamp);

-- company_info 公司信息表
CREATE TABLE company_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT UNIQUE NOT NULL,
    employee_count_min INTEGER,
    employee_count_max INTEGER,
    funding_total REAL,
    funding_stage TEXT,
    last_funding_date DATE,
    headquarters TEXT,
    founded_year INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- app_company 关联表
CREATE TABLE app_company (
    app_id INTEGER REFERENCES apps(id),
    company_id INTEGER REFERENCES company_info(id),
    PRIMARY KEY (app_id, company_id)
);

-- insights AI 生成的洞察表
CREATE TABLE insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER REFERENCES apps(id),
    insight_type TEXT,  -- 'moat', 'strategy', 'risk'
    content TEXT,
    confidence REAL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version TEXT  -- 记录使用的模型版本
);

-- reviews 评论样本表(用于情感分析)
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER REFERENCES apps(id),
    rating INTEGER,
    title TEXT,
    content TEXT,
    author TEXT,
    date DATE,
    sentiment REAL,  -- -1 到 1
    language TEXT
);
```

### 3.3 指标计算逻辑

```python
# app_radar/analytics/metrics.py

class MetricsCalculator:

    def calculate_growth_rate(self, app_id: int, days: int = 7) -> float:
        """计算评论增速"""
        query = """
            SELECT rating_count, timestamp
            FROM metrics
            WHERE app_id = ? AND timestamp >= date('now', '-{days} days')
            ORDER BY timestamp
        """.format(days=days)

        results = db.execute(query, [app_id])
        if len(results) < 2:
            return 0.0

        old_count = results[0]['rating_count']
        new_count = results[-1]['rating_count']

        return ((new_count - old_count) / old_count) * 100 if old_count > 0 else 0.0

    def estimate_dau(self, rating_count: int, rating: float) -> int:
        """
        基于评论数和评分估算 DAU
        假设模型: DAU = rating_count * conversion_rate * engagement_multiplier

        Benchmark 数据(需要校准):
        - 高质量应用(4.5+): 1% 用户会评论
        - 中等应用(3.5-4.5): 0.5% 用户会评论
        - 低质量应用(<3.5): 0.2% 用户会评论
        """
        if rating >= 4.5:
            conversion = 0.01
        elif rating >= 3.5:
            conversion = 0.005
        else:
            conversion = 0.002

        total_users = rating_count / conversion
        dau = total_users * 0.2  # 假设 20% DAU/MAU ratio

        return int(dau)

    def calculate_moat_score(self, app_id: int) -> Dict[str, Any]:
        """
        使用 LLM 分析护城河
        """
        app_data = self.get_app_context(app_id)

        prompt = f"""
        分析以下应用的竞争护城河,从1-10打分并说明理由:

        应用: {app_data['name']}
        类别: {app_data['category']}
        开发者: {app_data['developer']}
        评分: {app_data['rating']}
        评论数: {app_data['rating_count']}

        评分维度:
        1. 技术壁垒(AI/算法/专利): ?/10
        2. 网络效应(UGC/社交): ?/10
        3. 品牌壁垒(知名度): ?/10
        4. 数据壁垒(独家数据): ?/10

        请以 JSON 格式返回:
        {{
            "technical_moat": 8,
            "network_effect": 6,
            "brand_moat": 9,
            "data_moat": 7,
            "total_score": 7.5,
            "reasoning": "...",
            "key_strengths": ["...", "..."],
            "vulnerabilities": ["...", "..."]
        }}
        """

        # 调用 LLM API
        response = await anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)
```

---

## 4. 模块化设计

### 4.1 目录结构

```
app_radar/
├── __init__.py
├── cli.py                    # 命令行入口
├── config/
│   ├── __init__.py
│   ├── settings.py          # Pydantic settings
│   └── logging_config.py
├── data_sources/
│   ├── __init__.py
│   ├── base.py             # 基类
│   ├── itunes.py
│   ├── google_play.py
│   ├── crunchbase.py
│   ├── github.py
│   └── registry.py         # 数据源注册中心
├── models/
│   ├── __init__.py
│   ├── app.py              # Pydantic models
│   ├── metric.py
│   └── insight.py
├── storage/
│   ├── __init__.py
│   ├── database.py         # SQLAlchemy models
│   ├── migrations/         # Alembic migrations
│   └── cache.py            # Redis/Memory cache
├── analytics/
│   ├── __init__.py
│   ├── metrics.py          # 指标计算
│   ├── trends.py           # 趋势分析
│   ├── moat_analyzer.py    # LLM 护城河分析
│   └── rankings.py         # 榜单逻辑
├── reporting/
│   ├── __init__.py
│   ├── markdown.py         # Markdown 报告生成
│   ├── slack.py            # Slack Block Kit
│   ├── charts.py           # 图表生成
│   └── templates/          # Jinja2 模板
├── integrations/
│   ├── __init__.py
│   ├── slack_webhook.py
│   ├── email_sender.py
│   └── notion.py           # (可选) Notion 数据库同步
├── scheduler/
│   ├── __init__.py
│   ├── jobs.py             # APScheduler 任务
│   └── cron.py
└── utils/
    ├── __init__.py
    ├── retry.py            # 重试装饰器
    ├── rate_limiter.py
    └── validators.py
```

### 4.2 依赖注入示例

```python
# app_radar/cli.py
import typer
from app_radar.config.settings import Settings
from app_radar.data_sources.registry import DataSourceRegistry
from app_radar.analytics.metrics import MetricsCalculator

app = typer.Typer()

@app.command()
def fetch(
    app_name: str,
    sources: str = "itunes,crunchbase",
    output: str = "json"
):
    """
    从多个数据源采集应用数据

    示例:
        python -m app_radar fetch "Lemon8" --sources=itunes,crunchbase
    """
    settings = Settings()
    registry = DataSourceRegistry(settings)

    results = {}
    for source_name in sources.split(','):
        source = registry.get(source_name)
        data = await source.fetch_with_retry(app_name)
        results[source_name] = data

    if output == "json":
        print(json.dumps(results, indent=2))

@app.command()
def analyze(report_type: str = "top20"):
    """
    运行分析任务并生成报告
    """
    from app_radar.analytics.rankings import RankingAnalyzer
    from app_radar.reporting.slack import SlackReporter

    analyzer = RankingAnalyzer()
    top_apps = analyzer.get_top_apps(limit=20)

    reporter = SlackReporter()
    reporter.send_report(top_apps)

if __name__ == "__main__":
    app()
```

---

## 5. 存储方案

### 5.1 SQLite vs PostgreSQL

| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| **部署复杂度** | ⭐⭐⭐⭐⭐ 单文件 | ⭐⭐ 需要服务 |
| **并发写入** | ⭐⭐ 有限制 | ⭐⭐⭐⭐⭐ 优秀 |
| **查询性能** | ⭐⭐⭐⭐ 足够快 | ⭐⭐⭐⭐⭐ 更强 |
| **扩展性** | ⭐⭐ 单机 | ⭐⭐⭐⭐⭐ 可扩展 |
| **JSON 支持** | ⭐⭐⭐ JSON1 扩展 | ⭐⭐⭐⭐⭐ 原生 JSONB |

**推荐策略:**
- **阶段 1**: 使用 SQLite (数据量 < 100 万条记录)
- **阶段 2**: 数据增长后迁移到 PostgreSQL
- 设计时使用 SQLAlchemy ORM,保证可迁移性

### 5.2 缓存策略

```python
# app_radar/storage/cache.py
from functools import wraps
import hashlib
import json

class CacheManager:
    """
    多级缓存:
    L1: 内存 (LRU, 1000 items)
    L2: Redis (可选, TTL 1h)
    L3: SQLite (持久化)
    """

    def __init__(self, use_redis: bool = False):
        self.memory_cache = {}  # 简单 dict,生产环境用 lru_cache
        self.use_redis = use_redis
        if use_redis:
            import redis
            self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def cache_key(self, source: str, identifier: str) -> str:
        """生成缓存键"""
        return hashlib.md5(f"{source}:{identifier}".encode()).hexdigest()

    async def get(self, source: str, identifier: str):
        key = self.cache_key(source, identifier)

        # L1: 内存
        if key in self.memory_cache:
            return self.memory_cache[key]

        # L2: Redis
        if self.use_redis:
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                self.memory_cache[key] = data  # 回填 L1
                return data

        return None

    async def set(self, source: str, identifier: str, data: Any, ttl: int = 3600):
        key = self.cache_key(source, identifier)

        # L1
        self.memory_cache[key] = data

        # L2
        if self.use_redis:
            self.redis.setex(key, ttl, json.dumps(data))
```

---

## 6. 展示层设计

### 6.1 Slack Block Kit 升级方案

**当前问题:**
- 洞察内容是硬编码,不是基于实际数据生成
- 缺少图表可视化
- 无交互能力

**改进方案:**

```python
# app_radar/reporting/slack.py
class SlackReporter:

    def create_top20_report(self, apps: List[AppWithMetrics]) -> Dict:
        blocks = [
            self._header_block(),
            self._kpi_summary_block(apps),
            self._divider(),
            *self._top_apps_blocks(apps),
            self._divider(),
            *self._ai_insights_blocks(apps),  # LLM 生成洞察
            self._chart_block(apps),          # 趋势图表
            self._action_buttons_block()      # 交互按钮
        ]

        return {"blocks": blocks}

    def _kpi_summary_block(self, apps):
        """KPI 概览"""
        total_reviews = sum(a.rating_count for a in apps)
        avg_rating = statistics.mean(a.rating for a in apps)
        top_growth = max(apps, key=lambda a: a.growth_7d)

        return {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*📊 总评论数*\n{format_number(total_reviews)}"},
                {"type": "mrkdwn", "text": f"*⭐ 平均评分*\n{avg_rating:.2f}"},
                {"type": "mrkdwn", "text": f"*🚀 增速冠军*\n{top_growth.name} (+{top_growth.growth_7d:.1f}%)"},
                {"type": "mrkdwn", "text": f"*💰 融资最高*\n{max(apps, key=lambda a: a.funding).name}"}
            ]
        }

    def _ai_insights_blocks(self, apps):
        """使用 LLM 生成动态洞察"""
        # 构造上下文
        context = self._build_context_for_llm(apps)

        prompt = f"""
        基于以下 TOP20 应用数据,生成 3-5 条核心商业洞察,每条包含:
        1. 洞察标题(emoji + 简短描述)
        2. 支撑数据(具体应用名 + 指标)
        3. 可执行建议

        数据:
        {json.dumps(context, ensure_ascii=False, indent=2)}

        返回 JSON 格式:
        [
            {{
                "title": "🎮 游戏化留存策略",
                "evidence": "Duolingo 7日留存率 68%,采用 Streak 机制",
                "action": "建议在产品中加入连续签到奖励"
            }},
            ...
        ]
        """

        insights = call_llm_api(prompt)

        blocks = []
        for insight in insights:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{insight['title']}*\n{insight['evidence']}\n💡 {insight['action']}"
                }
            })

        return blocks

    def _chart_block(self, apps):
        """
        生成趋势图并上传到 Slack
        """
        import matplotlib.pyplot as plt

        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))

        # 绘制评论数 vs 评分散点图
        x = [a.rating for a in apps]
        y = [a.rating_count for a in apps]
        labels = [a.name for a in apps]

        ax.scatter(x, y, s=100, alpha=0.6)
        for i, label in enumerate(labels):
            ax.annotate(label, (x[i], y[i]), fontsize=8)

        ax.set_xlabel('Rating')
        ax.set_ylabel('Review Count')
        ax.set_title('APP评分 vs 用户参与度')

        # 保存到临时文件
        chart_path = "/tmp/app_radar_chart.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')

        # 上传到 Slack 并获取 URL
        chart_url = self._upload_chart_to_slack(chart_path)

        return {
            "type": "image",
            "image_url": chart_url,
            "alt_text": "评分与参与度关系图"
        }

    def _action_buttons_block(self):
        """交互按钮"""
        return {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📈 查看完整报告"},
                    "url": "https://your-dashboard.com/reports/latest",
                    "action_id": "view_full_report"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔔 订阅更新"},
                    "action_id": "subscribe_updates"
                }
            ]
        }
```

### 6.2 图表生成方案

**选项 1: matplotlib (静态图片)**
- 优点: 成熟稳定,样式丰富
- 缺点: 不支持交互

**选项 2: plotly (交互式图表)**
- 优点: 可交互,支持导出 HTML
- 缺点: 文件较大

**推荐:**
- Slack 推送: 使用 matplotlib 生成 PNG 上传
- Dashboard 网页: 使用 plotly 生成交互式图表

---

## 7. 调度与监控

### 7.1 调度方案

```python
# app_radar/scheduler/jobs.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(CronTrigger(hour='*/8'))  # 每 8 小时
async def fetch_and_analyze():
    """主任务: 采集 -> 分析 -> 推送"""
    logger.info("Starting scheduled job: fetch_and_analyze")

    try:
        # 1. 采集数据
        apps = await fetch_all_apps()
        logger.info(f"Fetched {len(apps)} apps")

        # 2. 存储到数据库
        await save_to_database(apps)

        # 3. 运行分析
        analyzer = RankingAnalyzer()
        top20 = analyzer.get_top_apps(limit=20)

        # 4. 生成报告
        reporter = SlackReporter()
        await reporter.send_report(top20)

        logger.info("Job completed successfully")

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)
        # 发送告警
        await send_alert_to_slack(f"❌ 定时任务失败: {e}")

# 启动调度器
def start_scheduler():
    scheduler.start()
    logger.info("Scheduler started")
```

### 7.2 监控与告警

```python
# app_radar/utils/monitoring.py
from loguru import logger
import sentry_sdk

# 集成 Sentry (可选)
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")

class MetricsCollector:
    """采集运行指标"""

    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }

    def record_api_call(self, source: str, duration: float):
        self.metrics['api_calls'] += 1
        logger.info(f"API call to {source} took {duration:.2f}s")

    def record_error(self, error: Exception):
        self.metrics['errors'] += 1
        logger.error(f"Error occurred: {error}")
        sentry_sdk.capture_exception(error)

    async def send_daily_summary(self):
        """每日发送指标汇总到 Slack"""
        message = f"""
        📊 App Radar 每日运行报告

        - API 调用: {self.metrics['api_calls']}
        - 缓存命中率: {self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100:.1f}%
        - 错误数: {self.metrics['errors']}
        """

        await send_to_slack(message)
```

---

## 8. 实施路线图

### Phase 1: 架构重构 (2 周)

**目标**: 模块化 + 存储层

- [ ] 重构代码为模块化结构
- [ ] 实现数据源抽象层
- [ ] 设计并实现 SQLite 数据库
- [ ] 添加配置管理(pydantic-settings)
- [ ] 实现缓存层
- [ ] 单元测试覆盖率 > 70%

**产出**:
- 可扩展的代码架构
- 历史数据存储能力

---

### Phase 2: 多数据源接入 (3 周)

**目标**: 丰富数据维度

- [ ] 实现 Google Play 数据源
- [ ] 实现 Crunchbase 数据源
- [ ] 实现 GitHub 数据源
- [ ] 实现评论抓取与情感分析
- [ ] 实现 DAU/MAU 估算算法
- [ ] 数据质量验证与清洗

**产出**:
- 支持 iOS + Android
- 融资、团队数据
- 用户活跃度估算

---

### Phase 3: 高级分析 (2 周)

**目标**: 护城河分析 + LLM 洞察

- [ ] 实现趋势分析(7d/30d 增速)
- [ ] 集成 Claude API 做护城河分析
- [ ] 实现榜单排名追踪
- [ ] 生成战略洞察与建议
- [ ] 图表可视化

**产出**:
- 智能洞察报告
- 护城河评分系统

---

### Phase 4: 展示与集成 (1 周)

**目标**: 优化报告质量

- [ ] 升级 Slack Block Kit 布局
- [ ] 图表生成与上传
- [ ] 支持交互按钮
- [ ] Email 报告(可选)
- [ ] Notion 数据库同步(可选)

**产出**:
- 美观的 Slack 报告
- 多渠道推送能力

---

### Phase 5: 生产化 (1 周)

**目标**: 稳定性与可维护性

- [ ] 实现 APScheduler 调度
- [ ] 日志与监控系统
- [ ] 错误告警机制
- [ ] Docker 容器化
- [ ] CI/CD 流水线
- [ ] 文档完善

**产出**:
- 可部署的生产系统
- 运维手册

---

## 9. 成本估算

| 项目 | 免费额度 | 付费成本(月) |
|------|----------|--------------|
| **数据源** | | |
| iTunes API | 无限制 | $0 |
| Google Play | 爬虫 | $0 |
| Crunchbase | 50 req/月 | $0-29 |
| GitHub API | 5000 req/h | $0 |
| **LLM API** | | |
| Claude API | $5 免费额度 | ~$10-50 |
| **基础设施** | | |
| Slack | 免费 | $0 |
| SQLite | 本地存储 | $0 |
| **总计** | | **$10-80/月** |

---

## 10. 风险与注意事项

### 10.1 API 合规性

⚠️ **Google Play 数据**: 官方无公开 API,需使用非官方库,存在被封禁风险
- **缓解**: 控制频率,使用代理池,模拟正常用户行为

⚠️ **评论抓取**: 可能违反服务条款
- **缓解**: 只抓取公开数据,尊重 robots.txt,合理间隔

### 10.2 数据准确性

⚠️ **DAU/MAU 估算**: 基于假设模型,可能偏差较大
- **缓解**: 明确标注"估算值",提供置信区间,使用多模型交叉验证

### 10.3 LLM 幻觉

⚠️ **护城河分析**: LLM 可能生成不准确的洞察
- **缓解**: 要求提供支撑证据,人工审核关键结论,版本控制 prompt

---

## 11. 总结

本架构方案在保持当前简单性的基础上,逐步演进为多维度商业智能分析系统:

✅ **模块化**: 清晰的分层架构,易于扩展
✅ **数据驱动**: 多源数据整合,历史趋势分析
✅ **智能化**: LLM 辅助洞察生成
✅ **生产级**: 监控、告警、容错机制
✅ **成本可控**: 优先使用免费数据源,按需升级

**关键成功因素:**
1. 分阶段实施,先验证核心价值
2. 数据质量优先于数据数量
3. 保持代码可测试性和可维护性
4. 持续优化 LLM prompt 质量

---

**附录: 参考资源**

- [iTunes Search API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/)
- [Crunchbase API v4](https://data.crunchbase.com/docs)
- [Slack Block Kit Builder](https://app.slack.com/block-kit-builder)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [APScheduler](https://apscheduler.readthedocs.io/)
