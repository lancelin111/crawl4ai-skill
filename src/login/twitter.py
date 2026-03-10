"""Twitter/X 登录模块

支持 Cookie 导入和用户名密码登录。
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from .base import LoginBase, LoginError, SessionExpiredError

logger = logging.getLogger(__name__)


class TwitterLogin(LoginBase):
    """Twitter/X 登录类

    支持两种登录方式：
    1. Cookie 导入（推荐）- 最稳定，无验证码
    2. 用户名密码登录 - 可能触发验证码

    Example:
        >>> login = TwitterLogin()
        >>> async with async_playwright() as p:
        ...     browser = await p.chromium.launch()
        ...     context = await browser.new_context()
        ...     # 方式1: Cookie 导入
        ...     await login.import_cookies("auth_token=xxx; ct0=yyy", context)
        ...     # 方式2: 用户名密码
        ...     await login.login(context, username="user", password="pass")
    """

    # Twitter 登录关键 Cookie
    REQUIRED_COOKIES = ["auth_token", "ct0"]

    # 登录页面 URL
    LOGIN_URL = "https://twitter.com/i/flow/login"
    HOME_URL = "https://twitter.com/home"

    def __init__(self, session_dir: Optional[Path] = None):
        """初始化 Twitter 登录

        Args:
            session_dir: Session 存储目录
        """
        super().__init__("twitter", session_dir)

    def _get_platform_domain(self) -> str:
        """获取平台域名"""
        return "twitter.com"

    async def check_login_status(self, page) -> bool:
        """检查是否已登录 Twitter

        Args:
            page: Playwright Page 对象

        Returns:
            是否已登录
        """
        try:
            # 获取当前页面的 cookies
            cookies = await page.context.cookies()
            cookie_names = {c["name"] for c in cookies}

            # 检查关键 cookie 是否存在
            has_required = all(name in cookie_names for name in self.REQUIRED_COOKIES)

            if not has_required:
                return False

            # 尝试访问主页验证登录状态
            current_url = page.url
            if "twitter.com" not in current_url:
                await page.goto(self.HOME_URL, wait_until="domcontentloaded", timeout=30000)

            # 检查是否被重定向到登录页
            await asyncio.sleep(2)
            final_url = page.url

            if "/login" in final_url or "/i/flow/login" in final_url:
                return False

            # 检查是否存在首页特征元素
            try:
                # 检查是否存在发推按钮或侧边栏
                home_indicator = await page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
                if home_indicator:
                    return True

                # 备用检查：主内容区域
                main_content = await page.query_selector('[data-testid="primaryColumn"]')
                if main_content:
                    return True

            except Exception:
                pass

            return False

        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False

    async def login(
        self,
        context,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cookies: Optional[str] = None,
    ) -> bool:
        """执行登录

        Args:
            context: Playwright BrowserContext
            username: 用户名/邮箱/手机号
            password: 密码
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

        # 用户名密码登录
        if username and password:
            return await self._login_with_credentials(context, username, password)

        # 交互式登录（打开浏览器让用户手动登录）
        return await self.interactive_login(context)

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

    async def _login_with_credentials(
        self,
        context,
        username: str,
        password: str,
    ) -> bool:
        """使用用户名密码登录

        注意：可能触发验证码，需要用户手动处理。

        Args:
            context: Playwright BrowserContext
            username: 用户名
            password: 密码

        Returns:
            登录是否成功
        """
        from ..browser.stealth import apply_stealth

        page = await context.new_page()

        try:
            # 应用 Stealth
            await apply_stealth(page)

            # 访问登录页
            logger.info("正在打开 Twitter 登录页...")
            await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            # 输入用户名
            logger.info("输入用户名...")
            username_input = await page.wait_for_selector(
                'input[autocomplete="username"]',
                timeout=30000
            )
            await username_input.fill(username)
            await asyncio.sleep(1)

            # 点击下一步
            next_button = await page.query_selector('[role="button"]:has-text("Next")')
            if not next_button:
                next_button = await page.query_selector('[role="button"]:has-text("下一步")')
            if next_button:
                await next_button.click()
                await asyncio.sleep(2)

            # 检查是否需要验证（如手机号/邮箱验证）
            unusual_activity = await page.query_selector('text="unusual login activity"')
            if unusual_activity:
                logger.warning("检测到异常登录活动验证，请手动处理...")
                logger.info("请在浏览器中完成验证，完成后按 Enter 继续...")
                # 在 CLI 模式下等待用户处理
                await asyncio.sleep(60)  # 给用户 60 秒处理

            # 输入密码
            logger.info("输入密码...")
            password_input = await page.wait_for_selector(
                'input[name="password"]',
                timeout=30000
            )
            await password_input.fill(password)
            await asyncio.sleep(1)

            # 点击登录
            login_button = await page.query_selector('[data-testid="LoginForm_Login_Button"]')
            if login_button:
                await login_button.click()
                await asyncio.sleep(5)

            # 检查登录结果
            if await self.check_login_status(page):
                await self.save_session(context)
                logger.info("用户名密码登录成功")
                return True
            else:
                # 检查错误信息
                error_msg = await page.query_selector('[data-testid="toast"]')
                if error_msg:
                    error_text = await error_msg.text_content()
                    raise LoginError(f"登录失败: {error_text}")
                raise LoginError("登录失败，请检查用户名和密码")

        except Exception as e:
            logger.error(f"用户名密码登录失败: {e}")
            raise

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
        from ..browser.stealth import apply_stealth

        if headless:
            logger.warning("交互式登录不支持无头模式")

        page = await context.new_page()

        try:
            await apply_stealth(page)

            logger.info("正在打开 Twitter 登录页...")
            logger.info("请在浏览器中完成登录...")

            await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

            # 等待用户完成登录
            logger.info("等待用户登录（最多 5 分钟）...")

            for _ in range(60):  # 最多等待 5 分钟
                await asyncio.sleep(5)

                if await self.check_login_status(page):
                    await self.save_session(context)
                    logger.info("登录成功，Session 已保存")
                    return True

            logger.warning("登录超时")
            return False

        except Exception as e:
            logger.error(f"交互式登录失败: {e}")
            raise

        finally:
            await page.close()
