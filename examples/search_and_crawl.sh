#!/bin/bash
# 搜索并爬取示例

# 搜索并爬取
echo "=== 搜索 'python web scraping' ==="
crawl4ai-skill search "python web scraping" --num-results 5

echo ""
echo "=== 搜索并爬取前 3 个结果 ==="
crawl4ai-skill search-and-crawl "python web scraping tutorials" \
    --num-results 5 \
    --crawl-top 3 \
    --output-dir ./search_results

echo ""
echo "=== 查看结果 ==="
ls -la ./search_results/

echo ""
echo "完成!"
