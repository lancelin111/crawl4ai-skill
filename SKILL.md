---
name: crawl4ai-skill
description: |
  爬 Twitter 推文、小红书笔记不再被拦截。Playwright Stealth + 加密 Session 管理，一次登录持久使用。同时支持 DuckDuckGo 搜索→爬取→Fit Markdown 一条龙，Token 省 80%。pip install crawl4ai-skill 开箱即用。
version: 0.2.0
author: Lancelin
license: MIT
repository: https://github.com/lancelin111/crawl4ai-skill
homepage: https://github.com/lancelin111/crawl4ai-skill
pypi: crawl4ai-skill
issues: https://github.com/lancelin111/crawl4ai-skill/issues
tags:
  - web-scraping
  - search
  - twitter
  - xiaohongshu
  - openclaw
  - crawl4ai
  - markdown
  - llm
  - token-optimization
requires:
  python: ">=3.9"
  packages:
    - crawl4ai>=0.4.0
    - playwright>=1.40.0
    - duckduckgo-search>=6.0.0
    - playwright-stealth>=1.0.0
    - cryptography>=41.0.0
  bins:
    - crawl4ai-skill
    - playwright
install:
  - kind: pip
    package: crawl4ai-skill
    verified: true
    note: "Recommended: PyPI package verified by Python Package Index"
  - kind: shell
    command: python -m playwright install chromium
security:
  encryption: AES-128-CBC
  storage: local-only
  verified: true
  credentials_storage: |
    Session cookies are AES-128-CBC encrypted and stored at ~/.crawl4ai-skill/sessions/<platform>_session.enc
    Encryption key is derived from machine identifier (MAC + hostname, cannot be decrypted on other machines)
    Browser data stored at ~/.crawl4ai-skill/browser_data/<platform>/
    All data stored locally, NEVER transmitted to external servers.
  automated_scans:
    - Bandit security scan on every commit
    - pip-audit dependency vulnerability check
    - GitHub Dependabot enabled
  input_methods:
    - Environment variables (⭐⭐⭐ recommended, not in shell history)
    - Interactive input (⭐⭐⭐ hidden input)
    - File with chmod 600 (⭐⭐ secure if protected)
    - Command line parameter (⭐ not recommended)
  recommendations:
    - Review code before installation (see SECURITY.md)
    - Use disposable/test accounts for initial testing
    - Use environment variables for credentials
    - Clear sessions when done: crawl4ai-skill session-clear
    - Do not use on public computers
    - Keep package updated
---

# Crawl4AI Skill

**集搜索、爬取、省Token、热门站登录为一身的智能工具。**

## 🔒 安全说明（必读）

### 代码透明度
- ✅ 本项目**完全开源**，所有代码可在 [GitHub](https://github.com/lancelin111/crawl4ai-skill) 审查
- ✅ **推荐**先克隆仓库审查代码，再安装
- ✅ 可使用 `bandit` 工具扫描安全问题

### 数据隐私
- ✅ **所有数据仅存储在本地**（`~/.crawl4ai-skill/`）
- ✅ **绝不上传**任何数据到第三方服务器
- ✅ Session 文件使用 **AES-128 加密存储**
- ✅ 加密密钥基于机器标识符派生（无法在其他机器解密）
- ✅ 文件权限设置为 `600`（仅用户可读写）
- ✅ 查看加密状态：`crawl4ai-skill session-status`

### 凭证管理
- ✅ 支持**环境变量**传递 cookies（不会记录在 shell history）
- ✅ 支持**交互式输入**（输入时不显示）
- ✅ 支持**从文件读取**（需设置 chmod 600）
- ⚠️ **不推荐**在命令行直接传递敏感信息

### 使用建议
- 🔍 **使用前**先审查代码
- 🔐 使用完毕后及时清理：`crawl4ai-skill session-clear`
- 💻 不要在公共电脑上使用
- 🔄 定期更新到最新版本

### 责任声明
- 本工具仅供学习和研究使用
- 使用者需自行承担法律责任
- 作者不对数据安全问题负责

---

## Features

- 🔍 DuckDuckGo 搜索（免 API key）
- 🕷️ 智能全站爬取（自动识别 sitemap/llms-full.txt）
- 📝 LLM 优化输出（Fit Markdown，去冗余）
- 🔐 **登录态爬取**（Twitter/X、小红书）
- 🐦 **推文提取**（支持引用推文 Quote Tweet）

## Installation

### ✅ 推荐方式：PyPI（已验证）

```bash
pip install crawl4ai-skill
python -m playwright install chromium
```

**PyPI 包已通过：**
- ✅ PyPI 官方验证（Verified by PyPI）
- ✅ 自动化安全扫描（Bandit + pip-audit）
- ✅ 依赖项审查（所有依赖均为知名开源项目）
- ✅ 查看安全报告：[SECURITY.md](https://github.com/lancelin111/crawl4ai-skill/blob/main/SECURITY.md)

### 从源码安装（开发者/审计）

```bash
git clone https://github.com/lancelin111/crawl4ai-skill.git
cd crawl4ai-skill

# 可选：使用 bandit 审计代码
pip install bandit
bandit -r src/

# 安装
pip install -e .
python -m playwright install chromium
```

## Usage

### 搜索

```bash
crawl4ai-skill search "python web scraping"
```

### 爬取单页

```bash
crawl4ai-skill crawl https://example.com
```

### 爬取全站

```bash
crawl4ai-skill crawl-site https://docs.example.com --max-pages 50
```

## 登录 Twitter/X

### 推荐方式：环境变量

```bash
export TWITTER_COOKIES="auth_token=xxx; ct0=yyy"
crawl4ai-skill login twitter
```

### 交互式方式

```bash
crawl4ai-skill login twitter --interactive
# 会提示输入 cookies（输入时不显示）
```

### 从文件读取

```bash
echo "auth_token=xxx; ct0=yyy" > ~/.twitter-cookies
chmod 600 ~/.twitter-cookies
crawl4ai-skill login twitter --cookies-file ~/.twitter-cookies
```

## 登录态爬取

```bash
# 爬取 Twitter 用户页面
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter

# 提取推文（包含引用推文）
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --extract-tweets
```

## 查看/清除登录状态

```bash
# 查看状态
crawl4ai-skill session-status

# 清除所有登录信息
crawl4ai-skill session-clear --all
```

## Commands

| 命令 | 说明 |
|------|------|
| `search <query>` | 搜索网页 |
| `crawl <url>` | 爬取单页 |
| `crawl-site <url>` | 爬取全站 |
| `search-and-crawl <query>` | 搜索并爬取 |
| `login <platform>` | 登录平台 |
| `crawl-with-login <url>` | 登录态爬取 |
| `session-status` | 查看登录状态 |
| `session-clear` | 清除登录信息 |

## Supported Platforms

| 平台 | 登录方式 | 说明 |
|------|----------|------|
| Twitter/X | Cookie/环境变量/文件 | 推荐使用 auth_token + ct0 |
| 小红书 | 扫码登录 | 需要 App 扫码 |
