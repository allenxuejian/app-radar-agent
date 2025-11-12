import requests, json, time, os

def fetch_appstore_data(app_name):
    url = f"https://itunes.apple.com/search?term={app_name}&entity=software"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json().get("results", [])
        if data:
            item = data[0]
            return {
                "trackName": item.get("trackName"),
                "sellerName": item.get("sellerName"),
                "averageUserRating": item.get("averageUserRating"),
                "userRatingCount": item.get("userRatingCount"),
                "trackViewUrl": item.get("trackViewUrl"),
                "genres": item.get("genres"),
                "version": item.get("version")
            }
    return {}

def main():
    import yaml
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    results = []
    for t in cfg["targets"]:
        data = fetch_appstore_data(t["app"])
        print(f"Fetched: {t['app']} -> {data.get('averageUserRating')} stars")
        results.append({"app": t["app"], "store_data": data})
        time.sleep(1)
    os.makedirs("./data/results", exist_ok=True)
    with open("./data/results/raw_data.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
