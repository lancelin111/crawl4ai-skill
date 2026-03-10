"""登录模块单元测试"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import sys
sys.path.insert(0, "/Users/lancelin/.openclaw/workspace-crawler/crawl4ai-skill")

from src.login.base import (
    LoginBase,
    LoginError,
    SessionExpiredError,
    CookieParseError,
)
from src.login.twitter import TwitterLogin
from src.login.xiaohongshu import XiaohongshuLogin
from src.login.session_manager import (
    SessionManager,
    get_session_manager,
    get_supported_platforms,
    register_platform,
)


class TestLoginExceptions:
    """登录异常测试"""

    def test_login_error_base_class(self):
        """测试基础异常类"""
        error = LoginError("test error")
        assert str(error) == "test error"
        assert isinstance(error, Exception)

    def test_session_expired_error(self):
        """测试 Session 过期异常"""
        error = SessionExpiredError("session expired")
        assert str(error) == "session expired"
        assert isinstance(error, LoginError)

    def test_cookie_parse_error(self):
        """测试 Cookie 解析异常"""
        error = CookieParseError("invalid cookie")
        assert str(error) == "invalid cookie"
        assert isinstance(error, LoginError)


class TestTwitterLogin:
    """Twitter 登录测试"""

    def test_init_default(self):
        """测试默认初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            assert login.platform == "twitter"
            assert login._get_platform_domain() == "twitter.com"

    def test_required_cookies(self):
        """测试必需 Cookie 列表"""
        assert "auth_token" in TwitterLogin.REQUIRED_COOKIES
        assert "ct0" in TwitterLogin.REQUIRED_COOKIES

    def test_has_no_session_initially(self):
        """测试初始无 Session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            assert not login.has_saved_session()

    def test_clear_nonexistent_session(self):
        """测试清除不存在的 Session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            # 不应抛出异常
            assert login.clear_session() is True


class TestXiaohongshuLogin:
    """小红书登录测试"""

    def test_init_default(self):
        """测试默认初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = XiaohongshuLogin(session_dir=Path(tmpdir))
            assert login.platform == "xiaohongshu"
            assert login._get_platform_domain() == "xiaohongshu.com"

    def test_required_cookies(self):
        """测试必需 Cookie 列表"""
        assert "web_session" in XiaohongshuLogin.REQUIRED_COOKIES


class TestSessionManager:
    """Session 管理器测试"""

    def test_init_creates_directory(self):
        """测试初始化创建目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir) / "sessions"
            manager = SessionManager(session_dir=session_dir)
            assert session_dir.exists()

    def test_get_login_twitter(self):
        """测试获取 Twitter 登录实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            login = manager.get_login("twitter")
            assert isinstance(login, TwitterLogin)

    def test_get_login_xiaohongshu(self):
        """测试获取小红书登录实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            login = manager.get_login("xiaohongshu")
            assert isinstance(login, XiaohongshuLogin)

    def test_get_login_alias(self):
        """测试平台别名"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            # Twitter 别名
            x_login = manager.get_login("x")
            assert isinstance(x_login, TwitterLogin)
            # 小红书别名
            xhs_login = manager.get_login("xhs")
            assert isinstance(xhs_login, XiaohongshuLogin)

    def test_get_login_unsupported(self):
        """测试不支持的平台"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            with pytest.raises(LoginError) as exc_info:
                manager.get_login("unsupported_platform")
            assert "不支持的平台" in str(exc_info.value)

    def test_get_supported_platforms(self):
        """测试获取支持的平台列表"""
        platforms = get_supported_platforms()
        assert "twitter" in platforms
        assert "xiaohongshu" in platforms

    def test_get_all_sessions_status(self):
        """测试获取所有 Session 状态"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            status = manager.get_all_sessions_status()
            # 应该包含所有支持的平台
            for platform in get_supported_platforms():
                assert platform in status
                assert "has_session" in status[platform]

    def test_is_logged_in_false(self):
        """测试未登录状态"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            assert not manager.is_logged_in("twitter")

    def test_clear_all_sessions(self):
        """测试清除所有 Session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=Path(tmpdir))
            results = manager.clear_all_sessions()
            # 所有平台都应该返回 True（无 Session 也算成功）
            for platform, success in results.items():
                assert success is True


class TestCookieParsing:
    """Cookie 解析测试"""

    @pytest.mark.asyncio
    async def test_parse_standard_cookies(self):
        """测试解析标准格式 Cookie"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))

            # 模拟 context
            mock_context = AsyncMock()
            mock_context.add_cookies = AsyncMock()

            cookies_str = "auth_token=abc123; ct0=xyz789"
            await login._import_standard_cookies(cookies_str, mock_context)

            # 验证 add_cookies 被调用
            mock_context.add_cookies.assert_called_once()
            cookies = mock_context.add_cookies.call_args[0][0]

            assert len(cookies) == 2
            cookie_dict = {c["name"]: c["value"] for c in cookies}
            assert cookie_dict["auth_token"] == "abc123"
            assert cookie_dict["ct0"] == "xyz789"

    @pytest.mark.asyncio
    async def test_parse_json_cookies(self):
        """测试解析 JSON 格式 Cookie"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))

            mock_context = AsyncMock()
            mock_context.add_cookies = AsyncMock()

            cookies_json = json.dumps([
                {"name": "auth_token", "value": "abc123"},
                {"name": "ct0", "value": "xyz789"},
            ])

            await login._import_json_cookies(cookies_json, mock_context)

            mock_context.add_cookies.assert_called_once()
            cookies = mock_context.add_cookies.call_args[0][0]

            assert len(cookies) == 2
            cookie_dict = {c["name"]: c["value"] for c in cookies}
            assert cookie_dict["auth_token"] == "abc123"

    @pytest.mark.asyncio
    async def test_parse_empty_cookies_raises_error(self):
        """测试空 Cookie 抛出错误"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            mock_context = AsyncMock()

            with pytest.raises(CookieParseError) as exc_info:
                await login.import_cookies("", mock_context)
            assert "为空" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_invalid_json_raises_error(self):
        """测试无效 JSON 抛出错误"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            mock_context = AsyncMock()

            with pytest.raises(CookieParseError) as exc_info:
                await login._import_json_cookies("[invalid json", mock_context)
            assert "JSON 解析失败" in str(exc_info.value)


class TestSessionPersistence:
    """Session 持久化测试"""

    @pytest.mark.asyncio
    async def test_save_and_load_session(self):
        """测试保存和加载 Session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))

            # 模拟 context
            mock_context = AsyncMock()
            mock_context.storage_state = AsyncMock(return_value={
                "cookies": [
                    {"name": "auth_token", "value": "abc123", "domain": ".twitter.com"},
                    {"name": "ct0", "value": "xyz789", "domain": ".twitter.com"},
                ],
                "origins": [],
            })

            # 保存 Session
            await login.save_session(mock_context)
            assert login.has_saved_session()

            # 获取 Session 信息
            info = login.get_session_info()
            assert info is not None
            assert info["platform"] == "twitter"
            assert info["cookie_count"] == 2
            assert "auth_token" in info["cookie_names"]

            # 加载 Session
            mock_context_2 = AsyncMock()
            mock_context_2.add_cookies = AsyncMock()

            success = await login.load_session(mock_context_2)
            assert success is True
            mock_context_2.add_cookies.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_nonexistent_session(self):
        """测试加载不存在的 Session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            mock_context = AsyncMock()

            success = await login.load_session(mock_context)
            assert success is False

    def test_get_session_info_no_session(self):
        """测试获取不存在的 Session 信息"""
        with tempfile.TemporaryDirectory() as tmpdir:
            login = TwitterLogin(session_dir=Path(tmpdir))
            info = login.get_session_info()
            assert info is None


class TestBrowserStealth:
    """浏览器 Stealth 测试"""

    def test_user_agents_list(self):
        """测试 User-Agent 列表"""
        from src.browser.stealth import USER_AGENTS, get_random_user_agent

        assert len(USER_AGENTS) > 0
        ua = get_random_user_agent()
        assert ua in USER_AGENTS
        assert "Mozilla" in ua

    @pytest.mark.asyncio
    async def test_apply_stealth_without_library(self):
        """测试无 playwright-stealth 时的处理"""
        from src.browser.stealth import apply_stealth

        mock_page = AsyncMock()

        # 即使没有 playwright-stealth 也不应抛出异常
        with patch.dict('sys.modules', {'playwright_stealth': None}):
            await apply_stealth(mock_page)  # 不应抛出异常
