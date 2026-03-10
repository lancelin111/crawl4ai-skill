---
name: crawl4ai-skill
description: 智能搜索与爬取工具，基于 crawl4ai，支持登录态爬取 Twitter/X、小红书等平台
version: 0.1.0
author: lancelin
repository: https://github.com/lancelin111/crawl4ai-skill
tags:
  - crawl
  - scrape
  - search
  - twitter
  - xiaohongshu
  - login
requires:
  - python: ">=3.9"
  - bins:
      - crawl4ai-skill
install:
  - kind: shell
    command: |
      pip install git+https://github.com/lancelin111/crawl4ai-skill.git
      python -m playwright install chromium
---

# Crawl4AI Skill

智能搜索与爬取工具，为 OpenClaw 提供 DuckDuckGo 搜索、智能网页爬取，以及 **登录态爬取** 能力（支持 Twitter/X、小红书）。

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
# 一键安装
curl -fsSL https://raw.githubusercontent.com/lancelin111/crawl4ai-skill/main/install.sh | bash

# 或手动安装
pip install git+https://github.com/lancelin111/crawl4ai-skill.git
python -m playwright install chromium
```
