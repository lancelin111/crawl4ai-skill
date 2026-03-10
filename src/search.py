"""搜索模块 - 提供 DuckDuckGo 网页搜索

这个模块封装了 DuckDuckGo 搜索功能，提供简洁的 API 用于网页搜索。
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional
import logging

# 兼容新旧包名
try:
    from ddgs import DDGS
    from ddgs.exceptions import DDGSException as DuckDuckGoSearchException
except ImportError:
    from duckduckgo_search import DDGS
    from duckduckgo_search.exceptions import DuckDuckGoSearchException

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """搜索相关错误的基类"""

    pass


class EmptyQueryError(SearchError):
    """空查询错误"""

    pass


class SearchNetworkError(SearchError):
    """网络错误"""

    pass


class RateLimitError(SearchError):
    """限流错误"""

    pass


@dataclass
class SearchResult:
    """搜索结果数据结构

    Attributes:
        title: 结果标题
        url: 结果 URL
        snippet: 结果摘要
        timestamp: 搜索时间戳 (ISO 格式)
    """

    title: str
    url: str
    snippet: str
    timestamp: str

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


class DuckDuckGoSearcher:
    """DuckDuckGo 搜索器

    使用 DuckDuckGo 进行网页搜索，无需 API key。

    Example:
        >>> searcher = DuckDuckGoSearcher()
        >>> results = searcher.search("python web scraping", num_results=5)
        >>> for r in results:
        ...     print(f"{r.title}: {r.url}")
    """

    def __init__(self, timeout: int = 10):
        """初始化搜索器

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self._ddgs: Optional[DDGS] = None

    @property
    def ddgs(self) -> DDGS:
        """懒加载 DDGS 实例"""
        if self._ddgs is None:
            try:
                self._ddgs = DDGS(timeout=self.timeout)
            except TypeError:
                # 新版 ddgs 包可能不支持 timeout 参数
                self._ddgs = DDGS()
        return self._ddgs

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量 (1-100)

        Returns:
            搜索结果列表

        Raises:
            EmptyQueryError: 查询为空
            SearchNetworkError: 网络请求失败
            SearchError: 其他搜索错误
        """
        # 验证查询
        if not query or not query.strip():
            raise EmptyQueryError("搜索查询不能为空")

        query = query.strip()

        # 限制结果数量
        num_results = max(1, min(100, num_results))

        try:
            logger.info(f"搜索: '{query}', 期望结果数: {num_results}")

            # 执行搜索
            results = self.ddgs.text(
                query,
                max_results=num_results,
                safesearch="moderate",
            )

            # 获取当前时间戳
            timestamp = datetime.now(timezone.utc).isoformat()

            # 转换为 SearchResult 对象
            search_results = []
            for r in results:
                result = SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                    timestamp=timestamp,
                )
                search_results.append(result)

            logger.info(f"搜索完成，返回 {len(search_results)} 条结果")
            return search_results

        except DuckDuckGoSearchException as e:
            logger.error(f"DuckDuckGo 搜索失败: {e}")
            raise SearchNetworkError(f"搜索请求失败: {e}") from e
        except Exception as e:
            logger.error(f"搜索时发生未知错误: {e}")
            raise SearchError(f"搜索失败: {e}") from e

    def search_news(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """搜索新闻

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            新闻搜索结果列表
        """
        if not query or not query.strip():
            raise EmptyQueryError("搜索查询不能为空")

        query = query.strip()
        num_results = max(1, min(100, num_results))

        try:
            logger.info(f"搜索新闻: '{query}'")

            results = self.ddgs.news(query, max_results=num_results)
            timestamp = datetime.now(timezone.utc).isoformat()

            search_results = []
            for r in results:
                result = SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("body", ""),
                    timestamp=r.get("date", timestamp),
                )
                search_results.append(result)

            return search_results

        except DuckDuckGoSearchException as e:
            raise SearchNetworkError(f"新闻搜索请求失败: {e}") from e
        except Exception as e:
            raise SearchError(f"新闻搜索失败: {e}") from e
