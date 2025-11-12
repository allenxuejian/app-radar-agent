"""
App Radar Agent - CLI 入口
命令行界面，支持数据采集、分析、报告生成
"""
import sys
import time
from typing import List, Optional
from datetime import datetime

# 本地导入
from app_radar.config.settings import settings, ensure_directories
from app_radar.storage.database import init_db, get_db_session, App, Metric
from app_radar.data_sources.itunes import ITunesDataSource
from app_radar.reporting.slack import SlackReporter
from app_radar.reporting.charts import ChartGenerator


def print_banner():
    """打印欢迎信息"""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║   📱 App Radar Agent v2.0                ║
    ║   Commercial Intelligence Platform       ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)


def fetch_all_apps(target_apps: Optional[List[str]] = None) -> List[dict]:
    """
    采集所有目标应用数据

    Args:
        target_apps: 目标应用列表，如果为 None 则使用配置文件中的列表

    Returns:
        List[dict]: 应用数据列表
    """
    if target_apps is None:
        target_apps = settings.target_apps

    print(f"\n🔍 开始采集 {len(target_apps)} 款应用数据...\n")

    itunes = ITunesDataSource()
    db = get_db_session()
    apps_data = []

    for i, app_name in enumerate(target_apps, 1):
        print(f"[{i}/{len(target_apps)}] Fetching {app_name}...", end=" ")

        try:
            # 从 iTunes 获取数据
            result = itunes.fetch_with_retry(app_name)
            data = result.data

            # 保存到数据库
            app_record = db.query(App).filter_by(
                app_identifier=result.app_identifier
            ).first()

            if not app_record:
                # 创建新记录
                app_record = App(
                    app_identifier=result.app_identifier,
                    name=data['name'],
                    platform='ios',
                    developer=data['developer'],
                    category=data['category'],
                    url=data['url']
                )
                db.add(app_record)
                db.commit()
                db.refresh(app_record)

            # 添加指标记录
            metric = Metric(
                app_id=app_record.id,
                rating=data['rating'],
                rating_count=data['rating_count'],
                version=data['version'],
                source='itunes'
            )
            db.add(metric)
            db.commit()

            # 添加到结果列表
            apps_data.append(data)

            print(f"✅ {data['rating']:.1f}⭐ ({data['rating_count']:,} reviews)")

            # 遵守 API 限流
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    db.close()

    print(f"\n✅ 成功采集 {len(apps_data)}/{len(target_apps)} 款应用\n")
    return apps_data


def generate_charts(apps_data: List[dict]) -> List[str]:
    """
    生成数据可视化图表

    Args:
        apps_data: 应用数据列表

    Returns:
        List[str]: 生成的图表文件路径列表
    """
    print("📊 生成数据可视化图表...\n")

    generator = ChartGenerator(settings.charts_dir)
    chart_paths = []

    try:
        # 评分散点图
        path1 = generator.create_rating_scatter(apps_data)
        chart_paths.append(str(path1))

        # 增长趋势图
        path2 = generator.create_growth_trend(apps_data)
        chart_paths.append(str(path2))

        # 类别分布图
        path3 = generator.create_category_distribution(apps_data)
        chart_paths.append(str(path3))

        print(f"\n✅ 生成 {len(chart_paths)} 张图表\n")

    except Exception as e:
        print(f"⚠️  图表生成失败: {e}\n")

    return chart_paths


def send_to_slack(apps_data: List[dict], top_n: int = 10):
    """
    发送报告到 Slack

    Args:
        apps_data: 应用数据列表
        top_n: 展示前 N 个应用
    """
    if not settings.slack_webhook_url:
        print("⚠️  Slack Webhook URL 未配置，跳过推送")
        print("   请在 .env 文件中设置 SLACK_WEBHOOK_URL\n")
        return

    print(f"📤 发送报告到 Slack (TOP {top_n})...\n")

    reporter = SlackReporter(settings.slack_webhook_url)

    try:
        success = reporter.send_report(apps_data, top_n=top_n)
        if success:
            print("✅ Slack 报告发送成功\n")
        else:
            print("❌ Slack 报告发送失败\n")
    except Exception as e:
        print(f"❌ 发送失败: {e}\n")


def run_full_pipeline(top_n: int = 10, target_apps: Optional[List[str]] = None):
    """
    运行完整流程：采集 -> 分析 -> 图表 -> Slack

    Args:
        top_n: Slack 报告中展示的应用数量
        target_apps: 自定义目标应用列表
    """
    print_banner()

    # 确保目录存在
    ensure_directories()

    # 初始化数据库
    print("🗄️  初始化数据库...")
    init_db()
    print()

    # 采集数据
    apps_data = fetch_all_apps(target_apps)

    if not apps_data:
        print("❌ 没有采集到任何数据，退出")
        return

    # 生成图表
    generate_charts(apps_data)

    # 发送到 Slack
    send_to_slack(apps_data, top_n=top_n)

    print("=" * 50)
    print("🎉 全部完成！")
    print("=" * 50)


def main():
    """主函数 - CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='App Radar Agent - Commercial Intelligence Platform'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top apps to show in Slack report (default: 10)'
    )

    parser.add_argument(
        '--apps',
        type=str,
        help='Comma-separated list of app names to track (overrides config)'
    )

    parser.add_argument(
        '--skip-slack',
        action='store_true',
        help='Skip sending report to Slack'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: only fetch 3 apps'
    )

    args = parser.parse_args()

    # 解析自定义应用列表
    target_apps = None
    if args.apps:
        target_apps = [app.strip() for app in args.apps.split(',')]
    elif args.test:
        target_apps = ["Lemon8", "CapCut", "Notion"]  # 测试模式只采集 3 个

    # 运行完整流程
    try:
        run_full_pipeline(top_n=args.top, target_apps=target_apps)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断，退出")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
