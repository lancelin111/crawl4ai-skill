"""解析模块单元测试"""

import pytest

import sys
sys.path.insert(0, "/Users/lancelin/.openclaw/workspace-crawler/crawl4ai-skill")

from src.parser import ContentParser


class TestContentParser:
    """ContentParser 测试"""

    def test_format_markdown_with_header(self):
        """测试带头部的格式化"""
        parser = ContentParser()
        content = "# Hello\n\nThis is content."
        metadata = {
            "title": "Test Page",
            "url": "https://example.com",
            "timestamp": "2026-03-10T00:00:00Z",
            "format": "fit_markdown",
        }

        result = parser.format_markdown(content, metadata)

        assert "# Test Page" in result
        assert "https://example.com" in result
        assert "Hello" in result
        assert "This is content." in result

    def test_format_markdown_without_header(self):
        """测试不带头部的格式化"""
        parser = ContentParser()
        content = "# Hello\n\nThis is content."
        metadata = {"title": "Test"}

        result = parser.format_markdown(content, metadata, include_header=False)

        assert result == content

    def test_add_citations_with_links(self):
        """测试添加引用"""
        parser = ContentParser()
        content = "Some content."
        links = ["https://example.com/1", "https://example.com/2"]

        result = parser.add_citations(content, links)

        assert "## References" in result
        assert "[1]: https://example.com/1" in result
        assert "[2]: https://example.com/2" in result

    def test_add_citations_empty_links(self):
        """测试空链接列表"""
        parser = ContentParser()
        content = "Some content."

        result = parser.add_citations(content, [])

        assert result == content

    def test_add_citations_filter_empty_links(self):
        """测试过滤空链接"""
        parser = ContentParser()
        content = "Some content."
        links = ["https://example.com", "", "  ", "https://test.com"]

        result = parser.add_citations(content, links)

        assert "[1]: https://example.com" in result
        assert "[2]: https://test.com" in result

    def test_clean_markdown_removes_extra_newlines(self):
        """测试清理多余空行"""
        parser = ContentParser()
        content = "Line 1\n\n\n\n\n\nLine 2"

        result = parser.clean_markdown(content)

        # 应该最多保留 3 个连续换行
        assert "\n\n\n\n" not in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_clean_markdown_strips_trailing_whitespace(self):
        """测试去除行尾空白"""
        parser = ContentParser()
        content = "Line with spaces   \nLine 2   "

        result = parser.clean_markdown(content)

        assert "   \n" not in result

    def test_clean_markdown_empty_content(self):
        """测试清理空内容"""
        parser = ContentParser()

        assert parser.clean_markdown("") == ""
        assert parser.clean_markdown(None) == ""

    def test_extract_title_from_markdown(self):
        """测试从 Markdown 提取标题"""
        parser = ContentParser()
        content = "Some intro\n\n# Main Title\n\nContent..."

        title = parser.extract_title_from_markdown(content)

        assert title == "Main Title"

    def test_extract_title_no_title(self):
        """测试无标题情况"""
        parser = ContentParser()
        content = "Just some content without h1"

        title = parser.extract_title_from_markdown(content)

        assert title is None

    def test_extract_title_empty_content(self):
        """测试空内容"""
        parser = ContentParser()

        assert parser.extract_title_from_markdown("") is None
        assert parser.extract_title_from_markdown(None) is None

    def test_truncate_content_short(self):
        """测试短内容不截断"""
        parser = ContentParser()
        content = "Short content"

        result = parser.truncate_content(content, max_length=100)

        assert result == content

    def test_truncate_content_long(self):
        """测试长内容截断"""
        parser = ContentParser()
        content = "A" * 200

        result = parser.truncate_content(content, max_length=100)

        assert len(result) < 200
        assert "... (内容已截断)" in result

    def test_truncate_content_at_paragraph(self):
        """测试在段落边界截断"""
        parser = ContentParser()
        content = "First paragraph.\n\nSecond paragraph that is long enough."

        # 设置截断点在第二段中间
        result = parser.truncate_content(content, max_length=40)

        # 应该在段落边界截断
        assert "First paragraph." in result

    def test_merge_results(self):
        """测试合并多个结果"""
        parser = ContentParser()
        results = [
            {"title": "Page 1", "url": "https://example.com/1", "markdown": "Content 1"},
            {"title": "Page 2", "url": "https://example.com/2", "markdown": "Content 2"},
        ]

        merged = parser.merge_results(results)

        assert "## Page 1" in merged
        assert "## Page 2" in merged
        assert "Content 1" in merged
        assert "Content 2" in merged
        assert "---" in merged  # 分隔符

    def test_merge_results_empty(self):
        """测试合并空结果"""
        parser = ContentParser()

        assert parser.merge_results([]) == ""
