"""搜索模块单元测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, "/Users/lancelin/.openclaw/workspace-crawler/crawl4ai-skill")

from src.search import (
    DuckDuckGoSearcher,
    SearchResult,
    SearchError,
    EmptyQueryError,
    SearchNetworkError,
    RateLimitError,
)


class TestSearchResult:
    """SearchResult 数据类测试"""

    def test_create_search_result(self):
        """测试创建搜索结果"""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            timestamp="2026-03-10T00:00:00+00:00",
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.timestamp == "2026-03-10T00:00:00+00:00"

    def test_to_dict(self):
        """测试转换为字典"""
        result = SearchResult(
            title="Test",
            url="https://test.com",
            snippet="Snippet",
            timestamp="2026-03-10T00:00:00+00:00",
        )
        d = result.to_dict()
        assert d["title"] == "Test"
        assert d["url"] == "https://test.com"
        assert d["snippet"] == "Snippet"


class TestDuckDuckGoSearcher:
    """DuckDuckGoSearcher 测试"""

    def test_init_default_timeout(self):
        """测试默认超时设置"""
        searcher = DuckDuckGoSearcher()
        assert searcher.timeout == 10

    def test_init_custom_timeout(self):
        """测试自定义超时"""
        searcher = DuckDuckGoSearcher(timeout=30)
        assert searcher.timeout == 30

    def test_search_empty_query_raises_error(self):
        """测试空查询抛出错误"""
        searcher = DuckDuckGoSearcher()
        with pytest.raises(EmptyQueryError):
            searcher.search("")

    def test_search_whitespace_query_raises_error(self):
        """测试空白查询抛出错误"""
        searcher = DuckDuckGoSearcher()
        with pytest.raises(EmptyQueryError):
            searcher.search("   ")

    def test_search_none_query_raises_error(self):
        """测试 None 查询抛出错误"""
        searcher = DuckDuckGoSearcher()
        with pytest.raises(EmptyQueryError):
            searcher.search(None)

    @patch.object(DuckDuckGoSearcher, "ddgs", new_callable=lambda: MagicMock())
    def test_search_success(self, mock_ddgs):
        """测试成功搜索"""
        # 模拟搜索结果
        mock_ddgs.text.return_value = [
            {
                "title": "Python Tutorial",
                "href": "https://python.org/tutorial",
                "body": "Learn Python programming",
            },
            {
                "title": "Python Docs",
                "href": "https://docs.python.org",
                "body": "Official Python documentation",
            },
        ]

        searcher = DuckDuckGoSearcher()
        searcher._ddgs = mock_ddgs

        results = searcher.search("python", num_results=2)

        assert len(results) == 2
        assert results[0].title == "Python Tutorial"
        assert results[0].url == "https://python.org/tutorial"
        assert results[1].title == "Python Docs"

    @patch.object(DuckDuckGoSearcher, "ddgs", new_callable=lambda: MagicMock())
    def test_search_num_results_limit(self, mock_ddgs):
        """测试结果数量限制"""
        mock_ddgs.text.return_value = []

        searcher = DuckDuckGoSearcher()
        searcher._ddgs = mock_ddgs

        # 测试最小值限制
        searcher.search("test", num_results=0)
        mock_ddgs.text.assert_called_with("test", max_results=1, safesearch="moderate")

        # 测试最大值限制
        searcher.search("test", num_results=200)
        mock_ddgs.text.assert_called_with(
            "test", max_results=100, safesearch="moderate"
        )

    @patch.object(DuckDuckGoSearcher, "ddgs", new_callable=lambda: MagicMock())
    def test_search_strips_query(self, mock_ddgs):
        """测试查询去除空白"""
        mock_ddgs.text.return_value = []

        searcher = DuckDuckGoSearcher()
        searcher._ddgs = mock_ddgs

        searcher.search("  python  ", num_results=5)
        mock_ddgs.text.assert_called_with(
            "python", max_results=5, safesearch="moderate"
        )

    def test_search_news_empty_query_raises_error(self):
        """测试新闻搜索空查询抛出错误"""
        searcher = DuckDuckGoSearcher()
        with pytest.raises(EmptyQueryError):
            searcher.search_news("")

    @patch.object(DuckDuckGoSearcher, "ddgs", new_callable=lambda: MagicMock())
    def test_search_news_success(self, mock_ddgs):
        """测试新闻搜索成功"""
        mock_ddgs.news.return_value = [
            {
                "title": "Breaking News",
                "url": "https://news.com/article",
                "body": "News content",
                "date": "2026-03-10",
            }
        ]

        searcher = DuckDuckGoSearcher()
        searcher._ddgs = mock_ddgs

        results = searcher.search_news("technology", num_results=1)

        assert len(results) == 1
        assert results[0].title == "Breaking News"
        assert results[0].url == "https://news.com/article"


class TestSearchExceptions:
    """搜索异常测试"""

    def test_search_error_base_class(self):
        """测试基础异常类"""
        error = SearchError("test error")
        assert str(error) == "test error"
        assert isinstance(error, Exception)

    def test_empty_query_error(self):
        """测试空查询异常"""
        error = EmptyQueryError("empty query")
        assert isinstance(error, SearchError)

    def test_network_error(self):
        """测试网络异常"""
        error = SearchNetworkError("network failed")
        assert isinstance(error, SearchError)

    def test_rate_limit_error(self):
        """测试限流异常"""
        error = RateLimitError("rate limited")
        assert str(error) == "rate limited"
        assert isinstance(error, SearchError)


# Integration test (requires network) - marked for optional execution
@pytest.mark.integration
class TestSearchIntegration:
    """集成测试（需要网络）"""

    def test_real_search(self):
        """测试真实搜索 - 需要网络连接"""
        searcher = DuckDuckGoSearcher()
        results = searcher.search("python programming language", num_results=3)

        assert len(results) > 0
        assert all(r.url for r in results)
        assert all(r.title for r in results)
