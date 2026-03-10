"""工具函数"""

import re
from urllib.parse import urlparse, urljoin
from typing import List, Optional


def is_valid_url(url: str) -> bool:
    """检查 URL 是否有效

    Args:
        url: 待检查的 URL

    Returns:
        是否有效
    """
    if not url:
        return False

    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def normalize_url(url: str, base_url: Optional[str] = None) -> Optional[str]:
    """标准化 URL

    Args:
        url: 待标准化的 URL
        base_url: 基础 URL（用于相对路径）

    Returns:
        标准化后的 URL 或 None
    """
    if not url:
        return None

    url = url.strip()

    # 跳过特殊链接
    if url.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
        return None

    # 处理相对路径
    if base_url and not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)

    # 移除 fragment
    parsed = urlparse(url)
    url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        url += f"?{parsed.query}"

    return url if is_valid_url(url) else None


def get_domain(url: str) -> Optional[str]:
    """获取 URL 的域名

    Args:
        url: URL

    Returns:
        域名或 None
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def is_same_domain(url1: str, url2: str) -> bool:
    """检查两个 URL 是否属于同一域名

    Args:
        url1: 第一个 URL
        url2: 第二个 URL

    Returns:
        是否同域
    """
    domain1 = get_domain(url1)
    domain2 = get_domain(url2)
    return domain1 is not None and domain1 == domain2


def extract_urls_from_text(text: str) -> List[str]:
    """从文本中提取 URL

    Args:
        text: 文本内容

    Returns:
        URL 列表
    """
    if not text:
        return []

    # 匹配 URL 的正则表达式
    url_pattern = r'https?://[^\s<>"\')\]}>]+'
    urls = re.findall(url_pattern, text)

    # 过滤和清理
    valid_urls = []
    for url in urls:
        # 移除末尾的标点符号
        url = url.rstrip('.,;:!?')
        if is_valid_url(url):
            valid_urls.append(url)

    return list(set(valid_urls))  # 去重


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断字符串

    Args:
        s: 原字符串
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的字符串
    """
    if not s or len(s) <= max_length:
        return s

    return s[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符

    Args:
        filename: 原文件名

    Returns:
        清理后的文件名
    """
    if not filename:
        return "untitled"

    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    # 移除首尾空白
    filename = filename.strip()
    # 限制长度
    filename = filename[:200] if len(filename) > 200 else filename

    return filename or "untitled"
