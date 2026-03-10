"""登录基类 - 定义登录接口

提供统一的登录接口，支持 Cookie 导入、Session 保存/加载。
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class LoginError(Exception):
    """登录相关错误基类"""
    pass


class SessionExpiredError(LoginError):
    """Session 过期错误"""
    pass


class CookieParseError(LoginError):
    """Cookie 解析错误"""
    pass


class LoginBase(ABC):
    """登录基类

    定义统一的登录接口，所有平台登录类都应继承此类。

    Attributes:
        platform: 平台名称
        session_dir: Session 存储目录
    """

    def __init__(self, platform: str, session_dir: Optional[Path] = None):
        """初始化登录类

        Args:
            platform: 平台名称（如 twitter、xiaohongshu）
            session_dir: Session 存储目录，默认为 ~/.crawl4ai-skill/sessions
        """
        self.platform = platform

        if session_dir is None:
            session_dir = Path.home() / ".crawl4ai-skill" / "sessions"

        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self._session_file = self.session_dir / f"{platform}_session.json"

    @abstractmethod
    async def login(self, context, **kwargs) -> bool:
        """执行登录

        Args:
            context: Playwright BrowserContext
            **kwargs: 登录参数（Cookie、用户名密码等）

        Returns:
            登录是否成功
        """
        pass

    @abstractmethod
    async def check_login_status(self, page) -> bool:
        """检查登录状态

        Args:
            page: Playwright Page 对象

        Returns:
            是否已登录
        """
        pass

    @abstractmethod
    def _get_platform_domain(self) -> str:
        """获取平台域名

        Returns:
            平台域名（如 twitter.com）
        """
        pass

    async def save_session(self, context) -> None:
        """保存 Session（Cookies + Storage State）

        Args:
            context: Playwright BrowserContext
        """
        try:
            # 获取 storage state（包含 cookies 和 localStorage）
            storage_state = await context.storage_state()

            session_data = {
                "platform": self.platform,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "storage_state": storage_state,
            }

            with open(self._session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Session 已保存: {self._session_file}")

        except Exception as e:
            logger.error(f"保存 Session 失败: {e}")
            raise LoginError(f"保存 Session 失败: {e}")

    async def load_session(self, context) -> bool:
        """加载已保存的 Session

        Args:
            context: Playwright BrowserContext

        Returns:
            是否成功加载
        """
        if not self._session_file.exists():
            logger.debug(f"Session 文件不存在: {self._session_file}")
            return False

        try:
            with open(self._session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            storage_state = session_data.get("storage_state")
            if not storage_state:
                logger.warning("Session 文件格式无效")
                return False

            # 添加 cookies 到 context
            cookies = storage_state.get("cookies", [])
            if cookies:
                await context.add_cookies(cookies)

            logger.info(f"Session 已加载: {len(cookies)} 个 cookies")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Session 文件解析失败: {e}")
            return False
        except Exception as e:
            logger.error(f"加载 Session 失败: {e}")
            return False

    async def import_cookies(self, cookies_str: str, context) -> bool:
        """导入 Cookie 字符串

        支持多种格式：
        1. 标准格式: "key1=value1; key2=value2"
        2. JSON 格式: [{"name": "key1", "value": "value1", ...}]

        Args:
            cookies_str: Cookie 字符串
            context: Playwright BrowserContext

        Returns:
            是否成功导入
        """
        cookies_str = cookies_str.strip()

        if not cookies_str:
            raise CookieParseError("Cookie 字符串为空")

        # 尝试解析 JSON 格式
        if cookies_str.startswith("["):
            return await self._import_json_cookies(cookies_str, context)

        # 解析标准格式
        return await self._import_standard_cookies(cookies_str, context)

    async def _import_json_cookies(self, cookies_str: str, context) -> bool:
        """导入 JSON 格式的 Cookies

        Args:
            cookies_str: JSON 格式的 Cookie 字符串
            context: Playwright BrowserContext

        Returns:
            是否成功导入
        """
        try:
            cookies_list = json.loads(cookies_str)

            if not isinstance(cookies_list, list):
                raise CookieParseError("JSON 格式无效，期望数组")

            # 验证并补全 cookie 字段
            domain = self._get_platform_domain()
            processed_cookies = []

            for cookie in cookies_list:
                if not isinstance(cookie, dict):
                    continue

                name = cookie.get("name")
                value = cookie.get("value")

                if not name or value is None:
                    continue

                processed_cookie = {
                    "name": name,
                    "value": str(value),
                    "domain": cookie.get("domain", f".{domain}"),
                    "path": cookie.get("path", "/"),
                }

                # 可选字段
                if "expires" in cookie:
                    processed_cookie["expires"] = cookie["expires"]
                if "httpOnly" in cookie:
                    processed_cookie["httpOnly"] = cookie["httpOnly"]
                if "secure" in cookie:
                    processed_cookie["secure"] = cookie["secure"]
                if "sameSite" in cookie:
                    processed_cookie["sameSite"] = cookie["sameSite"]

                processed_cookies.append(processed_cookie)

            if not processed_cookies:
                raise CookieParseError("未找到有效的 Cookie")

            await context.add_cookies(processed_cookies)
            logger.info(f"已导入 {len(processed_cookies)} 个 JSON Cookies")
            return True

        except json.JSONDecodeError as e:
            raise CookieParseError(f"JSON 解析失败: {e}")

    async def _import_standard_cookies(self, cookies_str: str, context) -> bool:
        """导入标准格式的 Cookies

        格式: "key1=value1; key2=value2"

        Args:
            cookies_str: 标准格式的 Cookie 字符串
            context: Playwright BrowserContext

        Returns:
            是否成功导入
        """
        domain = self._get_platform_domain()
        cookies = []

        # 解析 cookie 字符串
        for part in cookies_str.split(";"):
            part = part.strip()
            if not part or "=" not in part:
                continue

            # 分割 key=value
            eq_index = part.index("=")
            name = part[:eq_index].strip()
            value = part[eq_index + 1:].strip()

            if not name:
                continue

            cookies.append({
                "name": name,
                "value": value,
                "domain": f".{domain}",
                "path": "/",
            })

        if not cookies:
            raise CookieParseError("未能解析出有效的 Cookie")

        await context.add_cookies(cookies)
        logger.info(f"已导入 {len(cookies)} 个标准格式 Cookies")
        return True

    def clear_session(self) -> bool:
        """清除保存的 Session

        Returns:
            是否成功清除
        """
        if self._session_file.exists():
            try:
                self._session_file.unlink()
                logger.info(f"Session 已清除: {self._session_file}")
                return True
            except Exception as e:
                logger.error(f"清除 Session 失败: {e}")
                return False
        return True

    def has_saved_session(self) -> bool:
        """检查是否有保存的 Session

        Returns:
            是否存在保存的 Session
        """
        return self._session_file.exists()

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """获取保存的 Session 信息

        Returns:
            Session 信息（不含敏感数据）
        """
        if not self._session_file.exists():
            return None

        try:
            with open(self._session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            storage_state = session_data.get("storage_state", {})
            cookies = storage_state.get("cookies", [])

            return {
                "platform": session_data.get("platform"),
                "saved_at": session_data.get("saved_at"),
                "cookie_count": len(cookies),
                "cookie_names": [c.get("name") for c in cookies],
            }
        except Exception:
            return None
