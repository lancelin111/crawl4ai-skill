---
name: crawl4ai-skill
description: 智能搜索与爬取工具，输出 LLM 优化 Markdown，Token 降低 80%。支持 DuckDuckGo 搜索、全站爬取、登录态爬取。
version: 0.2.0
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
    - playwright
credentials:
  - name: TWITTER_COOKIES
    description: Twitter auth_token and ct0 for authenticated crawling
    optional: true
    example: "auth_token=xxx; ct0=yyy"
  - name: Session files
    description: Encrypted session storage at ~/.crawl4ai-skill/sessions/
    optional: true
---

# Crawl4AI Skill

**智能搜索与爬取 | LLM 优化输出 | 省 Token 80%**

## 核心功能

- 🔍 **DuckDuckGo 搜索** - 免 API key，零配置
- 🕷️ **智能全站爬取** - 自动识别 sitemap/递归爬取
- 📝 **LLM 优化输出** - Fit Markdown 格式，节省 80% Token
- 🔐 **登录态爬取** - Twitter/X、小红书（可选）

---

## 快速开始

### 安装

```bash
pip install crawl4ai-skill
python -m playwright install chromium
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
crawl4ai-skill crawl-site https://docs.fastapi.com --max-pages 100 --output fastapi-docs.md
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

## 高级功能：登录态爬取

**支持平台：** Twitter/X、小红书

### Twitter 登录（可选）

```bash
# 设置环境变量
export TWITTER_COOKIES="auth_token=xxx; ct0=yyy"
crawl4ai-skill login twitter

# 爬取
crawl4ai-skill crawl-with-login https://x.com/username -p twitter
```

**获取 Cookie：**
1. 浏览器登录 Twitter
2. F12 → Application → Cookies
3. 复制 `auth_token` 和 `ct0`

### 小红书登录（可选）

```bash
crawl4ai-skill login xiaohongshu
# 会显示二维码，用 App 扫码
```

### 管理登录状态

```bash
# 查看状态
crawl4ai-skill session-status

# 清除登录
crawl4ai-skill session-clear twitter
```

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `search <query>` | 搜索网页 |
| `crawl <url>` | 爬取单页 |
| `crawl-site <url>` | 爬取全站 |
| `search-and-crawl <query>` | 搜索并爬取 |
| `login <platform>` | 登录平台（可选） |
| `crawl-with-login <url>` | 登录态爬取 |
| `session-status` | 查看登录状态 |
| `session-clear` | 清除登录 |

### 常用参数

```bash
# 搜索
--num-results 10          # 返回数量
--region us-en           # 搜索区域

# 爬取
--format fit_markdown    # 输出格式
--output result.md       # 输出文件

# 全站爬取
--max-pages 100          # 最多爬取页面数
--max-depth 3            # 最大递归深度
```

---

## 安全说明

**数据安全：**
- ✅ 所有数据本地存储（`~/.crawl4ai-skill/`）
- ✅ Session 文件 AES-128 加密
- ✅ 不上传任何数据

**凭证管理：**
- ✅ 推荐环境变量或交互式输入
- ⚠️ 不推荐命令行直接传递

**使用建议：**
- 🔍 使用前审查代码：[GitHub](https://github.com/lancelin111/crawl4ai-skill)
- 🔐 用完清理：`crawl4ai-skill session-clear --all`
- 📦 定期更新：`pip install --upgrade crawl4ai-skill`

**查看详细安全政策：** [SECURITY.md](https://github.com/lancelin111/crawl4ai-skill/blob/main/SECURITY.md)

**责任声明：** 仅供学习研究，使用者自负法律责任。

---

## 常见问题

**如何获取 Twitter Cookie？**
1. 浏览器登录 Twitter
2. F12 → Application → Cookies
3. 找到 `auth_token` 和 `ct0`

**Playwright 安装失败？**
```bash
python -m playwright install chromium --with-deps
```

**爬取被拦截？**
确保使用登录态：
```bash
crawl4ai-skill crawl-with-login URL -p twitter
```

---

## 链接

- 📦 [PyPI](https://pypi.org/project/crawl4ai-skill/)
- 💻 [GitHub](https://github.com/lancelin111/crawl4ai-skill)
- 🔒 [Security Policy](https://github.com/lancelin111/crawl4ai-skill/blob/main/SECURITY.md)
