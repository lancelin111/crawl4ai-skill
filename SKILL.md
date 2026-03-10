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
    Session cookies are stored locally at ~/.crawl4ai-skill/sessions/<platform>.json
    Browser data is stored at ~/.crawl4ai-skill/browser_data/<platform>/
    All data is stored locally and never transmitted to external servers.
  recommendations:
    - Use disposable/test accounts for login
    - Clear shell history after passing cookies: history -c
    - Run session-clear when done to remove stored credentials
---

# Crawl4AI Skill

**集搜索、爬取、省Token、热门站登录为一身的智能工具。**

- 🔍 搜索 → 🕷️ 爬取 → 📝 LLM 优化 Markdown，一条龙服务
- 🔐 内置 Twitter/X、小红书等热门平台登录态爬取
- 💰 Fit Markdown 输出，大幅节省 Token 开销
- 📬 需要支持其他登录平台？[联系作者](https://github.com/lancelin111/crawl4ai-skill/issues)

## Features

- 🔍 DuckDuckGo 搜索（免 API key）
- 🕷️ 智能全站爬取（自动识别 sitemap/llms-full.txt）
- 📝 LLM 优化输出（Fit Markdown，去冗余）
- 🔐 **登录态爬取**（Twitter/X、小红书）
- 🐦 **推文提取**（支持引用推文 Quote Tweet）

## Usage

### 搜索

```
搜索 "python web scraping" 相关内容
```

```bash
crawl4ai-skill search "python web scraping"
```

### 爬取单页

```
爬取 https://example.com 的内容
```

```bash
crawl4ai-skill crawl https://example.com
```

### 爬取全站

```
深度爬取 https://docs.example.com，最多50页
```

```bash
crawl4ai-skill crawl-site https://docs.example.com --max-pages 50
```

### 登录 Twitter/X

```
登录 Twitter，Cookie: auth_token=xxx; ct0=yyy
```

```bash
crawl4ai-skill login twitter --cookies "auth_token=xxx; ct0=yyy"
```

### 爬取需要登录的页面

```
爬取 Elon Musk 的 Twitter 主页，提取推文
```

```bash
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --extract-tweets
```

### 查看登录状态

```
查看所有平台的登录状态
```

```bash
crawl4ai-skill session-status
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

## Options

### 登录选项

- `--cookies, -c` - Cookie 字符串（推荐）
- `--username, -u` - 用户名（Twitter）
- `--password, -p` - 密码（Twitter）

### 登录态爬取选项

- `--platform, -p` - 使用的平台（twitter/xiaohongshu）
- `--extract-tweets` - 提取推文模式（含引用推文）
- `--clean` - 清理模式（移除图片）

### 通用选项

- `-o, --output` - 输出文件
- `-f, --format` - 输出格式（fit_markdown/markdown_with_citations/raw_markdown）
- `-n, --num-results` - 搜索结果数量
- `-d, --max-depth` - 最大爬取深度
- `-p, --max-pages` - 最大页面数量

## Supported Platforms

| 平台 | 登录方式 | 说明 |
|------|----------|------|
| Twitter/X | Cookie 导入 | 推荐使用 auth_token + ct0 |
| 小红书 | 扫码登录 | 需要 App 扫码 |

## Installation

```bash
# 推荐：先 clone 检查代码
git clone https://github.com/lancelin111/crawl4ai-skill.git
cd crawl4ai-skill
pip install -e .
python -m playwright install chromium

# 或快速安装
pip install git+https://github.com/lancelin111/crawl4ai-skill.git
python -m playwright install chromium
```
