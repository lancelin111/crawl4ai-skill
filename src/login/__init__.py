"""登录模块 - 支持热门网站登录

提供 Cookie 注入、Session 持久化和反检测功能。

支持的平台：
- Twitter/X
- 小红书

Example:
    >>> from src.login import SessionManager, TwitterLogin
    >>> manager = SessionManager()
    >>> login = manager.get_login("twitter")
    >>> await login.import_cookies("auth_token=xxx", context)
"""

from .base import (
    LoginBase,
    LoginError,
    SessionExpiredError,
    CookieParseError,
)

from .twitter import TwitterLogin
from .xiaohongshu import XiaohongshuLogin

from .session_manager import (
    SessionManager,
    get_session_manager,
    get_supported_platforms,
    register_platform,
)

__all__ = [
    # 基类和异常
    "LoginBase",
    "LoginError",
    "SessionExpiredError",
    "CookieParseError",
    # 平台登录
    "TwitterLogin",
    "XiaohongshuLogin",
    # Session 管理
    "SessionManager",
    "get_session_manager",
    "get_supported_platforms",
    "register_platform",
]
