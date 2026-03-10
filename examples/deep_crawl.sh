#!/bin/bash
# 深度爬取示例

# 全站爬取
echo "=== 深度爬取 example.com ==="
crawl4ai-skill crawl-site https://example.com \
    --max-depth 2 \
    --max-pages 10 \
    --output-dir ./example_crawl

echo ""
echo "=== 查看爬取结果 ==="
ls -la ./example_crawl/

echo ""
echo "=== 查看统计信息 ==="
cat ./example_crawl/stats.json

echo ""
echo "完成!"
