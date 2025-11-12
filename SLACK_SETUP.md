# Slack 集成配置指南

## 步骤 1: 创建 Slack Incoming Webhook

### 1.1 访问 Slack App 管理页面

1. 打开浏览器访问: https://api.slack.com/apps
2. 点击 **"Create New App"** 按钮
3. 选择 **"From scratch"**

### 1.2 创建应用

1. **App Name**: 输入 `App Radar Agent`
2. **Pick a workspace**: 选择你要发送消息的工作区
3. 点击 **"Create App"**

### 1.3 添加 Incoming Webhooks

1. 在左侧菜单中找到 **"Incoming Webhooks"**
2. 将开关切换到 **"On"**
3. 滚动到页面底部，点击 **"Add New Webhook to Workspace"**
4. 选择要发送消息的频道（例如: #app-research, #product-insights）
5. 点击 **"Allow"** 授权

### 1.4 复制 Webhook URL

1. 页面会显示你的 Webhook URL，格式类似：
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```
2. 点击 **"Copy"** 复制这个 URL
3. **重要**: 保密这个 URL，不要公开分享

## 步骤 2: 配置 App Radar Agent

### 2.1 保存 Webhook URL

在终端运行以下命令（替换为你的实际 URL）:

```bash
# 创建配置文件
mkdir -p ~/.claude/agents/app-radar-agent-data

# 保存 Webhook URL
echo "YOUR_WEBHOOK_URL_HERE" > ~/.claude/agents/app-radar-agent-data/.slack_webhook
chmod 600 ~/.claude/agents/app-radar-agent-data/.slack_webhook
```

**示例**:
```bash
echo "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX" > ~/.claude/agents/app-radar-agent-data/.slack_webhook
```

### 2.2 测试发送

运行测试脚本验证配置:

```bash
cd ~/github/app-radar-agent
python3 scripts/send_to_slack.py --test
```

如果配置正确，你会在 Slack 频道看到测试消息。

## 步骤 3: 设置定时任务

### 3.1 每 8 小时自动发送

运行安装脚本:

```bash
cd ~/github/app-radar-agent
./scripts/setup_cron.sh
```

这会设置以下定时任务:
- 每天 8:00 AM 发送
- 每天 4:00 PM 发送
- 每天 12:00 AM 发送

### 3.2 自定义发送时间

编辑 crontab:

```bash
crontab -e
```

添加或修改以下行:

```bash
# 每 8 小时发送一次（0:00, 8:00, 16:00）
0 */8 * * * cd ~/.claude/agents/app-radar-agent-data && python3 scripts/send_to_slack.py >> /tmp/app-radar-slack.log 2>&1

# 或指定具体时间
0 9 * * * cd ~/.claude/agents/app-radar-agent-data && python3 scripts/send_to_slack.py  # 每天 9:00 AM
0 17 * * * cd ~/.claude/agents/app-radar-agent-data && python3 scripts/send_to_slack.py  # 每天 5:00 PM
```

## Cron 时间格式说明

```
* * * * * 命令
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0 和 7 都代表星期日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

**常用示例**:
```bash
0 */8 * * *    # 每 8 小时（0:00, 8:00, 16:00）
0 9,17 * * *   # 每天 9:00 和 17:00
*/30 * * * *   # 每 30 分钟
0 0 * * 1      # 每周一午夜
```

## 步骤 4: 验证和监控

### 4.1 查看定时任务

```bash
crontab -l
```

### 4.2 查看发送日志

```bash
tail -f /tmp/app-radar-slack.log
```

### 4.3 手动触发发送

```bash
cd ~/github/app-radar-agent
python3 scripts/send_to_slack.py
```

## 消息格式定制

编辑 `scripts/send_to_slack.py` 可以自定义:
- 消息标题和样式
- 包含的数据字段
- 图表和可视化
- @提醒特定用户

## 故障排查

### 问题 1: Webhook URL 无效

**症状**: 发送失败，返回 404 错误

**解决**:
- 检查 URL 是否完整复制
- 确认 Slack App 未被删除
- 重新生成 Webhook URL

### 问题 2: 定时任务未执行

**症状**: 到了时间没有收到消息

**解决**:
```bash
# 检查 cron 服务是否运行
sudo launchctl list | grep cron  # macOS
service cron status              # Linux

# 检查日志
tail -50 /tmp/app-radar-slack.log

# 检查脚本权限
chmod +x ~/github/app-radar-agent/scripts/send_to_slack.py
```

### 问题 3: Python 依赖缺失

**症状**: 脚本执行失败

**解决**:
```bash
pip3 install requests pyyaml
```

## 高级配置

### 发送到多个频道

创建多个 Webhook 并在脚本中配置:

```python
WEBHOOKS = [
    "https://hooks.slack.com/services/T00/B00/XXX",  # #product
    "https://hooks.slack.com/services/T00/B00/YYY",  # #engineering
]
```

### 添加条件触发

只在评分变化或有重要更新时发送:

```python
if should_send_alert(new_data, old_data):
    send_to_slack()
```

### 集成图表

使用 Slack Block Kit 添加可视化:
- 评分趋势图
- 评论数对比
- 排行榜

## 安全建议

1. ✅ 不要将 Webhook URL 提交到 Git
2. ✅ 使用环境变量或配置文件存储
3. ✅ 设置文件权限 `chmod 600`
4. ✅ 定期轮换 Webhook URL
5. ✅ 监控异常发送行为

## 成本说明

- Slack Incoming Webhooks: **完全免费**
- 无消息数量限制
- 无需付费订阅

## 支持

如有问题，请查看:
- Slack API 文档: https://api.slack.com/messaging/webhooks
- App Radar Agent Issues: https://github.com/allenxuejian/app-radar-agent/issues
