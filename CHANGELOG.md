# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-10

### Added

- 🔐 **登录功能** - 支持热门网站登录，保存 Session 后可爬取需要登录的页面
  - Twitter/X 登录（Cookie 导入、用户名密码）
  - 小红书登录（Cookie 导入、扫码）
- 🛡️ **反检测** - Playwright Stealth 配置
  - User-Agent 轮换池
  - 隐藏自动化特征
- 📦 **Session 管理**
  - 统一管理所有平台的登录状态
  - JSON 格式存储 Cookies 和 Storage State
- 🖥️ **新增 CLI 命令**
  - `login` - 登录指定平台
  - `session-status` - 查看所有平台登录状态
  - `session-clear` - 清除保存的 Session
  - `crawl-with-login` - 使用已保存 Session 爬取页面

### Technical

- 新增 `src/browser/` 模块（Stealth 配置）
- 新增 `src/login/` 模块（登录基类、平台实现、Session 管理）
- 新增 `playwright-stealth` 和 `aiohttp` 依赖
- 新增 25+ 个登录模块单元测试

## [0.1.1] - 2026-03-10

### Added

- 🛡️ URL 验证功能（`validate_url` 函数和 `InvalidURLError` 异常）
- 🔄 HTTP 错误处理（`HTTPError` 异常，包含状态码）
- 📁 Sitemap Index 支持（嵌套 sitemap 递归解析）
- ⚠️ 限流错误处理（`RateLimitError` 异常）
- 🛑 优雅中断处理（Ctrl+C 信号处理，保存已完成结果）
- ✅ 参数验证（`crawl-top` 不能超过 `num-results`）
- 📝 空结果处理（搜索无结果时的友好提示）
- 🔒 文件权限错误处理

### Changed

- ⏱️ 优化请求延迟策略：从"每 5 个请求延迟 1 秒"改为"每个请求随机延迟 0.1~0.3 秒"
  - 参考 crawl4ai 官方默认配置（mean_delay=0.1, max_range=0.3）
  - 更快：平均延迟从 0.2 秒/请求 优化为更平滑的体验
  - 更自然：随机延迟模拟人类行为，降低被检测风险

### Fixed

- 修复 sitemap/txt 获取时的 HTTP 错误处理
- 修复空 sitemap/txt 文件的处理
- 改进 CLI 错误提示信息

### Technical

- 新增 10 个单元测试（URL 验证、错误类）
- 测试总数从 45 增加到 57 个

## [0.1.0] - 2026-03-10

### Added

- 🔍 DuckDuckGo 搜索功能（免 API key）
- 🕷️ 单页爬取功能
- 🌐 智能全站爬取（支持 sitemap、llms-full.txt、递归策略）
- 📝 多种 Markdown 输出格式（fit_markdown、markdown_with_citations、raw_markdown）
- 🔗 搜索并爬取组合功能
- ⚙️ CLI 命令行工具
- 📖 完整文档和示例

### Technical

- 基于 crawl4ai 0.8.0
- 兼容 ddgs（原 duckduckgo-search）搜索库
- 支持 Python 3.9+
- 45 个单元测试
