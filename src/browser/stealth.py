"""Stealth 配置 - 反检测浏览器设置

使用 playwright-stealth 隐藏自动化特征，降低被检测风险。
"""

import random
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# User-Agent 轮换池 - 常见桌面浏览器
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
]


def get_random_user_agent() -> str:
    """获取随机 User-Agent

    Returns:
        随机选择的 User-Agent 字符串
    """
    return random.choice(USER_AGENTS)


async def apply_stealth(page) -> None:
    """应用 Stealth 脚本到页面

    使用 playwright-stealth 隐藏自动化特征。

    Args:
        page: Playwright Page 对象
    """
    try:
        from playwright_stealth import stealth_async
        await stealth_async(page)
        logger.debug("Stealth 脚本已应用")
    except ImportError:
        logger.warning("playwright-stealth 未安装，跳过 Stealth 配置")
    except Exception as e:
        logger.warning(f"应用 Stealth 脚本失败: {e}")


async def create_stealth_context(
    browser,
    proxy: Optional[Dict[str, str]] = None,
    user_agent: Optional[str] = None,
    viewport: Optional[Dict[str, int]] = None,
    locale: str = "zh-CN",
    timezone_id: str = "Asia/Shanghai",
) -> Any:
    """创建带 Stealth 配置的浏览器上下文

    Args:
        browser: Playwright Browser 对象
        proxy: 代理配置，如 {"server": "http://proxy:8080"}
        user_agent: 自定义 User-Agent，不指定则随机选择
        viewport: 视口大小，如 {"width": 1920, "height": 1080}
        locale: 语言区域设置
        timezone_id: 时区 ID

    Returns:
        配置好的 BrowserContext 对象
    """
    # 默认视口
    if viewport is None:
        viewport = {"width": 1920, "height": 1080}

    # 随机 User-Agent
    if user_agent is None:
        user_agent = get_random_user_agent()

    # 上下文配置
    context_options = {
        "user_agent": user_agent,
        "viewport": viewport,
        "locale": locale,
        "timezone_id": timezone_id,
        # 设置常见的浏览器权限
        "permissions": ["geolocation"],
        # 忽略 HTTPS 错误（开发环境）
        "ignore_https_errors": True,
        # 设备像素比
        "device_scale_factor": 1,
        # 颜色方案
        "color_scheme": "light",
    }

    # 添加代理配置
    if proxy:
        context_options["proxy"] = proxy

    logger.debug(f"创建浏览器上下文: user_agent={user_agent[:50]}...")

    context = await browser.new_context(**context_options)

    return context


async def create_persistent_context(
    browser_type,
    user_data_dir: str,
    proxy: Optional[Dict[str, str]] = None,
    user_agent: Optional[str] = None,
    headless: bool = False,
) -> Any:
    """创建持久化浏览器上下文

    使用 persistent context 保存登录状态、Cookies 等。

    Args:
        browser_type: Playwright BrowserType (chromium/firefox/webkit)
        user_data_dir: 用户数据目录路径，用于存储 Cookies、LocalStorage 等
        proxy: 代理配置
        user_agent: 自定义 User-Agent
        headless: 是否无头模式

    Returns:
        持久化的 BrowserContext 对象
    """
    if user_agent is None:
        user_agent = get_random_user_agent()

    context_options = {
        "user_data_dir": user_data_dir,
        "user_agent": user_agent,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "ignore_https_errors": True,
        "headless": headless,
    }

    if proxy:
        context_options["proxy"] = proxy

    logger.debug(f"创建持久化上下文: {user_data_dir}")

    context = await browser_type.launch_persistent_context(**context_options)

    return context
