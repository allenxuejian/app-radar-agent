# ⚡️ Slack 集成快速开始（5 分钟）

## 第一步：获取 Slack Webhook URL（2 分钟）

### 1. 访问 Slack API 页面

在浏览器中打开：**https://api.slack.com/apps**

### 2. 创建新应用

- 点击绿色按钮 **"Create New App"**
- 选择 **"From scratch"**
- App Name: `App Radar Agent`
- 选择你的工作区
- 点击 **"Create App"**

### 3. 启用 Incoming Webhooks

- 左侧菜单找到 **"Incoming Webhooks"**
- 将开关切换到 **ON**
- 滚动到底部，点击 **"Add New Webhook to Workspace"**
- 选择要发送的频道（例如 `#app-research`）
- 点击 **"Allow"**

### 4. 复制 Webhook URL

页面会显示类似这样的 URL：
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

**复制这个 URL**（点击 Copy 按钮）

---

## 第二步：配置 App Radar Agent（1 分钟）

### 在终端运行以下命令：

```bash
# 保存 Webhook URL（替换为你刚才复制的 URL）
echo "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" > ~/.claude/agents/app-radar-agent-data/.slack_webhook

# 设置文件权限
chmod 600 ~/.claude/agents/app-radar-agent-data/.slack_webhook
```

**重要**: 替换 `YOUR/WEBHOOK/URL` 为你实际的 Webhook URL！

---

## 第三步：测试发送（1 分钟）

```bash
# 复制脚本到正确位置
cp ~/github/app-radar-agent/scripts/send_to_slack.py ~/.claude/agents/app-radar-agent-data/scripts/

# 测试发送
cd ~/.claude/agents/app-radar-agent-data
python3 scripts/send_to_slack.py --test
```

如果看到 ✅ 和 "Test message sent successfully!"，去 Slack 查看测试消息。

---

## 第四步：设置定时发送（1 分钟）

```bash
# 运行自动配置脚本
cd ~/github/app-radar-agent
./scripts/setup_cron.sh
```

按提示选择：
- 选项 1: 每 8 小时（推荐）
- 选项 2: 每天 2 次
- 选项 3: 每天 1 次
- 选项 4: 自定义

---

## 完成！🎉

现在你的 Slack 将定期收到：

### 报告内容预览：

```
📱 App Radar 商业产品调研报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 更新时间 | 📊 监测应用: 6 款 | 💬 总评论数: 11.9M

📈 核心指标
• 平均评分: 4.72/5.0
• 参与度冠军: Duolingo (4.7M 评论)
• 满意度最高: Canva (4.88 分)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🌟 Duolingo
   • 评分: 4.73 | 评论: 4.7M
   • 参与度: 🔥 极高
   • 公司: Duolingo, Inc
   • 类别: Education, Social | 版本: 7.99.0
   [查看详情]

2. ⭐️ Canva
   • 评分: 4.88 | 评论: 3.0M
   • 参与度: 🔥 极高
   • 公司: Canva Pty Ltd
   • 类别: Photo & Video, Productivity
   [查看详情]

... (更多应用)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 核心洞察
• 🎮 游戏化教育: Duolingo 展现 Streak 机制威力
• 🎨 创作工具: Canva/CapCut 平民化趋势明显
• 🛍️ 社交电商: Temu 裂变增长模式值得研究
• 📝 生产力: Notion All-in-One 整合趋势
• 🤖 AI 整合: 所有头部应用都在加入 AI 功能

🎯 可执行策略
1. Freemium 模式: 免费核心功能 + Pro 订阅
2. 模板市场: 降低门槛 + 社区生态
3. Streak 打卡: 连续使用奖励提升留存
4. AI 辅助: 智能推荐/自动优化

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 数据来源: iTunes Search API
🤖 生成工具: App Radar Agent v1.0
```

---

## 常用命令

```bash
# 手动触发发送
cd ~/.claude/agents/app-radar-agent-data
python3 scripts/send_to_slack.py

# 查看定时任务
crontab -l

# 查看发送日志
tail -f /tmp/app-radar-slack.log

# 编辑定时任务
crontab -e

# 删除定时任务
crontab -e  # 然后删除包含 "App Radar" 的行
```

---

## 故障排查

### 问题: Webhook 文件未找到
```bash
# 检查文件是否存在
ls -la ~/.claude/agents/app-radar-agent-data/.slack_webhook

# 重新创建
echo "YOUR_WEBHOOK_URL" > ~/.claude/agents/app-radar-agent-data/.slack_webhook
chmod 600 ~/.claude/agents/app-radar-agent-data/.slack_webhook
```

### 问题: 数据文件未找到
```bash
# 先运行数据抓取
cd ~/.claude/agents/app-radar-agent-data
python3 scripts/fetch_data.py
python3 scripts/analyze.py
```

### 问题: 权限错误
```bash
chmod +x ~/github/app-radar-agent/scripts/*.py
chmod +x ~/github/app-radar-agent/scripts/*.sh
```

---

## 高级配置

### 发送到多个频道

创建多个 webhook 文件：
```bash
echo "WEBHOOK_URL_1" > ~/.claude/agents/app-radar-agent-data/.slack_webhook_product
echo "WEBHOOK_URL_2" > ~/.claude/agents/app-radar-agent-data/.slack_webhook_engineering
```

### 自定义发送时间

编辑 crontab:
```bash
crontab -e
```

添加或修改：
```
0 9 * * *    # 每天 9:00 AM
0 14 * * *   # 每天 2:00 PM
0 21 * * *   # 每天 9:00 PM
```

---

## 需要帮助？

查看完整文档：`~/github/app-radar-agent/SLACK_SETUP.md`

Issues: https://github.com/allenxuejian/app-radar-agent/issues
