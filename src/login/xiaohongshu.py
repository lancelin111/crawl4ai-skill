"""小红书登录模块

支持 Cookie 导入和扫码登录。
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from .base import LoginBase, LoginError, SessionExpiredError

logger = logging.getLogger(__name__)


class XiaohongshuLogin(LoginBase):
    """小红书登录类

    支持两种登录方式：
    1. Cookie 导入（推荐）- 最稳定
    2. 扫码登录 - 需要手机 App

    Example:
        >>> login = XiaohongshuLogin()
        >>> async with async_playwright() as p:
        ...     browser = await p.chromium.launch(headless=False)
        ...     context = await browser.new_context()
        ...     # 方式1: Cookie 导入
        ...     await login.import_cookies("web_session=xxx", context)
        ...     # 方式2: 扫码登录
        ...     await login.login(context)
    """

    # 小红书登录关键 Cookie
    REQUIRED_COOKIES = ["web_session"]

    # 页面 URL
    LOGIN_URL = "https://www.xiaohongshu.com"
    HOME_URL = "https://www.xiaohongshu.com/explore"

    def __init__(self, session_dir: Optional[Path] = None):
        """初始化小红书登录

        Args:
            session_dir: Session 存储目录
        """
        super().__init__("xiaohongshu", session_dir)

    def _get_platform_domain(self) -> str:
        """获取平台域名"""
        return "xiaohongshu.com"

    async def check_login_status(self, page) -> bool:
        """检查是否已登录小红书

        Args:
            page: Playwright Page 对象

        Returns:
            是否已登录
        """
        try:
            # 获取当前页面的 cookies
            cookies = await page.context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            # 检查关键 cookie 是否存在
            if "web_session" not in cookie_dict:
                return False

            # 尝试访问页面验证登录状态
            current_url = page.url
            if "xiaohongshu.com" not in current_url:
                await page.goto(self.HOME_URL, wait_until="domcontentloaded", timeout=30000)

            await asyncio.sleep(2)

            # 检查是否存在用户头像（已登录标志）
            try:
                # 检查用户信息区域
                user_avatar = await page.query_selector('.user-avatar')
                if user_avatar:
                    return True

                # 备用检查：个人主页入口
                user_center = await page.query_selector('[class*="user"]')
                if user_center:
                    return True

                # 检查是否显示登录弹窗
                login_modal = await page.query_selector('.login-container')
                if login_modal:
                    return False

            except Exception:
                pass

            # 通过检查特定 API 响应来验证
            # 如果 web_session 有效，应该能获取用户信息
            return "web_session" in cookie_dict

        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False

    async def login(
        self,
        context,
        cookies: Optional[str] = None,
    ) -> bool:
        """执行登录

        Args:
            context: Playwright BrowserContext
            cookies: Cookie 字符串（优先使用）

        Returns:
            登录是否成功
        """
        # 优先使用 Cookie 登录
        if cookies:
            return await self._login_with_cookies(context, cookies)

        # 尝试加载已保存的 Session
        if self.has_saved_session():
            logger.info("尝试使用已保存的 Session...")
            if await self.load_session(context):
                page = await context.new_page()
                try:
                    if await self.check_login_status(page):
                        logger.info("Session 有效，已登录")
                        return True
                    else:
                        logger.warning("Session 已过期")
                finally:
                    await page.close()

        # 扫码登录
        return await self.scan_qr_login(context)

    async def _login_with_cookies(self, context, cookies_str: str) -> bool:
        """使用 Cookie 登录

        Args:
            context: Playwright BrowserContext
            cookies_str: Cookie 字符串

        Returns:
            登录是否成功
        """
        try:
            await self.import_cookies(cookies_str, context)

            # 验证登录状态
            page = await context.new_page()
            try:
                if await self.check_login_status(page):
                    # 保存 Session
                    await self.save_session(context)
                    logger.info("Cookie 登录成功")
                    return True
                else:
                    raise SessionExpiredError("Cookie 无效或已过期")
            finally:
                await page.close()

        except Exception as e:
            logger.error(f"Cookie 登录失败: {e}")
            raise

    async def scan_qr_login(self, context, timeout: int = 300) -> bool:
        """扫码登录

        打开登录页面显示二维码，等待用户扫码。

        Args:
            context: Playwright BrowserContext
            timeout: 等待超时（秒），默认 5 分钟

        Returns:
            登录是否成功
        """
        from ..browser.stealth import apply_stealth

        page = await context.new_page()

        try:
            await apply_stealth(page)

            logger.info("正在打开小红书...")
            await page.goto(self.HOME_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            # 检查是否需要登录
            if await self.check_login_status(page):
                logger.info("已登录，无需扫码")
                await self.save_session(context)
                return True

            # 点击登录按钮触发登录弹窗
            logger.info("正在打开登录弹窗...")
            try:
                login_btn = await page.query_selector('text="登录"')
                if login_btn:
                    await login_btn.click()
                    await asyncio.sleep(2)
            except Exception:
                pass

            # 切换到二维码登录
            logger.info("切换到二维码登录...")
            try:
                qr_tab = await page.query_selector('text="扫码登录"')
                if qr_tab:
                    await qr_tab.click()
                    await asyncio.sleep(2)
            except Exception:
                pass

            # 等待二维码出现
            logger.info("等待二维码...")
            logger.info("请使用小红书 App 扫描屏幕上的二维码")
            logger.info(f"等待登录（最多 {timeout} 秒）...")

            # 轮询检查登录状态
            check_interval = 5
            elapsed = 0

            while elapsed < timeout:
                await asyncio.sleep(check_interval)
                elapsed += check_interval

                if await self.check_login_status(page):
                    await self.save_session(context)
                    logger.info("扫码登录成功！")
                    return True

                # 检查二维码是否过期
                qr_expired = await page.query_selector('text="二维码已过期"')
                if qr_expired:
                    logger.info("二维码已过期，正在刷新...")
                    refresh_btn = await page.query_selector('text="刷新"')
                    if refresh_btn:
                        await refresh_btn.click()
                        await asyncio.sleep(2)

                remaining = timeout - elapsed
                if remaining > 0:
                    logger.debug(f"等待扫码... 剩余 {remaining} 秒")

            logger.warning("扫码登录超时")
            return False

        except Exception as e:
            logger.error(f"扫码登录失败: {e}")
            raise LoginError(f"扫码登录失败: {e}")

        finally:
            await page.close()

    async def interactive_login(self, context, headless: bool = False) -> bool:
        """交互式登录

        打开浏览器让用户手动登录，完成后自动保存 Session。

        Args:
            context: Playwright BrowserContext
            headless: 是否无头模式（交互登录应设为 False）

        Returns:
            登录是否成功
        """
        if headless:
            logger.warning("交互式登录不支持无头模式")

        # 扫码登录本身就是交互式的
        return await self.scan_qr_login(context)
