# App Radar Agent v2.0 - 实施指南

> 从当前版本升级到多维度商业智能系统的具体操作步骤

## 📚 前置阅读

在开始实施之前,请先阅读:
- [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) - 整体技术架构
- 当前代码: `scripts/*.py` - 理解现有实现

---

## 🎯 实施策略

### 原则

1. **渐进式重构**: 不推倒重来,逐步迁移
2. **向后兼容**: 保证现有功能持续可用
3. **测试驱动**: 每个模块先写测试
4. **快速验证**: 2 周一个 milestone,持续产出价值

---

## 阶段 1: 架构重构 (Week 1-2)

### 目标

将单文件脚本重构为模块化架构,引入数据库存储

### 步骤 1.1: 创建项目结构

```bash
# 1. 创建新的模块化目录结构
mkdir -p app_radar/{config,data_sources,models,storage,analytics,reporting,integrations,scheduler,utils}

# 2. 创建 __init__.py 文件
find app_radar -type d -exec touch {}/__init__.py \;

# 3. 创建测试目录
mkdir -p tests/{unit,integration}
touch tests/__init__.py
```

### 步骤 1.2: 迁移配置管理

**创建 `app_radar/config/settings.py`:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # 数据库配置
    database_url: str = "sqlite:///./data/app_radar.db"

    # API Keys
    crunchbase_api_key: Optional[str] = None
    github_token: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Slack 配置
    slack_webhook_url: Optional[str] = None

    # 数据源配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour

    # 目标应用列表
    target_apps: List[str] = [
        "Lemon8", "CapCut", "Notion",
        "Temu", "Duolingo", "Canva"
    ]

    # 调度配置
    schedule_interval_hours: int = 8

# 全局配置实例
settings = Settings()
```

**创建 `.env` 文件:**

```bash
# .env (添加到 .gitignore!)
DATABASE_URL=sqlite:///./data/app_radar.db
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ANTHROPIC_API_KEY=sk-ant-xxx
CRUNCHBASE_API_KEY=your_key_here
```

### 步骤 1.3: 实现数据库模型

**创建 `app_radar/storage/database.py`:**

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app_radar.config.settings import settings

Base = declarative_base()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True)
    app_identifier = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    platform = Column(String)  # 'ios' or 'android'
    developer = Column(String)
    category = Column(String)
    url = Column(String)
    first_tracked_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, nullable=False)  # Foreign key
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 基础指标
    rating = Column(Float)
    rating_count = Column(Integer)
    version = Column(String)

    # 估算指标
    estimated_dau = Column(Integer)

    # 元数据
    source = Column(String)
    confidence = Column(Float)

# 创建所有表
def init_db():
    Base.metadata.create_all(engine)

# 数据库会话管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**初始化数据库:**

```python
# scripts/init_db.py
from app_radar.storage.database import init_db

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully")
```

### 步骤 1.4: 重构数据源为抽象层

**创建 `app_radar/data_sources/base.py`:**

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

class DataSourceResult(BaseModel):
    """统一的数据源返回格式"""
    source: str
    app_identifier: str
    timestamp: datetime
    data: Dict[str, Any]

class BaseDataSource(ABC):
    """数据源基类"""

    def __init__(self, config: Dict):
        self.config = config

    @abstractmethod
    async def fetch(self, app_identifier: str) -> DataSourceResult:
        """子类必须实现的抓取方法"""
        pass
```

**迁移现有 iTunes 逻辑到 `app_radar/data_sources/itunes.py`:**

```python
import httpx
from datetime import datetime
from .base import BaseDataSource, DataSourceResult

class ITunesDataSource(BaseDataSource):

    async def fetch(self, app_name: str) -> DataSourceResult:
        url = f"https://itunes.apple.com/search?term={app_name}&entity=software"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if not data.get('results'):
                raise ValueError(f"App not found: {app_name}")

            app = data['results'][0]

            return DataSourceResult(
                source="itunes",
                app_identifier=str(app['trackId']),
                timestamp=datetime.utcnow(),
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
```

### 步骤 1.5: 创建统一的 CLI 入口

**创建 `app_radar/cli.py`:**

```python
import typer
import asyncio
from app_radar.config.settings import settings
from app_radar.data_sources.itunes import ITunesDataSource
from app_radar.storage.database import get_db, App, Metric

app = typer.Typer()

@app.command()
def fetch():
    """采集所有目标应用数据"""
    asyncio.run(_fetch_async())

async def _fetch_async():
    itunes = ITunesDataSource({})

    for app_name in settings.target_apps:
        typer.echo(f"Fetching {app_name}...")
        result = await itunes.fetch(app_name)

        # 保存到数据库
        db = next(get_db())

        # 查找或创建 App 记录
        app_record = db.query(App).filter_by(
            app_identifier=result.app_identifier
        ).first()

        if not app_record:
            app_record = App(
                app_identifier=result.app_identifier,
                name=result.data['name'],
                platform='ios',
                developer=result.data['developer'],
                url=result.data['url']
            )
            db.add(app_record)
            db.commit()

        # 添加 Metric 记录
        metric = Metric(
            app_id=app_record.id,
            rating=result.data['rating'],
            rating_count=result.data['rating_count'],
            version=result.data['version'],
            source='itunes'
        )
        db.add(metric)
        db.commit()

        typer.echo(f"✅ {app_name}: {result.data['rating']} stars")

@app.command()
def analyze():
    """运行分析并生成报告"""
    typer.echo("分析功能开发中...")

if __name__ == "__main__":
    app()
```

### 步骤 1.6: 更新依赖

**更新 `requirements.txt`:**

```txt
# Core
requests
httpx
PyYAML

# Database
sqlalchemy>=2.0
alembic

# Configuration
pydantic>=2.0
pydantic-settings

# CLI
typer[all]

# Logging
loguru

# Async
asyncio

# Testing
pytest
pytest-asyncio
pytest-mock
```

**安装依赖:**

```bash
pip install -r requirements.txt
```

### 步骤 1.7: 测试新架构

**创建测试文件 `tests/unit/test_itunes.py`:**

```python
import pytest
from app_radar.data_sources.itunes import ITunesDataSource

@pytest.mark.asyncio
async def test_fetch_lemon8():
    """测试获取 Lemon8 数据"""
    source = ITunesDataSource({})
    result = await source.fetch("Lemon8")

    assert result.source == "itunes"
    assert "Lemon8" in result.data['name']
    assert result.data['rating'] > 0
    assert result.data['rating_count'] > 0

@pytest.mark.asyncio
async def test_fetch_nonexistent_app():
    """测试不存在的应用"""
    source = ITunesDataSource({})

    with pytest.raises(ValueError):
        await source.fetch("ThisAppDefinitelyDoesNotExist12345")
```

**运行测试:**

```bash
pytest tests/ -v
```

### 阶段 1 验收标准

- [x] 新目录结构已创建
- [x] 配置管理迁移到 pydantic-settings
- [x] SQLite 数据库已初始化
- [x] iTunes 数据源重构为类
- [x] CLI 可以运行 `python -m app_radar fetch`
- [x] 数据成功写入数据库
- [x] 测试通过

---

## 阶段 2: 多数据源接入 (Week 3-5)

### 步骤 2.1: 添加 Crunchbase 数据源

**创建 `app_radar/data_sources/crunchbase.py`:**

```python
import httpx
from datetime import datetime
from .base import BaseDataSource, DataSourceResult

class CrunchbaseDataSource(BaseDataSource):

    async def fetch(self, company_name: str) -> DataSourceResult:
        url = "https://api.crunchbase.com/api/v4/autocompletes"
        headers = {"X-cb-user-key": self.config.get('api_key')}

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                params={"query": company_name, "collection_ids": "organizations"},
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            if not data.get('entities'):
                return DataSourceResult(
                    source="crunchbase",
                    app_identifier=company_name,
                    timestamp=datetime.utcnow(),
                    data={}
                )

            org = data['entities'][0]

            return DataSourceResult(
                source="crunchbase",
                app_identifier=company_name,
                timestamp=datetime.utcnow(),
                data={
                    'company_name': org.get('identifier', {}).get('value'),
                    'funding_total_usd': org.get('funding_total', {}).get('value_usd'),
                    'employee_count': org.get('num_employees_enum'),
                    'last_funding_type': org.get('last_funding_type')
                }
            )
```

### 步骤 2.2: 数据源注册中心

**创建 `app_radar/data_sources/registry.py`:**

```python
from typing import Dict
from .base import BaseDataSource
from .itunes import ITunesDataSource
from .crunchbase import CrunchbaseDataSource

class DataSourceRegistry:
    """数据源注册和管理"""

    def __init__(self, config: Dict):
        self.config = config
        self._sources = {}
        self._register_default_sources()

    def _register_default_sources(self):
        self.register('itunes', ITunesDataSource)
        self.register('crunchbase', CrunchbaseDataSource)

    def register(self, name: str, source_class: type):
        self._sources[name] = source_class

    def get(self, name: str) -> BaseDataSource:
        if name not in self._sources:
            raise ValueError(f"Unknown data source: {name}")

        source_class = self._sources[name]
        return source_class(self.config)

    def list_sources(self):
        return list(self._sources.keys())
```

### 步骤 2.3: 更新 CLI 支持多数据源

```python
# app_radar/cli.py (新增命令)

@app.command()
def fetch_all(sources: str = "itunes,crunchbase"):
    """从多个数据源采集"""
    asyncio.run(_fetch_all_async(sources.split(',')))

async def _fetch_all_async(source_names: List[str]):
    from app_radar.data_sources.registry import DataSourceRegistry

    registry = DataSourceRegistry({
        'api_key': settings.crunchbase_api_key
    })

    for app_name in settings.target_apps:
        for source_name in source_names:
            source = registry.get(source_name)
            result = await source.fetch(app_name)
            # ... 保存逻辑
```

---

## 阶段 3: 高级分析 (Week 6-7)

### 步骤 3.1: 实现趋势分析

**创建 `app_radar/analytics/trends.py`:**

```python
from sqlalchemy import func
from app_radar.storage.database import get_db, Metric

class TrendAnalyzer:

    def calculate_growth_rate(self, app_id: int, days: int = 7) -> float:
        """计算评论增长率"""
        db = next(get_db())

        # 获取 N 天前的数据
        old_metric = db.query(Metric).filter(
            Metric.app_id == app_id,
            Metric.timestamp >= func.date('now', f'-{days} days')
        ).order_by(Metric.timestamp.asc()).first()

        # 获取最新数据
        new_metric = db.query(Metric).filter(
            Metric.app_id == app_id
        ).order_by(Metric.timestamp.desc()).first()

        if not old_metric or not new_metric:
            return 0.0

        old_count = old_metric.rating_count
        new_count = new_metric.rating_count

        if old_count == 0:
            return 0.0

        growth = ((new_count - old_count) / old_count) * 100
        return round(growth, 2)
```

### 步骤 3.2: LLM 护城河分析

**创建 `app_radar/analytics/moat_analyzer.py`:**

```python
from anthropic import Anthropic
from app_radar.config.settings import settings
import json

class MoatAnalyzer:

    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def analyze(self, app_data: dict) -> dict:
        """使用 Claude 分析护城河"""

        prompt = f"""
分析以下应用的竞争护城河,从 1-10 打分:

应用名称: {app_data['name']}
开发者: {app_data['developer']}
类别: {app_data['category']}
评分: {app_data['rating']} ({app_data['rating_count']} 评论)

请从以下维度评分:
1. 技术壁垒 (AI/算法/专利): ?/10
2. 网络效应 (UGC/社交图谱): ?/10
3. 品牌壁垒 (知名度/信任): ?/10
4. 数据壁垒 (独家数据源): ?/10

以 JSON 格式返回:
{{
    "technical_moat": 7,
    "network_effect": 8,
    "brand_moat": 9,
    "data_moat": 6,
    "total_score": 7.5,
    "reasoning": "详细分析...",
    "key_strengths": ["优势1", "优势2"],
    "vulnerabilities": ["风险1", "风险2"]
}}
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        # 解析 JSON 响应
        return json.loads(response.content[0].text)
```

---

## 阶段 4: Slack 展示升级 (Week 8)

### 步骤 4.1: 图表生成

**创建 `app_radar/reporting/charts.py`:**

```python
import matplotlib.pyplot as plt
from typing import List

class ChartGenerator:

    def create_scatter_chart(self, apps: List[dict], output_path: str):
        """评分 vs 评论数散点图"""
        fig, ax = plt.subplots(figsize=(10, 6))

        x = [app['rating'] for app in apps]
        y = [app['rating_count'] for app in apps]
        labels = [app['name'] for app in apps]

        ax.scatter(x, y, s=100, alpha=0.6, c='#FF6B6B')

        for i, label in enumerate(labels):
            ax.annotate(label, (x[i], y[i]), fontsize=9, alpha=0.7)

        ax.set_xlabel('Rating (评分)', fontsize=12)
        ax.set_ylabel('Review Count (评论数)', fontsize=12)
        ax.set_title('APP 评分与用户参与度', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Chart saved to {output_path}")
```

### 步骤 4.2: 升级 Slack 报告

参考 `TECHNICAL_ARCHITECTURE.md` 第 6 节的完整实现

---

## 阶段 5: 生产化 (Week 9)

### 步骤 5.1: 添加调度器

**创建 `app_radar/scheduler/jobs.py`:**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(CronTrigger(hour='*/8'))
async def fetch_and_report():
    """每 8 小时运行一次"""
    logger.info("Starting scheduled job")

    # 1. 采集数据
    # 2. 分析
    # 3. 推送 Slack

    logger.info("Job completed")

def start():
    scheduler.start()
    logger.info("Scheduler started")
```

### 步骤 5.2: Docker 容器化

**创建 `Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app_radar.scheduler.jobs"]
```

**创建 `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  app-radar:
    build: .
    environment:
      - DATABASE_URL=sqlite:///./data/app_radar.db
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

---

## 快速开始清单

### 第一周

- [ ] Day 1: 创建模块化目录结构
- [ ] Day 2: 实现配置管理 + 数据库模型
- [ ] Day 3: 重构 iTunes 数据源
- [ ] Day 4: 实现 CLI 入口
- [ ] Day 5: 测试 + 文档

### 第二周

- [ ] Day 1-2: 添加 Crunchbase 数据源
- [ ] Day 3-4: 实现趋势分析
- [ ] Day 5: 集成 LLM 护城河分析

### 第三周

- [ ] Day 1-2: 升级 Slack Block Kit
- [ ] Day 3: 图表生成
- [ ] Day 4: 调度器实现
- [ ] Day 5: Docker 部署 + 上线

---

## 常见问题

### Q1: 需要推倒重来吗?

**不需要**。采用渐进式迁移:
1. 先创建新架构(app_radar/ 模块)
2. 逐步迁移功能
3. 保留 scripts/ 作为兼容层
4. 完成迁移后再删除旧代码

### Q2: 如何保证数据一致性?

使用 SQLAlchemy 的事务:

```python
from sqlalchemy.exc import IntegrityError

db = next(get_db())
try:
    db.add(app_record)
    db.commit()
except IntegrityError:
    db.rollback()
    raise
```

### Q3: LLM API 成本会不会很高?

控制调用频率:
- 只对 TOP20 应用做深度分析
- 缓存 LLM 结果 24 小时
- 使用 Haiku 模型(更便宜)

预估成本: 每天 20 个应用 × $0.01 = $0.20/天 = $6/月

---

## 下一步

1. **立即开始**: 按照阶段 1 步骤开始重构
2. **持续迭代**: 每周 review 进展,调整计划
3. **保持简单**: 不要过度设计,按需添加功能

**Good luck!** 🚀
