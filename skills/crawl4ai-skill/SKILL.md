---
name: crawl4ai-skill
description: 智能搜索与爬取工具，输出 LLM 优化 Markdown，Token 降低 80%。支持 DuckDuckGo 搜索、全站爬取。
version: 0.3.0
author: Lancelin
license: MIT-0
repository: https://github.com/lancelin111/crawl4ai-skill
homepage: https://github.com/lancelin111/crawl4ai-skill
pypi: crawl4ai-skill
issues: https://github.com/lancelin111/crawl4ai-skill/issues
tags:
  - web-scraping
  - search
  - markdown
  - llm
  - token-optimization
requires:
  bins:
    - crawl4ai-skill
---

# Crawl4AI Skill

**智能搜索与爬取 | LLM 优化输出 | 省 Token 80%**

## 核心功能

- 🔍 **DuckDuckGo 搜索** - 免 API key，零配置
- 🕷️ **智能全站爬取** - 自动识别 sitemap/递归爬取
- 📝 **LLM 优化输出** - Fit Markdown 格式，节省 80% Token
- ⚡ **动态页面支持** - JavaScript 渲染页面爬取

---

## 快速开始

### 安装

```bash
pip install crawl4ai-skill
```

### 基础使用

```bash
# 搜索网页
crawl4ai-skill search "python async programming"

# 爬取单页
crawl4ai-skill crawl https://docs.python.org/3/library/asyncio.html

# 爬取全站
crawl4ai-skill crawl-site https://docs.python.org --max-pages 50
```

---

## 使用场景

### 场景 1：为 LLM 准备干净文档

```bash
# 爬取文档站，输出 LLM 优化 Markdown
crawl4ai-skill crawl-site https://docs.fastapi.com --max-pages 100 -o ./fastapi-docs
```

**优化效果：**
- ❌ 移除：导航栏、侧边栏、广告
- ✅ 保留：标题、正文、代码块
- 📊 **Token：50,000 → 10,000（-80%）**

### 场景 2：搜索+爬取

```bash
# 搜索主题，自动爬取前 3 个结果
crawl4ai-skill search-and-crawl "Vue 3 best practices" --crawl-top 3
```

### 场景 3：动态页面爬取

对于 JavaScript 渲染的页面（雪球、知乎等）：

```bash
# 等待网络空闲 + 额外等待 2 秒
crawl4ai-skill crawl https://xueqiu.com/S/BIDU --wait-until networkidle --delay 2
```

---

## 输出格式

### fit_markdown（推荐）

去冗余，节省 80% Token。

```bash
crawl4ai-skill crawl https://example.com --format fit_markdown
```

### raw_markdown

保留完整 HTML 结构。

```bash
crawl4ai-skill crawl https://example.com --format raw_markdown
```

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `search <query>` | 搜索网页 |
| `crawl <url>` | 爬取单页 |
| `crawl-site <url>` | 爬取全站 |
| `search-and-crawl <query>` | 搜索并爬取 |

### 常用参数

```bash
# 搜索
--num-results 10          # 返回数量

# 爬取
--format fit_markdown     # 输出格式
--output result.md        # 输出文件
--wait-until networkidle  # 等待策略（动态页面推荐）
--delay 2                 # 额外等待时间（秒）
--wait-for ".selector"    # 等待特定元素

# 全站爬取
--max-pages 100          # 最多爬取页面数
--max-depth 3            # 最大递归深度
```

---

## 链接

- 📦 [PyPI](https://pypi.org/project/crawl4ai-skill/)
- 💻 [GitHub](https://github.com/lancelin111/crawl4ai-skill)
