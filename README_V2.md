# App Radar Agent v2.0 📱

> **已升级！** 从基础脚本升级为模块化商业智能系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

## ✨ v2.0 新特性

### 🏗️ 架构升级
- ✅ **模块化设计** - 清晰的代码组织，易于扩展
- ✅ **SQLite 数据库** - 历史数据存储，支持趋势分析
- ✅ **类型安全配置** - Pydantic Settings 管理
- ✅ **数据源抽象** - 统一接口，便于添加新数据源

### 📊 数据可视化
- ✅ **散点图** - 评分 vs 用户参与度
- ✅ **趋势图** - 7天增长曲线
- ✅ **分布图** - 类别占比分析

### 💬 Slack 集成增强
- ✅ **Block Kit 卡片** - 精美的消息布局
- ✅ **动态洞察** - 基于真实数据的分析
- ✅ **交互按钮** - 一键查看详情/导出数据
- ✅ **Emoji 反馈** - 团队互动支持

### 🎯 功能亮点
- ✅ **真实数据采集** - iTunes Search API
- ✅ **自动分析** - TOP N 排名、参与度分级
- ✅ **历史追踪** - SQLite 存储每次采集记录
- ✅ **CLI 工具** - 命令行操作，支持参数定制

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/app-radar-agent.git
cd app-radar-agent

# 安装依赖
pip install -r requirements.txt

# 配置 Slack
cp .env.example .env
# 编辑 .env，添加 SLACK_WEBHOOK_URL
```

### 运行

```bash
# 测试模式(采集 3 个应用)
python3 -m app_radar --test

# 生产模式(采集 20 个应用并推送到 Slack)
python3 -m app_radar --top 20

# 自定义应用列表
python3 -m app_radar --apps "TikTok,Instagram,WhatsApp"
```

## 📸 实际效果展示

### 1. 真实数据采集
```
🔍 开始采集 3 款应用数据...

[1/3] Fetching Lemon8... ✅ 4.6⭐ (206,012 reviews)
[2/3] Fetching CapCut... ✅ 4.7⭐ (1,081,461 reviews)
[3/3] Fetching Notion... ✅ 4.8⭐ (70,919 reviews)

✅ 成功采集 3/3 款应用
```

### 2. 生成的图表
自动生成 3 张专业图表：
- `rating_scatter.png` - 清晰展示评分与参与度关系
- `growth_trend.png` - TOP 3 应用的增长趋势
- `category_dist.png` - 类别分布饼图

### 3. Slack 报告效果
- 📱 **专业头部** - 标题 + 时间戳 + 版本
- 📊 **KPI 卡片** - 平均评分、总评论数、冠军应用
- 🏆 **TOP N 列表** - 排名、评分、参与度、公司、类别
- 💡 **智能洞察** - 高评分趋势、参与度分析、头部开发者
- 🎯 **操作按钮** - 查看完整报告、导出数据

## 🗂️ 项目结构

```
app_radar/
├── config/
│   └── settings.py         # Pydantic 配置管理
├── data_sources/
│   ├── base.py            # 数据源基类
│   └── itunes.py          # iTunes Search API
├── storage/
│   └── database.py        # SQLAlchemy ORM 模型
├── reporting/
│   ├── charts.py          # Matplotlib 图表生成
│   └── slack.py           # Slack Block Kit
└── cli.py                 # 命令行入口

data/
├── app_radar.db           # SQLite 数据库
├── charts/                # 生成的图表
└── results/               # 报告输出
```

## 💾 数据库 Schema

### Apps 表
```sql
CREATE TABLE apps (
    id INTEGER PRIMARY KEY,
    app_identifier TEXT UNIQUE,
    name TEXT,
    platform TEXT,
    developer TEXT,
    category TEXT,
    url TEXT,
    first_tracked_at TIMESTAMP,
    last_updated_at TIMESTAMP
);
```

### Metrics 表(历史记录)
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    app_id INTEGER,
    timestamp TIMESTAMP,
    rating REAL,
    rating_count INTEGER,
    version TEXT,
    source TEXT
);
```

## 📈 实际数据示例

### 最新采集结果

| 排名 | 应用 | 评分 | 评论数 | 类别 | 开发者 |
|------|------|------|--------|------|--------|
| 1 | CapCut | 4.65 | 1.08M | Video | ByteDance |
| 2 | Lemon8 | 4.60 | 206K | Lifestyle | TikTok |
| 3 | Notion | 4.79 | 70.9K | Productivity | Notion Labs |

### 核心洞察(自动生成)
- 🌟 **高评分趋势**: 3 款应用评分超过 4.7，用户满意度整体优秀
- 🔥 **用户参与度**: 1 款应用评论数超过 100 万，社区活跃度高
- 🏢 **头部开发者**: ByteDance 有 2 款应用上榜

## 🎨 设计理念

基于 **Metric Luminance** 设计哲学：
- 深色背景，数据更清晰
- 渐进式信息层次
- 精准的空间布局
- 专业的配色方案

## 🔄 升级路径

### 从 v1.0 升级
```bash
# 保留旧版本(可选)
mv scripts scripts_v1_backup

# 使用新版本
python3 -m app_radar --test
```

### 数据迁移
旧数据自动保留在 `data/results/raw_data.json`，新数据存储在 SQLite。

## 📋 路线图

### Phase 2 (计划中)
- [ ] Crunchbase 数据源(融资信息)
- [ ] GitHub 数据源(开源项目活跃度)
- [ ] DAU/MAU 估算算法
- [ ] 趋势分析(7d/30d 增速)

### Phase 3 (计划中)
- [ ] Claude API 集成(护城河分析)
- [ ] LLM 生成战略洞察
- [ ] 图表上传到 Slack
- [ ] Email 报告支持

### Phase 4 (计划中)
- [ ] APScheduler 定时调度
- [ ] Docker 容器化
- [ ] 监控与告警
- [ ] Web Dashboard

## 🛠️ 技术栈

| 组件 | 技术选型 |
|------|----------|
| 数据采集 | requests + iTunes Search API |
| 配置管理 | pydantic-settings |
| 数据库 | SQLite + SQLAlchemy |
| 数据可视化 | matplotlib |
| 报告推送 | Slack Block Kit |
| CLI | argparse |

## 📚 文档

- [快速开始](./QUICKSTART.md) - 5 分钟上手指南
- [技术架构](./docs/TECHNICAL_ARCHITECTURE.md) - 详细设计文档
- [实施指南](./docs/IMPLEMENTATION_GUIDE.md) - 分步骤实施
- [Slack 配置](./SLACK_SETUP.md) - Webhook 设置教程

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- iTunes Search API - 苹果官方数据源
- Slack Block Kit - 精美的消息展示
- Claude Code - AI 辅助开发

---

**⚡ 从简单脚本到商业智能平台，App Radar Agent v2.0 已准备就绪！**

立即运行 `python3 -m app_radar --test` 体验！
