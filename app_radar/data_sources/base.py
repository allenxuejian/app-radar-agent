"""
App Radar Agent - 数据源基类
定义统一的数据源接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class DataSourceResult(BaseModel):
    """统一的数据源返回格式"""
    source: str
    app_identifier: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class BaseDataSource(ABC):
    """数据源抽象基类"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    @abstractmethod
    def fetch(self, app_identifier: str) -> DataSourceResult:
        """
        获取应用数据的抽象方法

        Args:
            app_identifier: 应用标识符（名称、bundle_id 等）

        Returns:
            DataSourceResult: 统一格式的数据源结果
        """
        pass

    def fetch_with_retry(self, app_identifier: str, max_retries: int = 3) -> DataSourceResult:
        """
        带重试的数据获取

        Args:
            app_identifier: 应用标识符
            max_retries: 最大重试次数

        Returns:
            DataSourceResult: 数据源结果
        """
        import time

        last_error = None
        for attempt in range(max_retries):
            try:
                return self.fetch(app_identifier)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        raise last_error if last_error else Exception("Unknown error")
