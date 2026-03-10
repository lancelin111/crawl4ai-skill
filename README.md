# Crawl4AI Skill

智能搜索与爬取工具，为 OpenClaw 提供 DuckDuckGo 搜索和智能网页爬取能力。

## Features

- 🔍 **DuckDuckGo 搜索** - 免 API key，快速搜索网页
- 🕷️ **智能全站爬取** - 自动识别 sitemap、llms-full.txt 和递归策略
- 📝 **LLM 优化输出** - Fit Markdown 格式，去除冗余内容
- 🔗 **引用和溯源** - 支持 markdown_with_citations 格式
- ⚙️ **可配置选项** - 深度控制、链接过滤、超时设置

## Installation

### 从 ClawHub 安装（推荐）

```bash
clawhub install crawl4ai-skill
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-username/crawl4ai-skill.git
cd crawl4ai-skill

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
python -m playwright install chromium
```

## Quick Start

### 搜索

```bash
# 基础搜索
crawl4ai-skill search "python web scraping"

# 指定结果数量
crawl4ai-skill search "AI tutorials" --num-results 5

# 输出到文件
crawl4ai-skill search "machine learning" -o results.json
```

### 爬取单页

```bash
# 基础爬取
crawl4ai-skill crawl https://example.com

# 指定格式并保存
crawl4ai-skill crawl https://docs.python.org -f fit_markdown -o python_docs.md

# 等待动态加载
crawl4ai-skill crawl https://example.com --wait-for ".article-content"
```

### 爬取全站

```bash
# 自动识别策略
crawl4ai-skill crawl-site https://docs.example.com

# 爬取 sitemap
crawl4ai-skill crawl-site https://example.com/sitemap.xml --strategy sitemap

# 深度爬取
crawl4ai-skill crawl-site https://example.com --max-depth 3 --max-pages 100
```

### 搜索并爬取

```bash
# 搜索并爬取前 3 个结果
crawl4ai-skill search-and-crawl "python web scraping tutorials"

# 自定义搜索和爬取数量
crawl4ai-skill search-and-crawl "AI tutorials" --num-results 10 --crawl-top 5
```

## Usage

### CLI 命令

| 命令 | 说明 |
|------|------|
| `search <query>` | 搜索网页 |
| `crawl <url>` | 爬取单个网页 |
| `crawl-site <url>` | 爬取整个站点 |
| `search-and-crawl <query>` | 搜索并爬取 |

### 常用选项

| 选项 | 说明 |
|------|------|
| `-n, --num-results` | 搜索结果数量 |
| `-f, --format` | 输出格式（fit_markdown/markdown_with_citations/raw_markdown） |
| `-o, --output` | 输出文件路径 |
| `-d, --max-depth` | 最大爬取深度 |
| `-p, --max-pages` | 最大页面数量 |

### Python API

```python
import asyncio
from src.search import DuckDuckGoSearcher
from src.crawler import SmartCrawler

# 搜索
searcher = DuckDuckGoSearcher()
results = searcher.search("python web scraping", num_results=5)
for r in results:
    print(f"{r.title}: {r.url}")

# 爬取
crawler = SmartCrawler()
result = asyncio.run(crawler.crawl_page("https://example.com"))
print(result.markdown)
```

## Output Formats

### fit_markdown（默认）

优化后的 Markdown，去除导航、广告等冗余内容，节省 token。

### markdown_with_citations

带引用列表的 Markdown，链接转换为编号引用，便于溯源。

### raw_markdown

原始 Markdown 输出，保留完整内容。

## 爬取策略

### auto（自动识别）

- URL 以 `sitemap.xml` 结尾 → sitemap 策略
- URL 以 `llms-full.txt` / `llms.txt` 结尾 → txt 列表策略
- 其他 → recursive 递归策略

### sitemap

解析 sitemap.xml，按顺序爬取所有 URL。

### recursive

从起始 URL 开始，递归爬取内部链接（BFS）。

## Examples

查看 `examples/` 目录获取更多示例：

- `simple_crawl.sh` - 简单爬取示例
- `deep_crawl.sh` - 深度爬取示例
- `search_and_crawl.sh` - 搜索+爬取示例

## Troubleshooting

### 爬取失败

1. 检查网络连接
2. 尝试增加超时时间：`--timeout 60`
3. 对于动态页面，使用 `--wait-for` 等待元素加载

### 搜索被限流

DuckDuckGo 可能会限流频繁请求，建议：
- 减少请求频率
- 使用更精确的查询词

### Playwright 浏览器问题

```bash
# 重新安装浏览器
python -m playwright install chromium --with-deps
```

## Contributing

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## License

MIT License - 详见 [LICENSE](LICENSE)

## Acknowledgments

- [crawl4ai](https://github.com/unclecode/crawl4ai) - 强大的 LLM 友好爬虫引擎
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search) - DuckDuckGo 搜索库
- [OpenClaw](https://openclaw.ai) - AI 助手平台
