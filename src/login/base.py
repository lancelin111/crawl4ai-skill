"""登录基类 - 定义登录接口

提供统一的登录接口，支持 Cookie 导入、Session 加密保存/加载。
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from .crypto import SessionEncryption

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

        self._session_file = self.session_dir / f"{platform}_session.enc"
        self._legacy_session_file = self.session_dir / f"{platform}_session.json"

        # 初始化加密模块
        self._crypto = SessionEncryption(session_dir)

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
        """保存 Session（加密存储 Cookies + Storage State）

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
                "encrypted": True,
            }

            # 加密并保存
            encrypted_content = self._crypto.encrypt(session_data)
            with open(self._session_file, "w", encoding="utf-8") as f:
                f.write(encrypted_content)

            # 设置文件权限为 600（仅用户可读写）
            os.chmod(self._session_file, 0o600)

            # 删除旧的未加密文件（如果存在）
            if self._legacy_session_file.exists():
                try:
                    self._legacy_session_file.unlink()
                    logger.info(f"已删除旧的未加密 Session 文件")
                except Exception:
                    pass

            encryption_type = "AES" if SessionEncryption.has_encryption_support() else "Base64"
            logger.info(f"Session 已加密保存 ({encryption_type}): {self._session_file}")

        except Exception as e:
            logger.error(f"保存 Session 失败: {e}")
            raise LoginError(f"保存 Session 失败: {e}")

    async def load_session(self, context) -> bool:
        """加载已保存的 Session（支持加密和旧格式）

        Args:
            context: Playwright BrowserContext

        Returns:
            是否成功加载
        """
        session_data = None

        # 优先尝试加载加密文件
        if self._session_file.exists():
            try:
                with open(self._session_file, "r", encoding="utf-8") as f:
                    encrypted_content = f.read()

                session_data = self._crypto.decrypt(encrypted_content)
                if session_data:
                    logger.info("已加载加密 Session")
            except Exception as e:
                logger.warning(f"加载加密 Session 失败: {e}")

        # 回退到旧的未加密格式
        if session_data is None and self._legacy_session_file.exists():
            try:
                with open(self._legacy_session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                logger.info("已加载旧格式 Session（将在下次保存时自动加密）")
            except Exception as e:
                logger.warning(f"加载旧格式 Session 失败: {e}")

        if session_data is None:
            logger.debug(f"未找到有效的 Session 文件")
            return False

        try:
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
        """清除保存的 Session（包括加密和旧格式）

        Returns:
            是否成功清除
        """
        cleared = False

        # 清除加密文件
        if self._session_file.exists():
            try:
                self._session_file.unlink()
                logger.info(f"加密 Session 已清除: {self._session_file}")
                cleared = True
            except Exception as e:
                logger.error(f"清除加密 Session 失败: {e}")

        # 清除旧格式文件
        if self._legacy_session_file.exists():
            try:
                self._legacy_session_file.unlink()
                logger.info(f"旧格式 Session 已清除: {self._legacy_session_file}")
                cleared = True
            except Exception as e:
                logger.error(f"清除旧格式 Session 失败: {e}")

        return cleared or not (self._session_file.exists() or self._legacy_session_file.exists())

    def has_saved_session(self) -> bool:
        """检查是否有保存的 Session

        Returns:
            是否存在保存的 Session
        """
        return self._session_file.exists() or self._legacy_session_file.exists()

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """获取保存的 Session 信息

        Returns:
            Session 信息（不含敏感数据）
        """
        session_data = None
        is_encrypted = False

        # 优先尝试加载加密文件
        if self._session_file.exists():
            try:
                with open(self._session_file, "r", encoding="utf-8") as f:
                    encrypted_content = f.read()
                session_data = self._crypto.decrypt(encrypted_content)
                is_encrypted = True
            except Exception:
                pass

        # 回退到旧格式
        if session_data is None and self._legacy_session_file.exists():
            try:
                with open(self._legacy_session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
            except Exception:
                pass

        if session_data is None:
            return None

        storage_state = session_data.get("storage_state", {})
        cookies = storage_state.get("cookies", [])

        return {
            "platform": session_data.get("platform"),
            "saved_at": session_data.get("saved_at"),
            "cookie_count": len(cookies),
            "cookie_names": [c.get("name") for c in cookies],
            "encrypted": is_encrypted,
            "encryption_type": "AES" if (is_encrypted and SessionEncryption.has_encryption_support()) else ("Base64" if is_encrypted else "None"),
        }
