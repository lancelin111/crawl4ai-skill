"""CLI 入口 - Click 命令行接口

提供 crawl4ai-skill 命令行工具。
"""

import asyncio
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

from .search import DuckDuckGoSearcher, SearchError, RateLimitError
from .crawler import SmartCrawler, CrawlError, InvalidURLError, HTTPError


# 全局标志，用于优雅退出
_interrupted = False


def handle_interrupt(signum, frame):
    """处理 Ctrl+C 中断"""
    global _interrupted
    _interrupted = True
    click.echo("\n⚠ 收到中断信号，正在优雅退出...", err=True)


# 注册信号处理
signal.signal(signal.SIGINT, handle_interrupt)

from .parser import ContentParser
from .login import (
    SessionManager,
    get_session_manager,
    get_supported_platforms,
    LoginError,
    SessionExpiredError,
)


@click.group()
@click.version_option(version="0.2.0", prog_name="crawl4ai-skill")
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
@click.option("--include-metadata", is_flag=True, help="在输出中包含元数据头")
def crawl(
    url: str,
    format: str,
    output: Optional[str],
    wait_for: Optional[str],
    timeout: int,
    include_metadata: bool,
):
    """爬取单个网页

    提取网页内容并转换为 Markdown 格式。

    \b
    示例:
      crawl4ai-skill crawl https://example.com
      crawl4ai-skill crawl https://example.com --format markdown_with_citations
      crawl4ai-skill crawl https://example.com -o page.md
    """
    try:
        crawler = SmartCrawler()
        result = asyncio.run(
            crawler.crawl_page(url, format=format, wait_for=wait_for, timeout=timeout)
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


@cli.command()
@click.argument("platform", type=click.Choice(get_supported_platforms()))
@click.option("--cookies", "-c", help="Cookie 字符串（不推荐，会记录在 shell history）")
@click.option("--cookies-file", type=click.Path(exists=True), help="从文件读取 Cookie（需 chmod 600）")
@click.option("--interactive", "-i", is_flag=True, help="交互式输入 Cookie（输入时不显示）")
@click.option("--username", "-u", help="用户名（Twitter）")
@click.option("--password", "-p", help="密码（Twitter）")
@click.option("--headless/--no-headless", default=False, help="是否无头模式（默认显示浏览器）")
def login(
    platform: str,
    cookies: Optional[str],
    cookies_file: Optional[str],
    interactive: bool,
    username: Optional[str],
    password: Optional[str],
    headless: bool,
):
    """登录指定平台并保存 Session

    支持的平台: twitter, xiaohongshu

    \b
    Cookie 输入方式（按安全性排序）：
    1. 环境变量（推荐）- 不记录在 shell history
       export TWITTER_COOKIES="auth_token=xxx; ct0=yyy"
       crawl4ai-skill login twitter

    2. 交互式输入 - 输入时不显示
       crawl4ai-skill login twitter --interactive

    3. 文件读取 - 需设置 chmod 600
       crawl4ai-skill login twitter --cookies-file ~/.twitter-cookies

    4. 命令行参数（不推荐）- 会记录在 shell history
       crawl4ai-skill login twitter --cookies "auth_token=xxx"

    \b
    其他登录方式：
    - 用户名密码（Twitter）- 可能需要验证码
    - 扫码登录（小红书）- 需要 App

    \b
    示例:
      # 环境变量（推荐）
      export TWITTER_COOKIES="auth_token=xxx; ct0=yyy"
      crawl4ai-skill login twitter

      # 交互式输入
      crawl4ai-skill login twitter --interactive

      # 从文件读取
      crawl4ai-skill login twitter --cookies-file ~/.twitter-cookies

      # 扫码登录
      crawl4ai-skill login xiaohongshu
    """
    # 获取 Cookie 的优先级：环境变量 > 交互式 > 文件 > 命令行参数
    final_cookies = None

    # 1. 检查环境变量
    env_var_name = f"{platform.upper()}_COOKIES"
    env_cookies = os.environ.get(env_var_name)
    if env_cookies:
        final_cookies = env_cookies
        click.echo(f"✓ 从环境变量 {env_var_name} 读取 Cookie")

    # 2. 交互式输入
    elif interactive:
        click.echo(f"请输入 {platform} 的 Cookie（输入时不显示）:")
        if platform in ["twitter", "x"]:
            click.echo("  格式: auth_token=xxx; ct0=yyy")
        final_cookies = click.prompt("Cookie", hide_input=True)

    # 3. 从文件读取
    elif cookies_file:
        try:
            with open(cookies_file, "r", encoding="utf-8") as f:
                final_cookies = f.read().strip()
            click.echo(f"✓ 从文件 {cookies_file} 读取 Cookie")
        except Exception as e:
            click.echo(f"✗ 读取文件失败: {e}", err=True)
            raise SystemExit(1)

    # 4. 命令行参数（不推荐）
    elif cookies:
        final_cookies = cookies
        click.echo("⚠ 警告: 命令行传递 Cookie 会记录在 shell history，建议使用环境变量或 --interactive", err=True)

    # 使用获取到的 cookies
    cookies = final_cookies
    async def _login():
        from playwright.async_api import async_playwright
        from .browser.stealth import apply_stealth, get_random_user_agent

        manager = get_session_manager()
        login_handler = manager.get_login(platform)

        # 使用持久化上下文目录（更难被检测）
        user_data_dir = Path.home() / ".crawl4ai-skill" / "browser_data" / platform
        user_data_dir.mkdir(parents=True, exist_ok=True)

        async with async_playwright() as p:
            # 使用持久化上下文，更像真实浏览器
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=headless,
                user_agent=get_random_user_agent(),
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            )

            try:
                # Cookie 登录
                if cookies:
                    click.echo(f"正在使用 Cookie 登录 {platform}...")
                    await login_handler.import_cookies(cookies, context)

                    # 验证
                    page = context.pages[0] if context.pages else await context.new_page()
                    await apply_stealth(page)

                    if await login_handler.check_login_status(page):
                        await login_handler.save_session(context)
                        click.echo(f"✓ {platform} 登录成功！Session 已保存")
                        return True
                    else:
                        click.echo(f"✗ Cookie 无效或已过期", err=True)
                        return False

                # 用户名密码登录（仅 Twitter）
                elif username and password:
                    if platform not in ["twitter", "x"]:
                        click.echo(f"✗ {platform} 不支持用户名密码登录", err=True)
                        return False

                    click.echo(f"正在使用用户名密码登录 {platform}...")
                    success = await login_handler.login(
                        context,
                        username=username,
                        password=password,
                    )

                    if success:
                        click.echo(f"✓ {platform} 登录成功！Session 已保存")
                    else:
                        click.echo(f"✗ 登录失败", err=True)
                    return success

                # 交互式登录（扫码等）
                else:
                    click.echo(f"正在启动交互式登录...")
                    click.echo("请在浏览器中完成登录...")

                    success = await login_handler.login(context)

                    if success:
                        click.echo(f"✓ {platform} 登录成功！Session 已保存")
                    else:
                        click.echo(f"✗ 登录失败或超时", err=True)
                    return success

            except Exception as e:
                click.echo(f"✗ 登录失败: {e}", err=True)
                return False

            finally:
                await context.close()

    try:
        success = asyncio.run(_login())
        if not success:
            raise SystemExit(1)
    except LoginError as e:
        click.echo(f"✗ 登录错误: {e}", err=True)
        raise SystemExit(1)


@cli.command("session-status")
def session_status():
    """查看所有平台的登录状态

    \b
    示例:
      crawl4ai-skill session-status
    """
    manager = get_session_manager()
    status = manager.get_all_sessions_status()

    click.echo("平台登录状态:")
    click.echo("-" * 50)

    for platform, info in status.items():
        has_session = info.get("has_session", False)

        if has_session:
            session_info = info.get("info", {})
            saved_at = session_info.get("saved_at", "未知")
            cookie_count = session_info.get("cookie_count", 0)
            encrypted = session_info.get("encrypted", False)
            encryption_type = session_info.get("encryption_type", "None")

            click.echo(f"  {platform}: ✓ 已登录")
            click.echo(f"    - 保存时间: {saved_at}")
            click.echo(f"    - Cookie 数量: {cookie_count}")
            if encrypted:
                click.echo(f"    - 加密存储: ✓ ({encryption_type})")
            else:
                click.echo(f"    - 加密存储: ✗ (建议重新登录以启用加密)")
        else:
            click.echo(f"  {platform}: ✗ 未登录")

    click.echo("-" * 50)
    click.echo(f"支持的平台: {', '.join(get_supported_platforms())}")


@cli.command("session-clear")
@click.argument("platform", required=False)
@click.option("--all", "clear_all", is_flag=True, help="清除所有平台的 Session")
def session_clear(platform: Optional[str], clear_all: bool):
    """清除保存的 Session

    \b
    示例:
      crawl4ai-skill session-clear twitter
      crawl4ai-skill session-clear --all
    """
    manager = get_session_manager()

    if clear_all:
        results = manager.clear_all_sessions()
        for p, success in results.items():
            if success:
                click.echo(f"  {p}: ✓ 已清除")
            else:
                click.echo(f"  {p}: - 无 Session")
        click.echo("✓ 所有 Session 已清除")
    elif platform:
        if manager.clear_session(platform):
            click.echo(f"✓ {platform} Session 已清除")
        else:
            click.echo(f"✗ 清除失败或无 Session", err=True)
    else:
        click.echo("请指定平台或使用 --all 清除所有", err=True)
        raise SystemExit(1)


async def _extract_twitter_content(page, url: str) -> str:
    """提取 Twitter/X 推文内容，包括引用推文"""
    import asyncio

    # 等待推文加载
    try:
        await page.wait_for_selector('[data-testid="tweet"]', timeout=10000)
    except Exception:
        pass

    await asyncio.sleep(2)

    # 滚动加载更多推文
    for _ in range(5):
        await page.evaluate("window.scrollBy(0, 1000)")
        await asyncio.sleep(0.8)

    # 提取用户信息和推文（包括引用推文）
    result = await page.evaluate("""
    () => {
        const tweets = [];

        // 获取用户名
        const nameEl = document.querySelector('[data-testid="UserName"]');
        const userName = nameEl ? nameEl.innerText : '';

        // 获取用户简介
        const bioEl = document.querySelector('[data-testid="UserDescription"]');
        const userBio = bioEl ? bioEl.innerText : '';

        // 获取所有推文
        const tweetEls = document.querySelectorAll('[data-testid="tweet"]');
        tweetEls.forEach((tweet, index) => {
            if (index >= 15) return; // 最多15条

            // 获取推文文本（可能有多个 tweetText，第一个是主推文）
            const textEls = tweet.querySelectorAll('[data-testid="tweetText"]');
            const timeEl = tweet.querySelector('time');
            const time = timeEl ? timeEl.getAttribute('datetime') : '';

            // 主推文文本
            const mainText = textEls[0] ? textEls[0].innerText : '';

            // 检查是否有引用推文 (Quote Tweet)
            let quotedTweet = null;

            // 方法1: 查找 [role="link"] 内嵌的引用推文区域
            const quoteContainer = tweet.querySelector('[aria-labelledby]');
            if (quoteContainer) {
                // 引用推文的作者
                const quoteUserEl = quoteContainer.querySelector('[data-testid="User-Name"]') ||
                                   quoteContainer.querySelector('span[dir="ltr"]');
                // 引用推文的文本（第二个 tweetText 通常是引用的内容）
                const quoteTextEl = quoteContainer.querySelector('[data-testid="tweetText"]');

                if (quoteTextEl) {
                    quotedTweet = {
                        user: quoteUserEl ? quoteUserEl.innerText.split('\\n')[0] : '',
                        text: quoteTextEl.innerText
                    };
                }
            }

            // 方法2: 如果有多个 tweetText，第二个可能是引用内容
            if (!quotedTweet && textEls.length > 1) {
                // 查找引用区域的用户名
                const allUserNames = tweet.querySelectorAll('[data-testid="User-Name"]');
                const quoteUser = allUserNames.length > 1 ? allUserNames[1].innerText.split('\\n')[0] : '';

                quotedTweet = {
                    user: quoteUser,
                    text: textEls[1].innerText
                };
            }

            // 检查是否是转发 (Retweet)
            let isRetweet = false;
            let retweetFrom = '';
            const socialContext = tweet.querySelector('[data-testid="socialContext"]');
            if (socialContext && socialContext.innerText.includes('reposted')) {
                isRetweet = true;
                retweetFrom = socialContext.innerText;
            }

            if (mainText || quotedTweet) {
                tweets.push({
                    text: mainText,
                    time,
                    quotedTweet,
                    isRetweet,
                    retweetFrom
                });
            }
        });

        return { userName, userBio, tweets };
    }
    """)

    # 格式化为 Markdown
    lines = []
    lines.append(f"# {result['userName']}")
    if result['userBio']:
        lines.append(f"\n> {result['userBio']}")
    lines.append(f"\n**URL**: {url}")
    lines.append(f"\n## 最新推文 ({len(result['tweets'])} 条)\n")

    for i, tweet in enumerate(result['tweets'], 1):
        time_str = tweet['time'][:10] if tweet['time'] else ''
        lines.append(f"### {i}. [{time_str}]")

        # 如果是转发，标注
        if tweet.get('isRetweet') and tweet.get('retweetFrom'):
            lines.append(f"*{tweet['retweetFrom']}*\n")

        # 主推文内容
        if tweet['text']:
            lines.append(f"{tweet['text']}")

        # 引用推文内容
        if tweet.get('quotedTweet'):
            qt = tweet['quotedTweet']
            lines.append(f"\n> **引用 {qt['user']}:**")
            lines.append(f"> {qt['text']}")

        lines.append("")  # 空行分隔

    return "\n".join(lines)


async def _extract_xiaohongshu_content(page, url: str) -> str:
    """提取小红书内容"""
    import asyncio

    await asyncio.sleep(3)

    # 滚动加载
    for _ in range(2):
        await page.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(1)

    # 提取内容
    result = await page.evaluate("""
    () => {
        // 笔记标题
        const titleEl = document.querySelector('#detail-title') || document.querySelector('.title');
        const title = titleEl ? titleEl.innerText : '';

        // 笔记内容
        const contentEl = document.querySelector('#detail-desc') || document.querySelector('.desc');
        const content = contentEl ? contentEl.innerText : '';

        // 作者
        const authorEl = document.querySelector('.author-wrapper .username') || document.querySelector('.user-name');
        const author = authorEl ? authorEl.innerText : '';

        // 点赞数等
        const likeEl = document.querySelector('[class*="like-count"]');
        const likes = likeEl ? likeEl.innerText : '';

        return { title, content, author, likes };
    }
    """)

    # 格式化
    lines = []
    if result['title']:
        lines.append(f"# {result['title']}")
    if result['author']:
        lines.append(f"\n**作者**: {result['author']}")
    if result['likes']:
        lines.append(f"**点赞**: {result['likes']}")
    lines.append(f"**URL**: {url}\n")
    lines.append("---\n")
    if result['content']:
        lines.append(result['content'])
    else:
        # 备用：获取整个页面文本
        body_text = page.evaluate("() => document.body.innerText")
        lines.append(str(body_text)[:2000])

    return "\n".join(lines)


@cli.command("crawl-with-login")
@click.argument("url")
@click.option("--platform", "-p", required=True, type=click.Choice(get_supported_platforms()), help="使用哪个平台的 Session")
@click.option(
    "--format",
    "-f",
    default="fit_markdown",
    type=click.Choice(["fit_markdown", "markdown_with_citations", "raw_markdown"]),
    help="输出格式",
)
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
@click.option("--headless/--no-headless", default=True, help="是否无头模式（默认无头）")
@click.option("--wait-for", "-w", help="等待元素加载 (CSS selector)")
@click.option("--clean", is_flag=True, help="生成更干净的输出（移除图片链接）")
@click.option("--extract-tweets", is_flag=True, help="专门提取推文内容（Twitter/X 推荐）")
def crawl_with_login(
    url: str,
    platform: str,
    format: str,
    output: Optional[str],
    headless: bool,
    wait_for: Optional[str],
    clean: bool,
    extract_tweets: bool,
):
    """使用已保存的 Session 爬取需要登录的页面

    使用 Playwright 加载页面 + crawl4ai Markdown 生成器转换内容。

    \b
    示例:
      # 先登录
      crawl4ai-skill login twitter --cookies "auth_token=xxx"

      # 然后爬取
      crawl4ai-skill crawl-with-login https://x.com/elonmusk --platform twitter
      crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --clean  # 更干净的输出
      crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --extract-tweets  # 仅提取推文
    """
    async def _crawl_with_login():
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError:
            click.echo("✗ crawl4ai 未安装，请运行: pip install crawl4ai && crawl4ai-setup", err=True)
            return None

        manager = get_session_manager()
        login_handler = manager.get_login(platform)

        # 检查是否有保存的 Session
        if not login_handler.has_saved_session():
            click.echo(f"✗ 未找到 {platform} 的登录 Session", err=True)
            click.echo(f"  请先运行: crawl4ai-skill login {platform}", err=True)
            return None

        # 获取 Session 信息
        session_info = login_handler.get_session_info()
        if not session_info:
            click.echo(f"✗ Session 文件格式无效", err=True)
            return None

        click.echo(f"正在使用 {platform} Session 爬取: {url}")
        click.echo(f"  Cookies 数量: {session_info.get('cookie_count', 0)}")
        if session_info.get('encrypted'):
            click.echo(f"  加密存储: ✓ ({session_info.get('encryption_type', 'Unknown')})")

        try:
            from playwright.async_api import async_playwright
            from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
            from crawl4ai.content_filter_strategy import PruningContentFilter
            from .browser.stealth import apply_stealth, get_random_user_agent

            # 方法：使用 Playwright 持久化上下文加载页面，
            # 然后用 crawl4ai 的 markdown 生成器处理 HTML
            browser_data_dir = Path.home() / ".crawl4ai-skill" / "browser_data" / platform

            if not browser_data_dir.exists():
                click.echo(f"✗ 未找到浏览器数据目录，请先登录", err=True)
                click.echo(f"  运行: crawl4ai-skill login {platform}", err=True)
                return None

            async with async_playwright() as p:
                # 使用持久化上下文（与登录时相同的浏览器数据）
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=str(browser_data_dir),
                    headless=headless,
                    user_agent=get_random_user_agent(),
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",  # 设置英文语言
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                        "--lang=en-US",  # 浏览器语言设为英文
                    ],
                )

                try:
                    page = context.pages[0] if context.pages else await context.new_page()
                    await apply_stealth(page)

                    # 导航到目标 URL
                    click.echo(f"正在加载页面...")
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    # 等待 JavaScript 渲染
                    import asyncio

                    # 对于 Twitter/X，等待推文加载
                    if platform in ["twitter", "x"]:
                        try:
                            await page.wait_for_selector('[data-testid="tweet"]', timeout=15000)
                        except Exception:
                            click.echo("  等待推文加载...")

                    # 等待页面加载
                    if wait_for:
                        try:
                            await page.wait_for_selector(wait_for, timeout=10000)
                        except Exception:
                            pass

                    # 滚动页面加载更多内容
                    for _ in range(3):
                        await page.evaluate("window.scrollBy(0, 500)")
                        await asyncio.sleep(0.5)

                    await asyncio.sleep(2)  # 等待动态内容加载

                    title = await page.title()

                    # 专门提取推文模式 (--extract-tweets)
                    if extract_tweets and platform in ["twitter", "x"]:
                        click.echo("  使用推文提取模式...")
                        markdown_str = await _extract_twitter_content(page, url)
                        click.echo(f"✓ 推文提取完成")
                        return {
                            "url": url,
                            "title": title,
                            "markdown": markdown_str,
                        }

                    # 获取 HTML 内容
                    html_content = await page.content()

                    # 移除 noscript 标签内容（Twitter 的 JS 禁用回退内容）
                    import re
                    html_content = re.sub(
                        r'<noscript[^>]*>.*?</noscript>',
                        '',
                        html_content,
                        flags=re.DOTALL | re.IGNORECASE
                    )

                    # 对于 Twitter/X，提取主要内容区域的 HTML
                    if platform in ["twitter", "x"] and clean:
                        # 提取推文区域的 HTML（移除侧边栏等）
                        try:
                            main_content = await page.evaluate("""
                            () => {
                                // 尝试获取主要内容区域
                                const main = document.querySelector('main[role="main"]');
                                if (main) {
                                    // 移除侧边栏
                                    const sidebar = main.querySelector('[data-testid="sidebarColumn"]');
                                    if (sidebar) sidebar.remove();

                                    // 移除推荐用户区
                                    const whoToFollow = main.querySelectorAll('[aria-label*="follow"]');
                                    whoToFollow.forEach(el => el.remove());

                                    return main.innerHTML;
                                }
                                return null;
                            }
                            """)
                            if main_content:
                                html_content = f"<html><body>{main_content}</body></html>"
                                click.echo("  已提取主要内容区域")
                        except Exception:
                            pass

                    # 使用 crawl4ai 的 markdown 生成器和内容过滤器
                    html2text_opts = {
                        'body_width': 0,  # 不换行
                        'skip_internal_links': True,  # 跳过内部锚点链接
                    }
                    if clean:
                        # 清理模式：移除图片，简化输出
                        html2text_opts.update({
                            'ignore_images': True,
                            'ignore_emphasis': False,
                        })

                    # 使用 PruningContentFilter 来智能过滤低价值内容
                    content_filter = PruningContentFilter(
                        threshold=0.48,
                        threshold_type="fixed",
                    )

                    md_generator = DefaultMarkdownGenerator(
                        content_filter=content_filter,
                    )

                    markdown_result = md_generator.generate_markdown(
                        html_content,
                        base_url=url,
                        html2text_options=html2text_opts,
                    )

                    # 优先使用 fit_markdown（经过内容过滤的更干净版本）
                    if hasattr(markdown_result, 'fit_markdown') and markdown_result.fit_markdown:
                        markdown_str = markdown_result.fit_markdown
                        click.echo("  使用 fit_markdown（已过滤）")
                    elif hasattr(markdown_result, 'raw_markdown') and markdown_result.raw_markdown:
                        markdown_str = markdown_result.raw_markdown
                    else:
                        markdown_str = str(markdown_result)

                    click.echo(f"✓ 爬取成功")

                    return {
                        "url": url,
                        "title": title,
                        "markdown": markdown_str,
                    }

                finally:
                    await context.close()

        except Exception as e:
            click.echo(f"✗ 爬取失败: {e}", err=True)
            return None

    try:
        result = asyncio.run(_crawl_with_login())

        if result is None:
            raise SystemExit(1)

        # 输出结果
        parser = ContentParser()
        markdown = result["markdown"]

        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    metadata = {
                        "title": result["title"],
                        "url": result["url"],
                        "platform": platform,
                    }
                    content = parser.format_markdown(markdown, metadata)
                    f.write(content)
                click.echo(f"✓ 页面已保存到 {output}")
                click.echo(f"  标题: {result['title']}")
            except PermissionError:
                click.echo(f"✗ 无法写入文件: {output}，权限不足", err=True)
                raise SystemExit(1)
            except OSError as e:
                click.echo(f"✗ 无法写入文件: {output}，{e}", err=True)
                raise SystemExit(1)
        else:
            click.echo(markdown)

    except LoginError as e:
        click.echo(f"✗ 登录错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"✗ 爬取失败: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
