"""爬取模块 - 基于 crawl4ai 的网页爬取

提供单页爬取和全站爬取功能，支持多种 Markdown 输出格式。
"""

import asyncio
import random
try:
    import defusedxml.ElementTree as ET
except ImportError:
    # Fallback to standard library with manual sanitization
    import xml.etree.ElementTree as ET
    import warnings
    warnings.warn("defusedxml not installed, using xml.etree.ElementTree (less secure)")
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Set, Dict, Any
from urllib.parse import urljoin, urlparse
import logging
import re

logger = logging.getLogger(__name__)


def _validate_url_scheme(url: str) -> None:
    """验证 URL 只允许 http/https 协议
    
    Args:
        url: 要验证的 URL
        
    Raises:
        ValueError: 如果 URL 使用了不安全的协议（如 file://）
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"不安全的 URL 协议: {parsed.scheme}。只允许 http 和 https。")


class CrawlError(Exception):
    """爬取相关错误的基类"""
    pass


class CrawlTimeoutError(CrawlError):
    """超时错误"""
    pass


class CrawlNetworkError(CrawlError):
    """网络错误"""
    pass


class InvalidURLError(CrawlError):
    """无效 URL 错误"""
    pass


class HTTPError(CrawlError):
    """HTTP 错误"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


def validate_url(url: str) -> None:
    """验证 URL 是否有效

    Args:
        url: 待验证的 URL

    Raises:
        InvalidURLError: URL 无效
    """
    if not url or not url.strip():
        raise InvalidURLError("URL 不能为空")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ('http', 'https'):
        raise InvalidURLError(f"不支持的协议: {parsed.scheme}，只支持 http/https")

    if not parsed.netloc:
        raise InvalidURLError(f"无效的 URL: {url}")


@dataclass
class CrawlResult:
    """爬取结果数据结构

    Attributes:
        url: 爬取的 URL
        title: 页面标题
        markdown: Markdown 内容
        links: 页面中的链接
        status: 爬取状态 (success/failed)
        error: 错误信息（如果失败）
        depth: 爬取深度
        crawled_at: 爬取时间
    """

    url: str
    title: str
    markdown: str
    links: List[str] = field(default_factory=list)
    status: str = "success"
    error: Optional[str] = None
    depth: int = 0
    crawled_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "url": self.url,
            "title": self.title,
            "markdown": self.markdown,
            "links": self.links,
            "status": self.status,
            "error": self.error,
            "depth": self.depth,
            "crawled_at": self.crawled_at,
        }


class SmartCrawler:
    """智能爬虫

    基于 crawl4ai 提供单页和全站爬取功能。

    Example:
        >>> crawler = SmartCrawler()
        >>> result = await crawler.crawl_page("https://example.com")
        >>> print(result.markdown)
    """

    def __init__(self, verbose: bool = False):
        """初始化爬虫

        Args:
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    async def crawl_page(
        self,
        url: str,
        format: str = "fit_markdown",
        wait_for: Optional[str] = None,
        timeout: int = 30,
        wait_until: str = "domcontentloaded",
        delay_before_return_html: float = 0.1,
    ) -> CrawlResult:
        """爬取单个页面

        Args:
            url: 目标 URL
            format: 输出格式 (fit_markdown/markdown_with_citations/raw_markdown)
            wait_for: 等待元素加载（CSS selector）
            timeout: 超时时间（秒）
            wait_until: 等待策略 (domcontentloaded/networkidle/load/commit)
            delay_before_return_html: 返回 HTML 前的额外延迟（秒），用于等待 JS 执行

        Returns:
            爬取结果

        Raises:
            CrawlTimeoutError: 超时
            CrawlNetworkError: 网络错误
            CrawlError: 其他爬取错误
        """
        try:
            from crawl4ai import AsyncWebCrawler
            from crawl4ai.async_configs import CrawlerRunConfig
        except ImportError:
            raise CrawlError("crawl4ai 未安装，请运行: pip install crawl4ai && crawl4ai-setup")

        # 验证 URL
        validate_url(url)

        try:
            logger.info(f"开始爬取: {url}")

            # 创建配置对象
            config = CrawlerRunConfig(
                wait_for=wait_for if wait_for else None,
                wait_until=wait_until,
                page_timeout=timeout * 1000,  # 转换为毫秒
                delay_before_return_html=delay_before_return_html,
            )

            async with AsyncWebCrawler(verbose=self.verbose) as crawler:
                result_container = await crawler.arun(
                    url=url,
                    config=config,
                )

                if not result_container.success:
                    error_msg = "Unknown error"
                    if hasattr(result_container, 'error_message'):
                        error_msg = result_container.error_message or error_msg
                    return CrawlResult(
                        url=url,
                        title="",
                        markdown="",
                        links=[],
                        status="failed",
                        error=error_msg,
                    )

                # crawl4ai 0.8.0: 结果是 CrawlResultContainer，需要获取第一个结果
                first_result = result_container[0] if hasattr(result_container, '__getitem__') else result_container

                # 获取标题 - 从 metadata 中获取
                title = ""
                if hasattr(first_result, 'metadata') and first_result.metadata:
                    title = first_result.metadata.get('title', '') or ""

                # 根据 format 选择输出格式
                # crawl4ai 0.8.0: 简化处理，直接使用 markdown 字符串
                markdown_str = str(result_container.markdown) if result_container.markdown else ""

                if format == "fit_markdown":
                    # 尝试获取 fit_markdown，如果不存在则使用原始 markdown
                    try:
                        fit_md = first_result.markdown.fit_markdown if hasattr(first_result.markdown, 'fit_markdown') else None
                        markdown = fit_md if fit_md else markdown_str
                    except (AttributeError, TypeError):
                        markdown = markdown_str
                elif format == "markdown_with_citations":
                    # 尝试获取带引用的 markdown
                    try:
                        if hasattr(first_result, 'markdown_v2') and first_result.markdown_v2:
                            citations_md = getattr(first_result.markdown_v2, 'markdown_with_citations', None)
                            markdown = citations_md if citations_md else markdown_str
                        else:
                            markdown = markdown_str
                    except (AttributeError, TypeError):
                        markdown = markdown_str
                else:
                    markdown = markdown_str

                # 提取链接
                links_dict = result_container.links if hasattr(result_container, 'links') else {}
                internal_links = links_dict.get("internal", []) if links_dict else []
                external_links = links_dict.get("external", []) if links_dict else []

                # 将链接对象转换为 URL 字符串
                all_links = []
                for link in internal_links:
                    if isinstance(link, dict):
                        all_links.append(link.get("href", ""))
                    else:
                        all_links.append(str(link))
                for link in external_links:
                    if isinstance(link, dict):
                        all_links.append(link.get("href", ""))
                    else:
                        all_links.append(str(link))

                logger.info(f"爬取完成: {url}, 标题: {title}")

                return CrawlResult(
                    url=url,
                    title=title,
                    markdown=markdown,
                    links=all_links,
                    status="success",
                )

        except asyncio.TimeoutError as e:
            logger.error(f"爬取超时: {url}")
            raise CrawlTimeoutError(f"爬取超时: {url}") from e
        except Exception as e:
            logger.error(f"爬取失败: {url}, 错误: {e}")
            raise CrawlError(f"爬取失败: {e}") from e

    async def crawl_site(
        self,
        start_url: str,
        max_depth: int = 2,
        max_pages: int = 50,
        include_external: bool = False,
        format: str = "fit_markdown",
        strategy: str = "auto",
    ) -> List[CrawlResult]:
        """爬取整个站点

        Args:
            start_url: 起始 URL
            max_depth: 最大爬取深度
            max_pages: 最大页面数量
            include_external: 是否包含外部链接
            format: 输出格式
            strategy: 爬取策略 (auto/sitemap/recursive)

        Returns:
            爬取结果列表
        """
        # 自动识别策略
        if strategy == "auto":
            strategy = self._detect_strategy(start_url)

        logger.info(f"开始全站爬取: {start_url}, 策略: {strategy}")

        # 根据策略执行爬取
        if strategy == "sitemap":
            return await self._crawl_from_sitemap(start_url, max_pages, format)
        elif strategy == "txt":
            return await self._crawl_from_txt(start_url, max_pages, format)
        else:
            return await self._crawl_recursive(
                start_url, max_depth, max_pages, include_external, format
            )

    def _detect_strategy(self, url: str) -> str:
        """检测爬取策略

        Args:
            url: URL

        Returns:
            策略名称
        """
        if url.endswith("sitemap.xml") or "sitemap" in url.lower():
            return "sitemap"
        elif url.endswith(".txt") and ("llms" in url.lower() or "links" in url.lower()):
            return "txt"
        else:
            return "recursive"

    async def _crawl_from_sitemap(
        self, sitemap_url: str, max_pages: int, format: str
    ) -> List[CrawlResult]:
        """从 sitemap.xml 爬取

        Args:
            sitemap_url: sitemap URL
            max_pages: 最大页面数
            format: 输出格式

        Returns:
            爬取结果列表
        """
        # 验证 URL
        validate_url(sitemap_url)

        try:
            import aiohttp
        except ImportError:
            import urllib.request
            import urllib.error
            # 使用同步请求作为回退
            try:
                # 验证 URL 协议安全性
                _validate_url_scheme(sitemap_url)
                with urllib.request.urlopen(sitemap_url, timeout=30) as response:  # nosec B310 - URL scheme validated
                    content = response.read().decode('utf-8')
            except urllib.error.HTTPError as e:
                raise HTTPError(f"获取 sitemap 失败: HTTP {e.code}", status_code=e.code)
            except urllib.error.URLError as e:
                raise CrawlNetworkError(f"获取 sitemap 失败: {e.reason}")
        else:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(sitemap_url) as response:
                        if response.status >= 400:
                            raise HTTPError(f"获取 sitemap 失败: HTTP {response.status}", status_code=response.status)
                        content = await response.text()
                except aiohttp.ClientError as e:
                    raise CrawlNetworkError(f"获取 sitemap 失败: {e}")

        # 解析 XML
        try:
            # Using defusedxml.ElementTree when available (fallback to xml.etree.ElementTree)
            root = ET.fromstring(content)  # nosec B314 - using defusedxml when available
            # 移除命名空间以简化解析
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]

            # 检查是否是 sitemap index（嵌套 sitemap）
            sitemap_locs = [loc.text for loc in root.findall('.//sitemap/loc') if loc.text]
            if sitemap_locs:
                logger.info(f"发现 sitemap index，包含 {len(sitemap_locs)} 个子 sitemap")
                # 递归获取所有子 sitemap 的 URL
                all_urls = []
                for sub_sitemap in sitemap_locs:
                    if len(all_urls) >= max_pages:
                        break
                    try:
                        sub_results = await self._crawl_from_sitemap(
                            sub_sitemap, max_pages - len(all_urls), format
                        )
                        # 只收集 URL，稍后统一爬取
                        for r in sub_results:
                            if len(all_urls) >= max_pages:
                                break
                            all_urls.append(r.url)
                    except Exception as e:
                        logger.warning(f"获取子 sitemap 失败: {sub_sitemap}, 错误: {e}")
                # 对于 sitemap index，直接返回已爬取的结果
                return sub_results if sub_results else []

            urls = [loc.text for loc in root.findall('.//loc') if loc.text]
        except ET.ParseError as e:
            logger.error(f"解析 sitemap 失败: {sitemap_url}")
            raise CrawlError(f"解析 sitemap XML 失败: {e}")

        if not urls:
            logger.warning(f"sitemap 中未发现任何 URL: {sitemap_url}")
            return []

        # 限制页面数量
        urls = urls[:max_pages]

        logger.info(f"从 sitemap 发现 {len(urls)} 个 URL")

        # 爬取所有 URL，添加延时
        results = []
        for i, url in enumerate(urls):
            try:
                result = await self.crawl_page(url, format=format)
                results.append(result)
            except Exception as e:
                logger.error(f"爬取失败: {url}, 错误: {e}")
                results.append(CrawlResult(
                    url=url,
                    title="",
                    markdown="",
                    status="failed",
                    error=str(e),
                ))

            if len(results) >= max_pages:
                break

            # 随机延迟 0.1~0.3 秒，模拟人类行为，避免触发速率限制
            await asyncio.sleep(random.uniform(0.1, 0.3))

        return results

    async def _crawl_from_txt(
        self, txt_url: str, max_pages: int, format: str
    ) -> List[CrawlResult]:
        """从 txt 文件爬取（llms-full.txt 等）

        Args:
            txt_url: txt 文件 URL
            max_pages: 最大页面数
            format: 输出格式

        Returns:
            爬取结果列表
        """
        # 验证 URL
        validate_url(txt_url)

        try:
            import aiohttp
        except ImportError:
            import urllib.request
            import urllib.error
            try:
                # 验证 URL 协议安全性
                _validate_url_scheme(txt_url)
                with urllib.request.urlopen(txt_url, timeout=30) as response:  # nosec B310 - URL scheme validated
                    content = response.read().decode('utf-8')
            except urllib.error.HTTPError as e:
                raise HTTPError(f"获取 txt 文件失败: HTTP {e.code}", status_code=e.code)
            except urllib.error.URLError as e:
                raise CrawlNetworkError(f"获取 txt 文件失败: {e.reason}")
        else:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(txt_url) as response:
                        if response.status >= 400:
                            raise HTTPError(f"获取 txt 文件失败: HTTP {response.status}", status_code=response.status)
                        content = await response.text()
                except aiohttp.ClientError as e:
                    raise CrawlNetworkError(f"获取 txt 文件失败: {e}")

        # 解析 URL（每行一个）
        urls = []
        for line in content.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith('http://') or line.startswith('https://')):
                urls.append(line)

        if not urls:
            logger.warning(f"txt 文件中未发现任何 URL: {txt_url}")
            return []

        urls = urls[:max_pages]
        logger.info(f"从 txt 文件发现 {len(urls)} 个 URL")

        # 爬取所有 URL，添加延时
        results = []
        for i, url in enumerate(urls):
            try:
                result = await self.crawl_page(url, format=format)
                results.append(result)
            except Exception as e:
                logger.error(f"爬取失败: {url}, 错误: {e}")
                results.append(CrawlResult(
                    url=url,
                    title="",
                    markdown="",
                    status="failed",
                    error=str(e),
                ))

            if len(results) >= max_pages:
                break

            # 随机延迟 0.1~0.3 秒，模拟人类行为，避免触发速率限制
            await asyncio.sleep(random.uniform(0.1, 0.3))

        return results

    async def _crawl_recursive(
        self,
        start_url: str,
        max_depth: int,
        max_pages: int,
        include_external: bool,
        format: str,
    ) -> List[CrawlResult]:
        """递归爬取（BFS）

        Args:
            start_url: 起始 URL
            max_depth: 最大深度
            max_pages: 最大页面数
            include_external: 是否包含外部链接
            format: 输出格式

        Returns:
            爬取结果列表
        """
        # 验证起始 URL
        validate_url(start_url)

        # 解析基础域名
        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc

        # BFS 队列: (url, depth)
        queue: List[tuple] = [(start_url, 0)]
        visited: Set[str] = set()
        results: List[CrawlResult] = []

        while queue and len(results) < max_pages:
            url, depth = queue.pop(0)

            # 跳过已访问的 URL
            if url in visited:
                continue

            # 跳过超过最大深度的 URL
            if depth > max_depth:
                continue

            visited.add(url)

            # 爬取页面
            try:
                result = await self.crawl_page(url, format=format)
                result.depth = depth
                results.append(result)

                logger.info(f"已爬取 {len(results)}/{max_pages} 页, 深度: {depth}")

                # 提取新链接加入队列
                if depth < max_depth:
                    for link in result.links:
                        if not link or link in visited:
                            continue

                        # 标准化链接
                        if link.startswith('/'):
                            link = urljoin(url, link)

                        parsed_link = urlparse(link)

                        # 检查是否为外部链接
                        is_external = parsed_link.netloc != base_domain

                        if is_external and not include_external:
                            continue

                        # 跳过非 HTTP 链接
                        if parsed_link.scheme not in ('http', 'https'):
                            continue

                        # 跳过锚点、javascript 等
                        if link.startswith('#') or link.startswith('javascript:'):
                            continue

                        queue.append((link, depth + 1))

            except Exception as e:
                logger.error(f"爬取失败: {url}, 错误: {e}")
                results.append(CrawlResult(
                    url=url,
                    title="",
                    markdown="",
                    status="failed",
                    error=str(e),
                    depth=depth,
                ))

            # 随机延迟 0.1~0.3 秒，模拟人类行为，避免触发速率限制
            await asyncio.sleep(random.uniform(0.1, 0.3))

        logger.info(f"递归爬取完成，共爬取 {len(results)} 页")
        return results
