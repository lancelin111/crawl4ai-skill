# Crawl4AI Skill

<p align="center">
  <strong>智能搜索与爬取工具 | 支持登录态爬取 Twitter/X、小红书</strong>
</p>

<p align="center">
  <a href="#安装">安装</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#登录态爬取">登录态爬取</a> •
  <a href="#致谢">致谢</a>
</p>

---

## 缘起

在使用 AI 助手处理信息时，我经常需要爬取网页内容。尝试了很多方案后，遇到了 [crawl4ai](https://github.com/unclecode/crawl4ai) —— 一个专为 LLM 设计的爬虫引擎，它的 **Fit Markdown** 输出简直是为 AI 量身定做的，去除了所有冗余内容，只保留核心信息。

但在实际使用中，我遇到了一个痛点：**很多有价值的内容需要登录才能访问**。

Twitter/X 上的推文、小红书的笔记... 这些平台的反爬措施很严格，普通的爬虫根本无法获取登录后的内容。crawl4ai 的 `storage_state` 参数理论上支持 Cookie 注入，但在 Twitter 等平台上会被反自动化检测拦截。

经过反复尝试，我找到了一个可行的方案：**Playwright 持久化上下文 + crawl4ai Markdown 生成器**。用 Playwright 绕过反检测加载页面，再用 crawl4ai 的强大能力转换为干净的 Markdown。

这个项目就是这些探索的成果。希望能帮助到有同样需求的朋友。

## 特性

- 🔍 **DuckDuckGo 搜索** - 免 API key，快速搜索
- 🕷️ **智能爬取** - 自动识别 sitemap、递归爬取
- 📝 **LLM 优化输出** - Fit Markdown，节省 token
- 🔐 **登录态爬取** - 支持 Twitter/X、小红书
- 🐦 **推文提取** - 支持引用推文 (Quote Tweet)
- 🛡️ **反检测** - Playwright Stealth 模式

## 安装

### 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/lancelin111/crawl4ai-skill/main/install.sh | bash
```

### 手动安装

```bash
pip install git+https://github.com/lancelin111/crawl4ai-skill.git
python -m playwright install chromium
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

## 登录态爬取

这是本项目的核心功能 —— 爬取需要登录的页面。

### 第一步：登录

**Twitter/X（Cookie 方式，推荐）：**

1. 在浏览器中登录 Twitter
2. 打开开发者工具 (F12) → Application → Cookies
3. 复制 `auth_token` 和 `ct0` 的值

```bash
crawl4ai-skill login twitter --cookies "auth_token=xxx; ct0=yyy"
```

**小红书（扫码方式）：**

```bash
crawl4ai-skill login xiaohongshu
# 会打开浏览器，用 App 扫码登录
```

### 第二步：爬取

```bash
# 爬取 Twitter 用户页面
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter

# 提取推文（包含引用推文）
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --extract-tweets

# 爬取小红书笔记
crawl4ai-skill crawl-with-login https://www.xiaohongshu.com/explore/xxx -p xiaohongshu
```

### 查看登录状态

```bash
crawl4ai-skill session-status
```

### 清除登录信息

```bash
crawl4ai-skill session-clear twitter
crawl4ai-skill session-clear --all
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `search <query>` | 搜索网页 |
| `crawl <url>` | 爬取单页 |
| `crawl-site <url>` | 爬取全站 |
| `search-and-crawl <query>` | 搜索并爬取 |
| `login <platform>` | 登录平台 |
| `crawl-with-login <url>` | 登录态爬取 |
| `session-status` | 查看登录状态 |
| `session-clear [platform]` | 清除登录信息 |

## 输出格式

| 格式 | 说明 |
|------|------|
| `fit_markdown` | 优化后的 Markdown，去除冗余（推荐） |
| `markdown_with_citations` | 带引用列表，便于溯源 |
| `raw_markdown` | 原始 Markdown |

## 常见问题

### Twitter 爬取显示未登录？

确保使用的是 `x.com` 而不是 `twitter.com`，Cookie 域名绑定在 `.x.com`。

### 小红书扫码后无响应？

扫码后需要在 App 中点击确认登录。

### Playwright 浏览器问题？

```bash
python -m playwright install chromium --with-deps
```

## 致谢

这个项目的诞生，离不开以下优秀的开源项目：

### [crawl4ai](https://github.com/unclecode/crawl4ai) ⭐

**一个真正为 LLM 设计的爬虫引擎。**

当我第一次看到 crawl4ai 的 Fit Markdown 输出时，我被震撼了。它不是简单地把 HTML 转成 Markdown，而是智能地提取核心内容，去除导航、广告、侧边栏等噪音。这正是 AI 需要的输入格式 —— 干净、精炼、直击要点。

crawl4ai 的 `PruningContentFilter` 和 `DefaultMarkdownGenerator` 是本项目 Markdown 生成的核心。感谢 [@unclecode](https://github.com/unclecode) 创造了这个强大的工具。

### [Playwright](https://playwright.dev/)

微软出品的浏览器自动化工具。本项目使用 Playwright 的持久化上下文来维护登录状态，绕过反自动化检测。它的稳定性和跨平台支持是项目可靠运行的基础。

### [playwright-stealth](https://github.com/nickoala/playwright-stealth)

帮助 Playwright 绕过反自动化检测的关键组件。没有它，登录态爬取根本不可能实现。

### [duckduckgo-search](https://github.com/deedy5/duckduckgo_search)

免 API key 的搜索能力来自这个项目。简单、可靠、无需注册。

---

**如果这个项目对你有帮助，请给上面这些项目一个 Star ⭐**

它们才是真正的英雄。

## License

MIT License

## 作者

[@lancelin](https://github.com/lancelin111)

---

<p align="center">
  <em>Built with ❤️ and open source</em>
</p>
