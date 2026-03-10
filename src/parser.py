"""解析模块 - 内容格式化和后处理

提供 Markdown 格式化、引用添加等功能。
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import re


class ContentParser:
    """内容解析器

    用于格式化和后处理爬取的内容。

    Example:
        >>> parser = ContentParser()
        >>> formatted = parser.format_markdown(content, metadata)
        >>> print(formatted)
    """

    def format_markdown(
        self,
        content: str,
        metadata: Dict[str, Any],
        include_header: bool = True,
    ) -> str:
        """格式化 Markdown 输出

        Args:
            content: 原始 markdown 内容
            metadata: 元数据（URL、标题、时间等）
            include_header: 是否包含页头

        Returns:
            格式化后的 markdown
        """
        if not include_header:
            return content

        title = metadata.get("title", "Untitled")
        url = metadata.get("url", "")
        timestamp = metadata.get("timestamp", datetime.now(timezone.utc).isoformat())
        format_type = metadata.get("format", "markdown")

        header = f"""# {title}

## Metadata
- **URL**: {url}
- **Crawled at**: {timestamp}
- **Format**: {format_type}

---

"""
        return header + content

    def add_citations(self, content: str, links: List[str]) -> str:
        """添加引用列表

        Args:
            content: markdown 内容
            links: 链接列表

        Returns:
            带引用的 markdown
        """
        if not links:
            return content

        # 过滤空链接
        valid_links = [link for link in links if link and link.strip()]

        if not valid_links:
            return content

        citations = "\n\n---\n\n## References\n\n"
        for i, link in enumerate(valid_links, 1):
            citations += f"[{i}]: {link}\n"

        return content + citations

    def clean_markdown(self, content: str) -> str:
        """清理 Markdown 内容

        移除多余空行、修复格式问题等。

        Args:
            content: 原始 markdown

        Returns:
            清理后的 markdown
        """
        if not content:
            return ""

        # 移除多余空行（保留最多两个连续空行）
        content = re.sub(r'\n{4,}', '\n\n\n', content)

        # 移除行尾空白
        content = '\n'.join(line.rstrip() for line in content.split('\n'))

        # 确保文件以单个换行结尾
        content = content.strip() + '\n'

        return content

    def extract_title_from_markdown(self, content: str) -> Optional[str]:
        """从 Markdown 中提取标题

        Args:
            content: markdown 内容

        Returns:
            提取的标题或 None
        """
        if not content:
            return None

        # 查找第一个 h1 标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return None

    def truncate_content(
        self,
        content: str,
        max_length: int = 10000,
        suffix: str = "\n\n... (内容已截断)"
    ) -> str:
        """截断内容

        Args:
            content: 原始内容
            max_length: 最大长度
            suffix: 截断后缀

        Returns:
            截断后的内容
        """
        if not content or len(content) <= max_length:
            return content

        # 在适当位置截断（尝试在段落边界）
        truncated = content[:max_length]

        # 尝试在最后一个段落结束处截断
        last_para = truncated.rfind('\n\n')
        if last_para > max_length * 0.8:
            truncated = truncated[:last_para]

        return truncated + suffix

    def merge_results(
        self,
        results: List[Dict[str, Any]],
        separator: str = "\n\n---\n\n"
    ) -> str:
        """合并多个爬取结果

        Args:
            results: 爬取结果列表
            separator: 分隔符

        Returns:
            合并后的 markdown
        """
        if not results:
            return ""

        parts = []
        for result in results:
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            content = result.get("markdown", "")

            part = f"## {title}\n\n**Source**: {url}\n\n{content}"
            parts.append(part)

        return separator.join(parts)
