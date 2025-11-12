"""
App Radar Agent - 图表生成模块
使用 matplotlib 生成数据可视化图表
"""
import matplotlib.pyplot as plt
import matplotlib
from typing import List, Dict
from pathlib import Path

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class ChartGenerator:
    """图表生成器"""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置样式
        plt.style.use('seaborn-v0_8-darkgrid')

    def create_rating_scatter(self, apps: List[Dict], filename: str = "rating_scatter.png") -> Path:
        """
        创建评分 vs 评论数散点图

        Args:
            apps: 应用数据列表
            filename: 输出文件名

        Returns:
            Path: 生成的图片路径
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        # 提取数据
        x = [app['rating'] for app in apps if app.get('rating')]
        y = [app['rating_count'] / 1000 for app in apps if app.get('rating_count')]  # 转换为 K
        labels = [app['name'] for app in apps if app.get('rating')]
        colors = ['#007A5A' if app['rating'] >= 4.7 else '#1264A3' for app in apps if app.get('rating')]

        # 绘制散点
        scatter = ax.scatter(x, y, s=200, alpha=0.6, c=colors, edgecolors='white', linewidth=2)

        # 添加标签
        for i, label in enumerate(labels):
            if i < len(x):
                ax.annotate(label, (x[i], y[i]),
                           xytext=(8, 8), textcoords='offset points',
                           fontsize=9, alpha=0.8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        # 设置标签和标题
        ax.set_xlabel('Average Rating', fontsize=12, fontweight='bold')
        ax.set_ylabel('Review Count (K)', fontsize=12, fontweight='bold')
        ax.set_title('App Rating vs User Engagement', fontsize=14, fontweight='bold', pad=20)

        # 设置网格
        ax.grid(True, alpha=0.3, linestyle='--')

        # 设置背景
        ax.set_facecolor('#F8F8F8')
        fig.patch.set_facecolor('white')

        # 保存
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Chart saved: {output_path}")
        return output_path

    def create_growth_trend(self, apps: List[Dict], filename: str = "growth_trend.png") -> Path:
        """
        创建增长趋势图

        Args:
            apps: 应用数据列表（需要包含历史数据）
            filename: 输出文件名

        Returns:
            Path: 生成的图片路径
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # 模拟 7 天数据（实际应从数据库获取）
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # TOP 3 应用的趋势
        top_apps = sorted(apps, key=lambda x: x.get('rating_count', 0), reverse=True)[:3]
        colors = ['#007A5A', '#1264A3', '#ECB22E']

        for i, app in enumerate(top_apps):
            # 模拟增长数据
            base = app.get('rating_count', 1000) / 1000  # K
            growth = [base * (1 + j * 0.02) for j in range(7)]  # 2% daily growth

            ax.plot(days, growth, marker='o', linewidth=2.5,
                   label=app['name'], color=colors[i], markersize=8)

        ax.set_xlabel('Day of Week', fontsize=12, fontweight='bold')
        ax.set_ylabel('Review Count (K)', fontsize=12, fontweight='bold')
        ax.set_title('7-Day Growth Trend (Top 3 Apps)', fontsize=14, fontweight='bold', pad=20)

        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#F8F8F8')
        fig.patch.set_facecolor('white')

        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Chart saved: {output_path}")
        return output_path

    def create_category_distribution(self, apps: List[Dict], filename: str = "category_dist.png") -> Path:
        """创建类别分布饼图"""
        fig, ax = plt.subplots(figsize=(10, 8))

        # 统计类别
        categories = {}
        for app in apps:
            cat = app.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        # 绘制饼图
        colors = plt.cm.Set3(range(len(categories)))
        wedges, texts, autotexts = ax.pie(
            categories.values(),
            labels=categories.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10}
        )

        ax.set_title('App Category Distribution', fontsize=14, fontweight='bold', pad=20)

        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Chart saved: {output_path}")
        return output_path
