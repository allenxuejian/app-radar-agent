"""
App Radar Agent - iTunes Search API 数据源
官方 API: https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/
"""
import requests
from datetime import datetime
from typing import Dict, Any
from .base import BaseDataSource, DataSourceResult


class ITunesDataSource(BaseDataSource):
    """iTunes Search API 数据源实现"""

    API_URL = "https://itunes.apple.com/search"

    def fetch(self, app_name: str) -> DataSourceResult:
        """
        从 iTunes Search API 获取应用数据

        Args:
            app_name: 应用名称

        Returns:
            DataSourceResult: 包含应用数据的结果对象
        """
        params = {
            "term": app_name,
            "entity": "software",
            "limit": 1,  # 只获取最相关的结果
            "country": "US"
        }

        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get('results') or len(data['results']) == 0:
                raise ValueError(f"App not found: {app_name}")

            app = data['results'][0]

            return DataSourceResult(
                source="itunes",
                app_identifier=str(app.get('trackId', '')),
                timestamp=datetime.utcnow(),
                data={
                    'trackId': app.get('trackId'),
                    'name': app.get('trackName', ''),
                    'developer': app.get('sellerName', app.get('artistName', '')),
                    'rating': app.get('averageUserRating'),
                    'rating_count': app.get('userRatingCount', 0),
                    'version': app.get('version', ''),
                    'genres': app.get('genres', []),
                    'category': app.get('primaryGenreName', ''),
                    'url': app.get('trackViewUrl', ''),
                    'description': app.get('description', ''),
                    'price': app.get('price', 0),
                    'currency': app.get('currency', 'USD'),
                    'releaseDate': app.get('releaseDate', ''),
                    'currentVersionReleaseDate': app.get('currentVersionReleaseDate', ''),
                    'fileSizeBytes': app.get('fileSizeBytes'),
                    'contentAdvisoryRating': app.get('contentAdvisoryRating', ''),
                },
                metadata={
                    'search_term': app_name,
                    'result_count': data.get('resultCount', 0)
                }
            )

        except requests.exceptions.RequestException as e:
            raise Exception(f"iTunes API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse iTunes API response: {e}")


def test_itunes_fetch():
    """测试 iTunes 数据源"""
    source = ITunesDataSource()

    test_apps = ["Lemon8", "CapCut", "Notion", "Duolingo", "Canva"]

    print("🧪 Testing iTunes Data Source\n")
    for app_name in test_apps:
        try:
            result = source.fetch_with_retry(app_name)
            print(f"✅ {app_name}:")
            print(f"   Name: {result.data['name']}")
            print(f"   Developer: {result.data['developer']}")
            print(f"   Rating: {result.data['rating']} ({result.data['rating_count']:,} reviews)")
            print(f"   Category: {result.data['category']}")
            print()
        except Exception as e:
            print(f"❌ {app_name}: {e}\n")


if __name__ == "__main__":
    test_itunes_fetch()
