# App Radar Agent v2.0 - 快速开始指南

## 🎉 已完成！系统已成功运行

系统刚刚采集了真实数据：
- ✅ CapCut: 4.7⭐ (1,081,461 评论)
- ✅ Lemon8: 4.6⭐ (206,012 评论)
- ✅ Notion: 4.8⭐ (70,919 评论)

## 📁 项目结构

```
app-radar-agent/
├── app_radar/              # 主应用代码
│   ├── config/            # 配置管理
│   ├── data_sources/      # 数据源(iTunes API)
│   ├── storage/           # 数据库模型
│   ├── analytics/         # 分析引擎(待实现)
│   ├── reporting/         # 报告生成
│   │   ├── charts.py     # 图表生成 ✅
│   │   └── slack.py      # Slack 推送 ✅
│   └── cli.py            # 命令行入口 ✅
├── data/
│   ├── app_radar.db      # SQLite 数据库 ✅
│   ├── charts/           # 生成的图表 ✅
│   └── results/          # 报告输出
├── docs/                  # 技术文档
├── .env                   # 环境变量(需创建)
└── requirements.txt       # Python 依赖 ✅
```

## 🚀 快速使用

### 1. 安装依赖(已完成)

```bash
pip install -r requirements.txt
```

### 2. 配置 Slack Webhook(必需)

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env`，添加你的 Slack Webhook URL：

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**获取 Webhook URL:**
1. 访问 https://api.slack.com/apps
2. 创建新应用或选择现有应用
3. 启用 "Incoming Webhooks"
4. 添加到你的频道
5. 复制 Webhook URL

### 3. 运行命令

#### 测试模式(只采集 3 个应用)
```bash
python3 -m app_radar --test
```

#### 采集 TOP 20 应用
```bash
python3 -m app_radar --top 20
```

#### 自定义应用列表
```bash
python3 -m app_radar --apps "Instagram,TikTok,WhatsApp,YouTube"
```

#### 跳过 Slack 推送(仅生成图表)
```bash
python3 -m app_radar --skip-slack
```

## 📊 输出内容

### 1. 数据库记录
- 位置: `data/app_radar.db`
- 包含应用信息和历史指标

### 2. 可视化图表
生成 3 张图表到 `data/charts/`:
- `rating_scatter.png` - 评分 vs 评论数散点图
- `growth_trend.png` - 7天增长趋势
- `category_dist.png` - 类别分布饼图

### 3. Slack 报告
发送到配置的频道，包含：
- 📈 核心指标(平均评分、总评论数等)
- 🏆 TOP N 应用列表
- 💡 核心洞察(自动分析)
- 🎯 操作按钮

## 🔧 高级配置

编辑 `app_radar/config/settings.py` 自定义：

```python
# 默认监控的应用列表
target_apps: List[str] = [
    "Lemon8", "CapCut", "Notion",
    "Temu", "Duolingo", "Canva",
    # ... 添加更多
]

# 调度间隔(小时)
schedule_interval_hours: int = 8
```

## 📈 实际数据示例

刚刚采集的真实数据：

| 应用 | 评分 | 评论数 | 类别 | 开发者 |
|------|------|--------|------|--------|
| CapCut | 4.65 | 1,081,461 | Video | ByteDance |
| Lemon8 | 4.60 | 206,012 | Lifestyle | TikTok |
| Notion | 4.79 | 70,919 | Productivity | Notion Labs |

## 🎯 下一步

### Phase 2 功能(可选)

1. **添加 Crunchbase 数据源**
   - 获取融资信息
   - 团队规模数据

2. **LLM 洞察生成**
   - 使用 Claude API 分析护城河
   - 战略建议生成

3. **定时调度**
   ```bash
   # 使用 cron 每 8 小时运行
   0 */8 * * * cd /path/to/app-radar-agent && python3 -m app_radar
   ```

4. **Dashboard 网页**
   - 部署 Streamlit/Gradio 界面
   - 实时数据查看

## ❓ 常见问题

### Q: Slack 推送失败？
**A:** 检查：
1. `.env` 文件中的 `SLACK_WEBHOOK_URL` 是否正确
2. Webhook URL 是否有效(访问 Slack App 设置页面确认)
3. 网络连接是否正常

### Q: 找不到某个应用？
**A:** iTunes Search API 可能找不到部分应用：
- 确保应用名称拼写正确
- 尝试使用完整名称
- 部分仅限特定地区的应用可能无法搜索到

### Q: 如何查看历史数据？
**A:** 使用 SQLite 查询：
```bash
sqlite3 data/app_radar.db
> SELECT * FROM apps;
> SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10;
```

## 📞 支持

- Issues: [GitHub Issues](https://github.com/yourusername/app-radar-agent/issues)
- 文档: 查看 `docs/` 目录

---

**🎉 恭喜！系统已经成功运行并采集真实数据！**

现在配置 Slack Webhook 即可开始自动推送报告。
