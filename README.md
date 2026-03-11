# Crawl4AI Skill

<p align="center">
  <strong>智能搜索与爬取工具 | LLM 优化输出</strong>
</p>

<p align="center">
  <a href="https://github.com/lancelin111/crawl4ai-skill/actions/workflows/security.yml">
    <img src="https://github.com/lancelin111/crawl4ai-skill/actions/workflows/security.yml/badge.svg" alt="Security Scan">
  </a>
  <a href="https://pypi.org/project/crawl4ai-skill/">
    <img src="https://img.shields.io/pypi/v/crawl4ai-skill" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/crawl4ai-skill/">
    <img src="https://img.shields.io/pypi/pyversions/crawl4ai-skill" alt="Python Version">
  </a>
  <a href="https://github.com/lancelin111/crawl4ai-skill/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
</p>

<p align="center">
  <a href="#安装">安装</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#命令参考">命令参考</a> •
  <a href="#致谢">致谢</a>
</p>

---

## 缘起

在使用 AI 助手处理信息时，我经常需要爬取网页内容。尝试了很多方案后，遇到了 [crawl4ai](https://github.com/unclecode/crawl4ai) —— 一个专为 LLM 设计的爬虫引擎，它的 **Fit Markdown** 输出简直是为 AI 量身定做的，去除了所有冗余内容，只保留核心信息。

这个项目就是这些探索的成果。希望能帮助到有同样需求的朋友。

## 特性

- 🔍 **DuckDuckGo 搜索** - 免 API key，快速搜索
- 🕷️ **智能爬取** - 自动识别 sitemap、递归爬取
- 📝 **LLM 优化输出** - Fit Markdown，节省 token
- ⚡ **动态页面支持** - 支持 JavaScript 渲染页面

## 安装

### 方式 1：PyPI（推荐）

```bash
pip install crawl4ai-skill
```

### 方式 2：skills.sh 生态（通用 Agent）

适用于 Claude、Copilot、通用 AI Agent：

```bash
npx skills add lancelin111/crawl4ai-skill@crawl4ai-skill
```

### 方式 3：ClawHub（OpenClaw 专用）

```bash
clawhub install crawl4ai-skill
```

**PyPI 包已通过：**
- ✅ PyPI 官方验证（Verified by PyPI）
- ✅ 自动化安全扫描（Bandit + pip-audit）
- ✅ 依赖项审查（所有依赖均为知名开源项目）

### 从源码安装（开发者/审计）

```bash
git clone https://github.com/lancelin111/crawl4ai-skill.git
cd crawl4ai-skill

# 可选：使用 bandit 审计代码
pip install bandit
bandit -r src/

# 安装
pip install -e .
```

## 快速开始

### 搜索

```bash
crawl4ai-skill search "python web scraping"
```

### 爬取网页

```bash
crawl4ai-skill crawl https://example.com -o page.md
```

### 爬取整站

```bash
crawl4ai-skill crawl-site https://docs.example.com --max-pages 50
```

### 搜索并爬取

```bash
crawl4ai-skill search-and-crawl "AI tutorials" --crawl-top 3
```

### 动态页面爬取

对于 JavaScript 渲染的动态页面（如雪球、知乎等），使用 `--wait-until` 和 `--delay` 参数：

```bash
# 等待网络空闲 + 额外等待 2 秒
crawl4ai-skill crawl https://xueqiu.com/S/BIDU --wait-until networkidle --delay 2

# 等待特定元素出现
crawl4ai-skill crawl https://example.com --wait-for ".content-loaded"
```

| 参数 | 说明 |
|------|------|
| `--wait-until` | 等待策略：`domcontentloaded`(默认), `networkidle`(推荐动态页面), `load`, `commit` |
| `--delay` | 返回前额外等待时间（秒） |
| `--wait-for` | 等待特定 CSS 选择器元素出现 |

## 命令参考

| 命令 | 说明 |
|------|------|
| `search <query>` | 搜索网页 |
| `crawl <url>` | 爬取单页 |
| `crawl-site <url>` | 爬取全站 |
| `search-and-crawl <query>` | 搜索并爬取 |

## 输出格式

| 格式 | 说明 |
|------|------|
| `fit_markdown` | 优化后的 Markdown，去除冗余（推荐） |
| `markdown_with_citations` | 带引用列表，便于溯源 |
| `raw_markdown` | 原始 Markdown |

## 致谢

这个项目的诞生，离不开以下优秀的开源项目：

### [crawl4ai](https://github.com/unclecode/crawl4ai)

**一个真正为 LLM 设计的爬虫引擎。**

当我第一次看到 crawl4ai 的 Fit Markdown 输出时，我被震撼了。它不是简单地把 HTML 转成 Markdown，而是智能地提取核心内容，去除导航、广告、侧边栏等噪音。这正是 AI 需要的输入格式 —— 干净、精炼、直击要点。

crawl4ai 的 `PruningContentFilter` 和 `DefaultMarkdownGenerator` 是本项目 Markdown 生成的核心。感谢 [@unclecode](https://github.com/unclecode) 创造了这个强大的工具。

### [duckduckgo-search](https://github.com/deedy5/duckduckgo_search)

免 API key 的搜索能力来自这个项目。简单、可靠、无需注册。

---

**如果这个项目对你有帮助，请给上面这些项目一个 Star**

它们才是真正的英雄。

## License

MIT License

## 作者

[@lancelin](https://github.com/lancelin111)

---

<p align="center">
  <em>Built with open source</em>
</p>
