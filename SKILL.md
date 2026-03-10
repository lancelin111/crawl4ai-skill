---
name: crawl4ai-skill
description: |
  集搜索、爬取、省Token、热门站登录为一身的智能工具。
  支持 DuckDuckGo 搜索 → 爬取 → 输出 LLM 优化的 Markdown，大幅节省 Token。
  内置 Twitter/X、小红书等热门平台登录态爬取。
  需要新增其他登录平台？欢迎联系作者：https://github.com/lancelin111
version: 0.1.0
author: lancelin
repository: https://github.com/lancelin111/crawl4ai-skill
tags:
  - crawl
  - scrape
  - search
  - markdown
  - save-token
  - twitter
  - xiaohongshu
  - login
requires:
  - python: ">=3.9"
  - bins:
      - crawl4ai-skill
      - playwright
install:
  - kind: pip
    package: git+https://github.com/lancelin111/crawl4ai-skill.git
  - kind: shell
    command: python -m playwright install chromium
security:
  credentials_storage: |
    Session cookies are stored locally at ~/.crawl4ai-skill/sessions/<platform>.json (permission 600)
    Browser data is stored at ~/.crawl4ai-skill/browser_data/<platform>/
    All data is stored locally and NEVER transmitted to external servers.
  input_methods:
    - Environment variables (recommended, not in shell history)
    - Interactive input (hidden input)
    - File with restricted permissions (chmod 600)
  recommendations:
    - Review code before installation
    - Use disposable/test accounts
    - Clear sessions when done: crawl4ai-skill session-clear
    - Do not use on public computers
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
- ✅ Session 文件权限设置为 `600`（仅用户可读写）
- ⚠️ **风险**：如果你的电脑被入侵，本地 cookies 可能被窃取

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

### 方式 1：审查后安装（推荐）

```bash
# 先克隆仓库，审查代码
git clone https://github.com/lancelin111/crawl4ai-skill.git
cd crawl4ai-skill

# 可选：使用 bandit 扫描安全问题
pip install bandit
bandit -r src/

# 确认无问题后安装
pip install -e .
python -m playwright install chromium
```

### 方式 2：快速安装（风险自负）

```bash
pip install git+https://github.com/lancelin111/crawl4ai-skill.git
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
