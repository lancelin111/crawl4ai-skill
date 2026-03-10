"""爬取模块单元测试"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio

import sys
sys.path.insert(0, "/Users/lancelin/.openclaw/workspace-crawler/crawl4ai-skill")

from src.crawler import (
    SmartCrawler,
    CrawlResult,
    CrawlError,
    CrawlTimeoutError,
    CrawlNetworkError,
    InvalidURLError,
    HTTPError,
    validate_url,
)


class TestCrawlResult:
    """CrawlResult 数据类测试"""

    def test_create_crawl_result(self):
        """测试创建爬取结果"""
        result = CrawlResult(
            url="https://example.com",
            title="Example",
            markdown="# Example",
            links=["https://example.com/page1"],
            status="success",
        )
        assert result.url == "https://example.com"
        assert result.title == "Example"
        assert result.markdown == "# Example"
        assert result.status == "success"
        assert result.error is None

    def test_create_failed_result(self):
        """测试创建失败结果"""
        result = CrawlResult(
            url="https://example.com",
            title="",
            markdown="",
            status="failed",
            error="Connection refused",
        )
        assert result.status == "failed"
        assert result.error == "Connection refused"

    def test_to_dict(self):
        """测试转换为字典"""
        result = CrawlResult(
            url="https://example.com",
            title="Test",
            markdown="Content",
        )
        d = result.to_dict()
        assert d["url"] == "https://example.com"
        assert d["title"] == "Test"
        assert d["markdown"] == "Content"
        assert "crawled_at" in d


class TestSmartCrawler:
    """SmartCrawler 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        crawler = SmartCrawler()
        assert crawler.verbose is False

    def test_init_verbose(self):
        """测试启用详细日志"""
        crawler = SmartCrawler(verbose=True)
        assert crawler.verbose is True

    def test_detect_strategy_sitemap(self):
        """测试检测 sitemap 策略"""
        crawler = SmartCrawler()
        assert crawler._detect_strategy("https://example.com/sitemap.xml") == "sitemap"
        assert crawler._detect_strategy("https://example.com/SITEMAP.xml") == "sitemap"

    def test_detect_strategy_txt(self):
        """测试检测 txt 策略"""
        crawler = SmartCrawler()
        assert crawler._detect_strategy("https://example.com/llms-full.txt") == "txt"
        assert crawler._detect_strategy("https://example.com/llms.txt") == "txt"

    def test_detect_strategy_recursive(self):
        """测试检测递归策略"""
        crawler = SmartCrawler()
        assert crawler._detect_strategy("https://example.com") == "recursive"
        assert crawler._detect_strategy("https://example.com/docs") == "recursive"


class TestCrawlExceptions:
    """爬取异常测试"""

    def test_crawl_error_base_class(self):
        """测试基础异常类"""
        error = CrawlError("test error")
        assert str(error) == "test error"
        assert isinstance(error, Exception)

    def test_timeout_error(self):
        """测试超时异常"""
        error = CrawlTimeoutError("timeout")
        assert isinstance(error, CrawlError)

    def test_network_error(self):
        """测试网络异常"""
        error = CrawlNetworkError("network failed")
        assert isinstance(error, CrawlError)

    def test_invalid_url_error(self):
        """测试无效 URL 异常"""
        error = InvalidURLError("invalid url")
        assert str(error) == "invalid url"
        assert isinstance(error, CrawlError)

    def test_http_error(self):
        """测试 HTTP 异常"""
        error = HTTPError("not found", status_code=404)
        assert str(error) == "not found"
        assert error.status_code == 404
        assert isinstance(error, CrawlError)

    def test_http_error_without_status_code(self):
        """测试 HTTP 异常（无状态码）"""
        error = HTTPError("error")
        assert error.status_code is None


class TestValidateUrl:
    """URL 验证函数测试"""

    def test_validate_url_valid(self):
        """测试有效 URL"""
        validate_url("https://example.com")
        validate_url("http://example.com/path")
        validate_url("https://example.com:8080/path?query=1")

    def test_validate_url_empty(self):
        """测试空 URL"""
        with pytest.raises(InvalidURLError) as exc_info:
            validate_url("")
        assert "不能为空" in str(exc_info.value)

    def test_validate_url_none(self):
        """测试 None URL"""
        with pytest.raises(InvalidURLError) as exc_info:
            validate_url(None)
        assert "不能为空" in str(exc_info.value)

    def test_validate_url_whitespace(self):
        """测试空白 URL"""
        with pytest.raises(InvalidURLError) as exc_info:
            validate_url("   ")
        assert "不能为空" in str(exc_info.value)

    def test_validate_url_invalid_scheme(self):
        """测试无效协议"""
        with pytest.raises(InvalidURLError) as exc_info:
            validate_url("ftp://example.com")
        assert "不支持的协议" in str(exc_info.value)

    def test_validate_url_no_host(self):
        """测试无主机名"""
        with pytest.raises(InvalidURLError) as exc_info:
            validate_url("https://")
        assert "无效的 URL" in str(exc_info.value)


@pytest.mark.asyncio
class TestSmartCrawlerAsync:
    """SmartCrawler 异步测试"""

    async def test_crawl_page_without_crawl4ai(self):
        """测试未安装 crawl4ai 时的错误处理"""
        crawler = SmartCrawler()

        # 模拟 crawl4ai 未安装
        with patch.dict('sys.modules', {'crawl4ai': None}):
            with pytest.raises(CrawlError) as exc_info:
                await crawler.crawl_page("https://example.com")
            # 检查错误消息或只检查异常类型
            assert isinstance(exc_info.value, CrawlError)

    async def test_crawl_site_auto_strategy(self):
        """测试自动策略选择"""
        crawler = SmartCrawler()

        # 模拟 _crawl_recursive 方法
        crawler._crawl_recursive = AsyncMock(return_value=[])

        await crawler.crawl_site(
            "https://example.com",
            strategy="auto",
            max_pages=5,
        )

        crawler._crawl_recursive.assert_called_once()

    async def test_crawl_site_sitemap_strategy(self):
        """测试 sitemap 策略"""
        crawler = SmartCrawler()

        crawler._crawl_from_sitemap = AsyncMock(return_value=[])

        await crawler.crawl_site(
            "https://example.com/sitemap.xml",
            strategy="sitemap",
            max_pages=5,
        )

        crawler._crawl_from_sitemap.assert_called_once()


# Integration tests (require network and crawl4ai)
@pytest.mark.integration
@pytest.mark.asyncio
class TestCrawlerIntegration:
    """集成测试（需要网络和 crawl4ai）"""

    async def test_crawl_example_com(self):
        """测试爬取 example.com"""
        crawler = SmartCrawler()
        result = await crawler.crawl_page("https://example.com")

        assert result.status == "success"
        assert result.title
        assert result.markdown
        assert "Example" in result.title or "Example" in result.markdown
