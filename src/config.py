"""配置管理 - 使用 Pydantic"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class CrawlConfig(BaseModel):
    """爬取配置"""

    timeout: int = Field(default=30, ge=1, le=300, description="超时时间（秒）")
    max_depth: int = Field(default=2, ge=1, le=10, description="最大爬取深度")
    max_pages: int = Field(default=50, ge=1, le=1000, description="最大页面数量")
    include_external: bool = Field(default=False, description="是否包含外部链接")
    format: Literal["fit_markdown", "markdown_with_citations", "raw_markdown"] = Field(
        default="fit_markdown", description="输出格式"
    )
    wait_for: Optional[str] = Field(default=None, description="等待元素（CSS selector）")


class SearchConfig(BaseModel):
    """搜索配置"""

    num_results: int = Field(default=10, ge=1, le=100, description="搜索结果数量")
    timeout: int = Field(default=10, ge=1, le=60, description="超时时间（秒）")


class SiteCrawlConfig(CrawlConfig):
    """全站爬取配置"""

    strategy: Literal["auto", "sitemap", "recursive"] = Field(
        default="auto", description="爬取策略"
    )
    output_dir: str = Field(default="./crawl_output", description="输出目录")


class SearchAndCrawlConfig(BaseModel):
    """搜索并爬取配置"""

    num_results: int = Field(default=5, ge=1, le=100, description="搜索结果数量")
    crawl_top: int = Field(default=3, ge=1, le=20, description="爬取前 N 个结果")
    format: Literal["fit_markdown", "markdown_with_citations", "raw_markdown"] = Field(
        default="fit_markdown", description="输出格式"
    )
    output_dir: str = Field(default="./search_crawl_output", description="输出目录")
