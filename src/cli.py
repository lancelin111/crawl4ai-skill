"""CLI 入口 - Click 命令行接口

提供 crawl4ai-skill 命令行工具。
"""

import asyncio
import json
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

from .search import DuckDuckGoSearcher, SearchError, RateLimitError
from .crawler import SmartCrawler, CrawlError, InvalidURLError, HTTPError
from .parser import ContentParser


# 全局标志，用于优雅退出
_interrupted = False


def handle_interrupt(signum, frame):
    """处理 Ctrl+C 中断"""
    global _interrupted
    _interrupted = True
    click.echo("\n⚠ 收到中断信号，正在优雅退出...", err=True)


# 注册信号处理
signal.signal(signal.SIGINT, handle_interrupt)


@click.group()
@click.version_option(version="0.3.0", prog_name="crawl4ai-skill")
def cli():
    """Crawl4AI Skill - 智能搜索与爬取工具

    为 OpenClaw 提供 DuckDuckGo 搜索和智能网页爬取能力。

    \b
    示例:
      crawl4ai-skill search "python web scraping"
      crawl4ai-skill crawl https://example.com
      crawl4ai-skill crawl-site https://docs.example.com
    """
    pass


@cli.command()
@click.argument("query")
@click.option("--num-results", "-n", default=10, help="搜索结果数量 (1-100)")
@click.option("--output", "-o", type=click.Path(), help="输出文件路径 (JSON 格式)")
def search(query: str, num_results: int, output: Optional[str]):
    """搜索网页

    使用 DuckDuckGo 搜索，无需 API key。

    \b
    示例:
      crawl4ai-skill search "python web scraping"
      crawl4ai-skill search "AI tutorials" --num-results 5
      crawl4ai-skill search "machine learning" -o results.json
    """
    try:
        searcher = DuckDuckGoSearcher()
        results = searcher.search(query, num_results)

        if not results:
            click.echo(f"⚠ 未找到相关结果: {query}", err=True)
            raise SystemExit(0)

        output_data = {
            "query": query,
            "num_results": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": [r.to_dict() for r in results],
        }

        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                click.echo(f"✓ 搜索结果已保存到 {output}")
            except PermissionError:
                click.echo(f"✗ 无法写入文件: {output}，权限不足", err=True)
                raise SystemExit(1)
            except OSError as e:
                click.echo(f"✗ 无法写入文件: {output}，{e}", err=True)
                raise SystemExit(1)
        else:
            click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))

    except RateLimitError as e:
        click.echo(f"✗ 搜索被限流，请稍后重试: {e}", err=True)
        raise SystemExit(1)
    except SearchError as e:
        click.echo(f"✗ 搜索失败: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("url")
@click.option(
    "--format",
    "-f",
    default="fit_markdown",
    type=click.Choice(["fit_markdown", "markdown_with_citations", "raw_markdown"]),
    help="输出格式",
)
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
@click.option("--wait-for", "-w", help="等待元素加载 (CSS selector)")
@click.option("--timeout", "-t", default=30, help="超时时间（秒）")
@click.option(
    "--wait-until",
    default="domcontentloaded",
    type=click.Choice(["domcontentloaded", "networkidle", "load", "commit"]),
    help="等待策略：domcontentloaded(默认), networkidle(动态页面推荐), load, commit",
)
@click.option(
    "--delay",
    "-d",
    default=0.1,
    type=float,
    help="返回前额外等待时间（秒），用于 JS 动态页面",
)
@click.option("--include-metadata", is_flag=True, help="在输出中包含元数据头")
def crawl(
    url: str,
    format: str,
    output: Optional[str],
    wait_for: Optional[str],
    timeout: int,
    wait_until: str,
    delay: float,
    include_metadata: bool,
):
    """爬取单个网页

    提取网页内容并转换为 Markdown 格式。

    \b
    示例:
      crawl4ai-skill crawl https://example.com
      crawl4ai-skill crawl https://example.com --format markdown_with_citations
      crawl4ai-skill crawl https://example.com -o page.md
      crawl4ai-skill crawl https://xueqiu.com/S/BIDU --wait-until networkidle --delay 2
    """
    try:
        crawler = SmartCrawler()
        result = asyncio.run(
            crawler.crawl_page(
                url,
                format=format,
                wait_for=wait_for,
                timeout=timeout,
                wait_until=wait_until,
                delay_before_return_html=delay,
            )
        )

        if result.status == "failed":
            click.echo(f"✗ 爬取失败: {result.error}", err=True)
            raise SystemExit(1)

        # 格式化输出
        parser = ContentParser()
        markdown = result.markdown

        if include_metadata:
            metadata = {
                "title": result.title,
                "url": result.url,
                "timestamp": result.crawled_at,
                "format": format,
            }
            markdown = parser.format_markdown(markdown, metadata)

        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(markdown)
                click.echo(f"✓ 页面已保存到 {output}")
                click.echo(f"  标题: {result.title}")
                click.echo(f"  链接数: {len(result.links)}")
            except PermissionError:
                click.echo(f"✗ 无法写入文件: {output}，权限不足", err=True)
                raise SystemExit(1)
            except OSError as e:
                click.echo(f"✗ 无法写入文件: {output}，{e}", err=True)
                raise SystemExit(1)
        else:
            click.echo(markdown)

    except InvalidURLError as e:
        click.echo(f"✗ 无效的 URL: {e}", err=True)
        raise SystemExit(1)
    except HTTPError as e:
        click.echo(f"✗ HTTP 错误: {e}", err=True)
        raise SystemExit(1)
    except CrawlError as e:
        click.echo(f"✗ 爬取失败: {e}", err=True)
        raise SystemExit(1)


@cli.command("crawl-site")
@click.argument("url")
@click.option("--max-depth", "-d", default=2, help="最大爬取深度 (1-10)")
@click.option("--max-pages", "-p", default=50, help="最大页面数量 (1-1000)")
@click.option("--include-external", is_flag=True, help="包含外部链接")
@click.option(
    "--format",
    "-f",
    default="fit_markdown",
    type=click.Choice(["fit_markdown", "markdown_with_citations", "raw_markdown"]),
    help="输出格式",
)
@click.option(
    "--output-dir",
    "-o",
    default="./crawl_output",
    type=click.Path(),
    help="输出目录",
)
@click.option(
    "--strategy",
    "-s",
    default="auto",
    type=click.Choice(["auto", "sitemap", "recursive"]),
    help="爬取策略",
)
def crawl_site(
    url: str,
    max_depth: int,
    max_pages: int,
    include_external: bool,
    format: str,
    output_dir: str,
    strategy: str,
):
    """爬取整个站点

    支持 sitemap、llms-full.txt 和递归爬取策略。

    \b
    示例:
      crawl4ai-skill crawl-site https://docs.example.com
      crawl4ai-skill crawl-site https://example.com/sitemap.xml --strategy sitemap
      crawl4ai-skill crawl-site https://example.com --max-depth 3 --max-pages 100
    """
    try:
        # 创建输出目录
        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            pages_path = output_path / "pages"
            pages_path.mkdir(exist_ok=True)
        except PermissionError:
            click.echo(f"✗ 无法创建目录: {output_dir}，权限不足", err=True)
            raise SystemExit(1)
        except OSError as e:
            click.echo(f"✗ 无法创建目录: {output_dir}，{e}", err=True)
            raise SystemExit(1)

        click.echo(f"开始爬取: {url}")
        click.echo(f"策略: {strategy}, 最大深度: {max_depth}, 最大页面: {max_pages}")

        crawler = SmartCrawler()
        results = asyncio.run(
            crawler.crawl_site(
                url,
                max_depth=max_depth,
                max_pages=max_pages,
                include_external=include_external,
                format=format,
                strategy=strategy,
            )
        )

        if not results:
            click.echo("⚠ 未爬取到任何页面", err=True)
            return

        # 保存结果
        parser = ContentParser()
        index_data = {
            "start_url": url,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "strategy": strategy,
            "max_depth": max_depth,
            "max_pages": max_pages,
            "pages": [],
        }

        success_count = 0
        failed_count = 0

        for i, result in enumerate(results, 1):
            page_id = f"page_{i:03d}"
            page_file = f"pages/{page_id}.md"

            if result.status == "success":
                success_count += 1
                # 保存页面内容
                try:
                    with open(output_path / page_file, "w", encoding="utf-8") as f:
                        metadata = {
                            "title": result.title,
                            "url": result.url,
                            "timestamp": result.crawled_at,
                            "format": format,
                        }
                        content = parser.format_markdown(result.markdown, metadata)
                        f.write(content)
                except (PermissionError, OSError) as e:
                    click.echo(f"  ⚠ 无法保存文件 {page_file}: {e}", err=True)
                    failed_count += 1
                    success_count -= 1
            else:
                failed_count += 1

            index_data["pages"].append(
                {
                    "id": page_id,
                    "url": result.url,
                    "title": result.title,
                    "depth": result.depth,
                    "file": page_file if result.status == "success" else None,
                    "status": result.status,
                    "error": result.error,
                    "links_found": len(result.links),
                }
            )

            click.echo(
                f"  [{i}/{len(results)}] {result.status}: {result.url[:60]}..."
                if len(result.url) > 60
                else f"  [{i}/{len(results)}] {result.status}: {result.url}"
            )

        # 保存索引
        with open(output_path / "index.json", "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        # 保存统计信息
        stats = {
            "total_pages": len(results),
            "successful": success_count,
            "failed": failed_count,
            "total_links_found": sum(len(r.links) for r in results),
        }
        with open(output_path / "stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        click.echo()
        click.echo(f"✓ 爬取完成!")
        click.echo(f"  成功: {success_count}, 失败: {failed_count}")
        click.echo(f"  输出目录: {output_path}")

    except InvalidURLError as e:
        click.echo(f"✗ 无效的 URL: {e}", err=True)
        raise SystemExit(1)
    except HTTPError as e:
        click.echo(f"✗ HTTP 错误: {e}", err=True)
        raise SystemExit(1)
    except CrawlError as e:
        click.echo(f"✗ 爬取失败: {e}", err=True)
        raise SystemExit(1)


@cli.command("search-and-crawl")
@click.argument("query")
@click.option("--num-results", "-n", default=5, help="搜索结果数量")
@click.option("--crawl-top", "-c", default=3, help="爬取前 N 个结果")
@click.option(
    "--format",
    "-f",
    default="fit_markdown",
    type=click.Choice(["fit_markdown", "markdown_with_citations", "raw_markdown"]),
    help="输出格式",
)
@click.option(
    "--output-dir",
    "-o",
    default="./search_crawl_output",
    type=click.Path(),
    help="输出目录",
)
def search_and_crawl(
    query: str,
    num_results: int,
    crawl_top: int,
    format: str,
    output_dir: str,
):
    """搜索并爬取

    先搜索，再爬取前 N 个结果。

    \b
    示例:
      crawl4ai-skill search-and-crawl "python web scraping tutorials"
      crawl4ai-skill search-and-crawl "AI tutorials" --num-results 10 --crawl-top 5
    """
    global _interrupted

    # 参数验证: crawl_top 不能超过 num_results
    if crawl_top > num_results:
        click.echo(f"⚠ crawl-top ({crawl_top}) 大于 num-results ({num_results})，已自动调整为 {num_results}", err=True)
        crawl_top = num_results

    try:
        # 创建输出目录
        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            click.echo(f"✗ 无法创建目录: {output_dir}，权限不足", err=True)
            raise SystemExit(1)
        except OSError as e:
            click.echo(f"✗ 无法创建目录: {output_dir}，{e}", err=True)
            raise SystemExit(1)

        # 1. 搜索
        click.echo(f"搜索: {query}")
        searcher = DuckDuckGoSearcher()
        search_results = searcher.search(query, num_results)

        if not search_results:
            click.echo(f"⚠ 未找到相关结果: {query}", err=True)
            # 保存空结果
            search_data = {
                "query": query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": [],
            }
            with open(output_path / "search_results.json", "w", encoding="utf-8") as f:
                json.dump(search_data, f, indent=2, ensure_ascii=False)
            click.echo(f"✓ 空结果已保存到 {output_path}")
            return

        click.echo(f"  找到 {len(search_results)} 条结果")

        # 保存搜索结果
        search_data = {
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": [r.to_dict() for r in search_results],
        }
        with open(output_path / "search_results.json", "w", encoding="utf-8") as f:
            json.dump(search_data, f, indent=2, ensure_ascii=False)

        # 2. 爬取前 N 个
        urls_to_crawl = [r.url for r in search_results[:crawl_top]]
        click.echo(f"\n爬取前 {len(urls_to_crawl)} 个结果:")

        crawler = SmartCrawler()
        parser = ContentParser()
        crawl_results = []

        for i, url in enumerate(urls_to_crawl, 1):
            # 检查是否被中断
            if _interrupted:
                click.echo("\n⚠ 用户中断，保存已完成的结果...", err=True)
                break

            click.echo(f"  [{i}/{len(urls_to_crawl)}] {url[:60]}...")
            try:
                result = asyncio.run(crawler.crawl_page(url, format=format))
                crawl_results.append(result)

                # 保存页面
                if result.status == "success":
                    filename = f"page_{i:02d}.md"
                    with open(output_path / filename, "w", encoding="utf-8") as f:
                        metadata = {
                            "title": result.title,
                            "url": result.url,
                            "timestamp": result.crawled_at,
                            "format": format,
                        }
                        content = parser.format_markdown(result.markdown, metadata)
                        f.write(content)
                    click.echo(f"    ✓ 已保存: {filename}")
                else:
                    click.echo(f"    ✗ 失败: {result.error}")

            except Exception as e:
                click.echo(f"    ✗ 错误: {e}")

        # 保存索引
        index_data = {
            "query": query,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "search_results": len(search_results),
            "crawled_pages": len([r for r in crawl_results if r.status == "success"]),
            "interrupted": _interrupted,
            "pages": [
                {
                    "url": r.url,
                    "title": r.title,
                    "status": r.status,
                }
                for r in crawl_results
            ],
        }
        with open(output_path / "index.json", "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        click.echo(f"\n✓ 完成! 输出目录: {output_path}")

    except RateLimitError as e:
        click.echo(f"✗ 搜索被限流，请稍后重试: {e}", err=True)
        raise SystemExit(1)
    except SearchError as e:
        click.echo(f"✗ 搜索失败: {e}", err=True)
        raise SystemExit(1)
    except InvalidURLError as e:
        click.echo(f"✗ 无效的 URL: {e}", err=True)
        raise SystemExit(1)
    except CrawlError as e:
        click.echo(f"✗ 爬取失败: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
