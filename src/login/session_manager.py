"""Session 管理器 - 统一管理所有平台的登录 Session

提供平台注册、Session 状态查询等功能。
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Type, List, Any

from .base import LoginBase, LoginError

logger = logging.getLogger(__name__)


# 平台注册表
_PLATFORM_REGISTRY: Dict[str, Type[LoginBase]] = {}


def _register_builtin_platforms() -> None:
    """注册内置平台（模块级别）"""
    try:
        from .twitter import TwitterLogin
        _PLATFORM_REGISTRY["twitter"] = TwitterLogin
        _PLATFORM_REGISTRY["x"] = TwitterLogin  # 别名
    except ImportError:
        pass

    try:
        from .xiaohongshu import XiaohongshuLogin
        _PLATFORM_REGISTRY["xiaohongshu"] = XiaohongshuLogin
        _PLATFORM_REGISTRY["xhs"] = XiaohongshuLogin  # 别名
        _PLATFORM_REGISTRY["redbook"] = XiaohongshuLogin  # 别名
    except ImportError:
        pass


# 模块导入时自动注册平台
_register_builtin_platforms()


def register_platform(name: str, login_class: Type[LoginBase]) -> None:
    """注册平台登录类

    Args:
        name: 平台名称
        login_class: 登录类
    """
    _PLATFORM_REGISTRY[name.lower()] = login_class


def get_platform_class(name: str) -> Optional[Type[LoginBase]]:
    """获取平台登录类

    Args:
        name: 平台名称

    Returns:
        登录类，不存在则返回 None
    """
    return _PLATFORM_REGISTRY.get(name.lower())


def get_supported_platforms() -> List[str]:
    """获取支持的平台列表

    Returns:
        平台名称列表
    """
    return list(_PLATFORM_REGISTRY.keys())


class SessionManager:
    """Session 管理器

    统一管理所有平台的登录 Session。

    Example:
        >>> manager = SessionManager()
        >>> # 获取登录实例
        >>> twitter_login = manager.get_login("twitter")
        >>> # 查看所有 Session 状态
        >>> status = manager.get_all_sessions_status()
    """

    def __init__(self, session_dir: Optional[Path] = None):
        """初始化 Session 管理器

        Args:
            session_dir: Session 存储目录，默认为 ~/.crawl4ai-skill/sessions
        """
        if session_dir is None:
            session_dir = Path.home() / ".crawl4ai-skill" / "sessions"

        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # 登录实例缓存
        self._login_instances: Dict[str, LoginBase] = {}

    def get_login(self, platform: str) -> LoginBase:
        """获取指定平台的登录实例

        Args:
            platform: 平台名称

        Returns:
            登录实例

        Raises:
            LoginError: 平台不支持
        """
        platform = platform.lower()

        # 检查缓存
        if platform in self._login_instances:
            return self._login_instances[platform]

        # 获取登录类
        login_class = get_platform_class(platform)
        if login_class is None:
            supported = ", ".join(get_supported_platforms())
            raise LoginError(f"不支持的平台: {platform}，支持: {supported}")

        # 创建实例
        instance = login_class(session_dir=self.session_dir)
        self._login_instances[platform] = instance

        return instance

    def get_all_sessions_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有平台的 Session 状态

        Returns:
            {platform: {has_session, info}}
        """
        status = {}

        for platform in get_supported_platforms():
            try:
                login = self.get_login(platform)
                has_session = login.has_saved_session()
                info = login.get_session_info() if has_session else None

                status[platform] = {
                    "has_session": has_session,
                    "info": info,
                }
            except Exception as e:
                status[platform] = {
                    "has_session": False,
                    "error": str(e),
                }

        return status

    def clear_session(self, platform: str) -> bool:
        """清除指定平台的 Session

        Args:
            platform: 平台名称

        Returns:
            是否成功
        """
        try:
            login = self.get_login(platform)
            return login.clear_session()
        except Exception as e:
            logger.error(f"清除 {platform} Session 失败: {e}")
            return False

    def clear_all_sessions(self) -> Dict[str, bool]:
        """清除所有 Session

        Returns:
            {platform: success}
        """
        results = {}
        for platform in get_supported_platforms():
            results[platform] = self.clear_session(platform)
        return results

    def is_logged_in(self, platform: str) -> bool:
        """检查平台是否有有效 Session

        注意：这只检查 Session 文件是否存在，不验证是否有效。

        Args:
            platform: 平台名称

        Returns:
            是否有 Session
        """
        try:
            login = self.get_login(platform)
            return login.has_saved_session()
        except Exception:
            return False


# 默认全局管理器
_default_manager: Optional[SessionManager] = None


def get_session_manager(session_dir: Optional[Path] = None) -> SessionManager:
    """获取默认 Session 管理器

    Args:
        session_dir: Session 存储目录

    Returns:
        SessionManager 实例
    """
    global _default_manager

    if _default_manager is None or session_dir is not None:
        _default_manager = SessionManager(session_dir)

    return _default_manager
