import json, os
from datetime import datetime

def analyze(data):
    lines = []
    lines.append(f"# 📊 AppRadar 报告（{datetime.now().strftime('%Y-%m-%d')}）\n")
    lines.append("| App | Rating | Reviews | 公司 | 类别 | 可抄点 |")
    lines.append("|-----|---------|----------|------|--------|--------|")
    for item in data:
        d = item["store_data"]
        rating = d.get("averageUserRating", "-")
        reviews = d.get("userRatingCount", "-")
        seller = d.get("sellerName", "-")
        genre = ", ".join(d.get("genres", [])) if d.get("genres") else "-"
        lines.append(f"| {item['app']} | {rating} | {reviews} | {seller} | {genre} | 高评分产品逻辑值得研究 |")
    return "\n".join(lines)

def main():
    with open("./data/results/raw_data.json") as f:
        data = json.load(f)
    report = analyze(data)
    os.makedirs("./data/results", exist_ok=True)
    with open("./data/results/appradar_report.md", "w") as f:
        f.write(report)
    print("✅ Report generated at ./data/results/appradar_report.md")

if __name__ == "__main__":
    main()
