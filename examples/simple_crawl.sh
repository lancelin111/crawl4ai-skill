#!/bin/bash
# 简单爬取示例

# 爬取单个页面
echo "=== 爬取 example.com ==="
crawl4ai-skill crawl https://example.com

echo ""
echo "=== 爬取并保存到文件 ==="
crawl4ai-skill crawl https://example.com -o example.md

echo ""
echo "=== 使用 markdown_with_citations 格式 ==="
crawl4ai-skill crawl https://example.com -f markdown_with_citations

echo ""
echo "完成!"
