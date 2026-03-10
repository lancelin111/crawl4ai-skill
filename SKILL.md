---
name: crawl4ai-skill
description: |
  智能搜索与爬取工具，输出 LLM 优化 Markdown，Token 消耗降低 80%。零配置 DuckDuckGo 搜索→爬取→Fit Markdown 一条龙。额外支持 Twitter/X、小红书登录态爬取（Playwright Stealth + 加密 Session）。pip install crawl4ai-skill 开箱即用。
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

**智能搜索与爬取 | LLM 优化输出 | 省 Token 80%**

## 核心功能

- 🔍 **DuckDuckGo 搜索** - 免 API key，零配置
- 🕷️ **智能全站爬取** - 自动识别 sitemap/llms-full.txt/递归爬取
- 📝 **LLM 优化输出** - Fit Markdown 格式，去冗余，节省 80% Token
- 🔐 **登录态爬取** - Twitter/X、小红书（Playwright Stealth 反检测）
- 🐦 **推文提取** - 支持引用推文 (Quote Tweet)

---

## 快速开始

### 安装

```bash
# 推荐：从 PyPI 安装（已验证）
pip install crawl4ai-skill
python -m playwright install chromium

# 或从源码审查后安装
git clone https://github.com/lancelin111/crawl4ai-skill.git
cd crawl4ai-skill && pip install -e . && python -m playwright install chromium
```

### 基础使用

```bash
# 1. 搜索网页
crawl4ai-skill search "python async programming"

# 2. 爬取单页
crawl4ai-skill crawl https://docs.python.org/3/library/asyncio.html

# 3. 爬取全站（自动识别 sitemap）
crawl4ai-skill crawl-site https://docs.python.org --max-pages 50

# 4. 搜索并爬取（一条龙）
crawl4ai-skill search-and-crawl "FastAPI tutorial" --crawl-top 3
```

---

## 使用场景

### 场景 1：为 LLM 准备干净的文档

**需求：** 让 AI 学习一个库的文档，但原始 HTML 太冗余。

```bash
# 爬取整个文档站，输出 LLM 优化 Markdown
crawl4ai-skill crawl-site https://docs.fastapi.com --max-pages 100 --output fastapi-docs.md

# 输出示例（Fit Markdown）：
# - 去除导航栏、侧边栏、广告
# - 保留核心内容、代码块、结构
# - Token 消耗从 50,000 降到 10,000 ✅
```

**参数说明：**
- `--max-pages N` - 最多爬取 N 个页面（默认 100）
- `--output FILE` - 输出到文件（默认打印到终端）
- `--format FORMAT` - 输出格式：`fit_markdown` (默认), `raw_markdown`, `markdown_with_citations`

---

### 场景 2：搜索+爬取热门结果

**需求：** 搜索一个主题，自动爬取前 3 个结果并整合。

```bash
crawl4ai-skill search-and-crawl "Vue 3 composition API best practices" --crawl-top 3 --output vue3-guide.md
```

**工作流程：**
1. DuckDuckGo 搜索 "Vue 3 composition API best practices"
2. 自动爬取排名前 3 的页面
3. 每个页面输出 Fit Markdown
4. 整合到一个文件

---

### 场景 3：监控竞品博客更新

**需求：** 定期抓取竞品博客，提取新文章。

```bash
# 爬取博客首页的文章列表
crawl4ai-skill crawl https://competitor.com/blog --format fit_markdown

# 配合 cron 实现自动监控
# crontab: 0 9 * * * crawl4ai-skill crawl https://competitor.com/blog > /path/to/blog-$(date +\%Y\%m\%d).md
```

---

### 场景 4：爬取需要登录的内容

**需求：** 爬取 Twitter 用户的推文（包括引用推文）。

```bash
# 步骤 1: 登录 Twitter（首次）
export TWITTER_COOKIES="auth_token=abc123; ct0=xyz789"
crawl4ai-skill login twitter

# 步骤 2: 爬取用户页面
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --extract-tweets -o elon-tweets.md
```

**输出示例：**
```markdown
# @elonmusk 的推文

## Tweet 1
Content: Just launched Starship...
Posted: 2026-03-10
Likes: 125k | Retweets: 32k

## Quote Tweet (引用)
> Original by @NASA: ...
Quoted by @elonmusk: This is exciting!
```

---

## 登录态爬取（高级功能）

### 支持的平台

| 平台 | 登录方式 | 说明 |
|------|----------|------|
| **Twitter/X** | Cookie 注入 | 需要 `auth_token` + `ct0` |
| **小红书** | 扫码登录 | App 扫码确认 |

### Twitter/X 登录

**方式 1：环境变量（推荐）**
```bash
export TWITTER_COOKIES="auth_token=xxx; ct0=yyy"
crawl4ai-skill login twitter
```

**方式 2：交互式输入**
```bash
crawl4ai-skill login twitter --interactive
# 提示：Enter cookies (隐藏输入): 
```

**方式 3：从文件读取**
```bash
echo "auth_token=xxx; ct0=yyy" > ~/.twitter-cookies
chmod 600 ~/.twitter-cookies
crawl4ai-skill login twitter --cookies-file ~/.twitter-cookies
```

**获取 Twitter Cookie：**
1. 浏览器登录 Twitter
2. F12 → Application → Cookies → https://x.com
3. 复制 `auth_token` 和 `ct0` 的值

### 小红书登录

```bash
crawl4ai-skill login xiaohongshu
# 会打开浏览器显示二维码
# 用小红书 App 扫码并确认
```

### 登录态爬取示例

```bash
# 爬取 Twitter 用户页面
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter

# 提取推文（包含引用推文）
crawl4ai-skill crawl-with-login https://x.com/elonmusk -p twitter --extract-tweets

# 爬取小红书笔记
crawl4ai-skill crawl-with-login https://www.xiaohongshu.com/explore/123456 -p xiaohongshu
```

### 管理登录状态

```bash
# 查看状态（显示加密信息）
crawl4ai-skill session-status
# 输出：
# Platform: twitter
# Status: ✅ Logged in
# Encrypted: ✅ AES-128-CBC
# Last used: 2026-03-10 10:30:00

# 清除指定平台
crawl4ai-skill session-clear twitter

# 清除所有平台
crawl4ai-skill session-clear --all
```

---

## 输出格式

### fit_markdown（推荐）

去除冗余，保留核心内容，节省 80% Token。

```bash
crawl4ai-skill crawl https://example.com --format fit_markdown
```

**优化效果：**
- ❌ 移除：导航栏、侧边栏、广告、页脚
- ✅ 保留：标题、正文、代码块、表格、链接
- 📊 **Token 节省：50,000 → 10,000（-80%）**

### raw_markdown

保留完整 HTML 结构转换的 Markdown。

```bash
crawl4ai-skill crawl https://example.com --format raw_markdown
```

### markdown_with_citations

带引用列表，便于溯源。

```bash
crawl4ai-skill crawl https://example.com --format markdown_with_citations
```

**输出示例：**
```markdown
# 标题

内容...[1]

## References
[1] https://example.com/source1
```

---

## 高级参数

### 搜索相关

```bash
crawl4ai-skill search "query" \
  --num-results 10          # 返回结果数量（默认 5）
  --region us-en           # 搜索区域（默认 wt-wt）
```

### 爬取相关

```bash
crawl4ai-skill crawl https://example.com \
  --format fit_markdown    # 输出格式（默认）
  --output result.md       # 输出文件
  --wait-for ".content"    # 等待选择器出现
```

### 全站爬取

```bash
crawl4ai-skill crawl-site https://docs.example.com \
  --max-pages 100          # 最多爬取页面数
  --max-depth 3            # 最大递归深度
  --same-domain            # 只爬取同域名（默认开启）
  --output-dir ./output    # 输出目录
```

---

## 命令速查表

| 命令 | 说明 | 示例 |
|------|------|------|
| `search` | 搜索网页 | `crawl4ai-skill search "AI agents"` |
| `crawl` | 爬取单页 | `crawl4ai-skill crawl https://example.com` |
| `crawl-site` | 爬取全站 | `crawl4ai-skill crawl-site https://docs.example.com` |
| `search-and-crawl` | 搜索并爬取 | `crawl4ai-skill search-and-crawl "topic" --crawl-top 3` |
| `login` | 登录平台 | `crawl4ai-skill login twitter` |
| `crawl-with-login` | 登录态爬取 | `crawl4ai-skill crawl-with-login URL -p twitter` |
| `session-status` | 查看登录状态 | `crawl4ai-skill session-status` |
| `session-clear` | 清除登录 | `crawl4ai-skill session-clear twitter` |

---

## 🔒 安全说明（简要）

**数据安全：**
- ✅ 所有数据**本地存储**（`~/.crawl4ai-skill/`）
- ✅ Session Cookies **AES-128 加密**，密钥基于机器标识符
- ✅ **绝不上传**任何数据到第三方服务器

**凭证管理：**
- ✅ 推荐用**环境变量**或**交互式输入**（不记录在 shell history）
- ⚠️ 不推荐命令行直接传递（会记录在历史）

**代码审查：**
- ✅ **完全开源**，可在 [GitHub](https://github.com/lancelin111/crawl4ai-skill) 审查
- ✅ 通过 [Bandit 安全扫描](https://github.com/lancelin111/crawl4ai-skill/actions)
- ✅ 查看详细安全政策：[SECURITY.md](https://github.com/lancelin111/crawl4ai-skill/blob/main/SECURITY.md)

**使用建议：**
- 🔍 使用前审查代码
- 🔐 用完及时清理：`crawl4ai-skill session-clear --all`
- 💻 不要在公共电脑使用
- 📦 定期更新：`pip install --upgrade crawl4ai-skill`

**责任声明：** 仅供学习研究，使用者自负法律责任。

---

## 常见问题

### 如何获取 Twitter Cookie？

1. 浏览器登录 Twitter
2. F12 → Application → Cookies
3. 找到 `auth_token` 和 `ct0`

### Playwright 安装失败？

```bash
python -m playwright install chromium --with-deps
```

### 爬取被拦截？

确保使用登录态：
```bash
crawl4ai-skill crawl-with-login URL -p twitter
```

### 输出太长？

使用 `--format fit_markdown` 去冗余。

---

## 链接

- 📦 [PyPI](https://pypi.org/project/crawl4ai-skill/)
- 💻 [GitHub](https://github.com/lancelin111/crawl4ai-skill)
- 🔒 [Security Policy](https://github.com/lancelin111/crawl4ai-skill/blob/main/SECURITY.md)
- 🐛 [Issues](https://github.com/lancelin111/crawl4ai-skill/issues)
