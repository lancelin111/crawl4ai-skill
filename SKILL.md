---
name: crawl4ai-skill
description: 智能搜索与爬取工具，基于 crawl4ai，支持 DuckDuckGo 搜索和全站爬取
version: 0.1.0
author: lancelin
repository: https://github.com/your-username/crawl4ai-skill
tags:
  - crawl
  - scrape
  - search
  - web-fetch
  - llm-friendly
requires:
  - python: ">=3.9"
  - bins:
      - crawl4ai-skill
install:
  - kind: pip
    package: .
    editable: true
  - kind: shell
    command: python -m playwright install chromium
---

# Crawl4AI Skill

智能搜索与爬取工具，为 OpenClaw 提供 DuckDuckGo 搜索和智能网页爬取能力。

## Features

- 🔍 DuckDuckGo 搜索（免 API key）
- 🕷️ 智能全站爬取（自动识别 sitemap/llms-full.txt）
- 📝 LLM 优化输出（Fit Markdown，去冗余）
- 🔗 引用和溯源（markdown_with_citations）
- ⚙️ 可配置深度和链接过滤

## Usage

### 搜索

```
搜索 "python web scraping" 相关内容
```

OpenClaw 会执行：
```bash
crawl4ai-skill search "python web scraping"
```

### 爬取单页

```
爬取 https://example.com 的内容
```

OpenClaw 会执行：
```bash
crawl4ai-skill crawl https://example.com
```

### 爬取全站

```
深度爬取 https://docs.example.com，最多50页
```

OpenClaw 会执行：
```bash
crawl4ai-skill crawl-site https://docs.example.com --max-pages 50
```

### 搜索并爬取

```
搜索 "AI tutorials" 并爬取前3个结果
```

OpenClaw 会执行：
```bash
crawl4ai-skill search-and-crawl "AI tutorials" --crawl-top 3
```

## Commands

| 命令 | 说明 | 示例 |
|------|------|------|
| `search <query>` | 搜索网页 | `crawl4ai-skill search "python"` |
| `crawl <url>` | 爬取单页 | `crawl4ai-skill crawl https://example.com` |
| `crawl-site <url>` | 爬取全站 | `crawl4ai-skill crawl-site https://docs.example.com` |
| `search-and-crawl <query>` | 搜索并爬取 | `crawl4ai-skill search-and-crawl "AI"` |

## Options

### 通用选项

- `-o, --output` - 输出文件或目录
- `-f, --format` - 输出格式（fit_markdown/markdown_with_citations/raw_markdown）

### 搜索选项

- `-n, --num-results` - 搜索结果数量（默认 10）

### 爬取选项

- `-w, --wait-for` - 等待元素加载（CSS selector）
- `-t, --timeout` - 超时时间（秒）

### 全站爬取选项

- `-d, --max-depth` - 最大爬取深度（默认 2）
- `-p, --max-pages` - 最大页面数量（默认 50）
- `-s, --strategy` - 爬取策略（auto/sitemap/recursive）
- `--include-external` - 包含外部链接

## Output Formats

### fit_markdown（推荐）

优化后的 Markdown，去除导航、广告等冗余内容，节省 token。适合 LLM 处理。

### markdown_with_citations

带引用列表的 Markdown，便于溯源和验证信息来源。

### raw_markdown

原始 Markdown 输出，保留完整内容。

## Installation

```bash
clawhub install crawl4ai-skill
```

## Examples

见 README.md 和 examples/ 目录。
