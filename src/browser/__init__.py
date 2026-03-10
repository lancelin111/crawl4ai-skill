"""浏览器模块 - Playwright Stealth 配置

提供反检测浏览器配置和 User-Agent 轮换。
"""

from .stealth import (
    apply_stealth,
    create_stealth_context,
    get_random_user_agent,
    USER_AGENTS,
)

__all__ = [
    "apply_stealth",
    "create_stealth_context",
    "get_random_user_agent",
    "USER_AGENTS",
]
