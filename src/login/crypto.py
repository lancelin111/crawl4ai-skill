"""加密模块 - Cookie/Session 加密存储

使用 Fernet 对称加密（AES-128-CBC）保护敏感数据。
密钥基于机器标识符派生，确保数据只能在同一台机器上解密。
"""

import base64
import hashlib
import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

# 尝试导入 cryptography，如果没有则使用简单的 base64 混淆
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _get_machine_id() -> str:
    """获取机器唯一标识符

    组合多个系统信息生成稳定的机器 ID。

    Returns:
        机器标识符字符串
    """
    parts = []

    # 平台信息
    parts.append(platform.node())
    parts.append(platform.system())
    parts.append(platform.machine())

    # 尝试获取 MAC 地址
    try:
        mac = uuid.getnode()
        parts.append(str(mac))
    except Exception:
        pass

    # 用户目录路径（作为额外的唯一性因素）
    parts.append(str(Path.home()))

    return "|".join(parts)


def _derive_key(salt: bytes) -> bytes:
    """从机器 ID 派生加密密钥

    Args:
        salt: 盐值

    Returns:
        32 字节的密钥（用于 Fernet）
    """
    machine_id = _get_machine_id().encode()

    if HAS_CRYPTO:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(machine_id))
    else:
        # 降级方案：使用 hashlib
        combined = salt + machine_id
        return base64.urlsafe_b64encode(
            hashlib.pbkdf2_hmac('sha256', machine_id, salt, 100000)
        )


class SessionEncryption:
    """Session 加密类

    提供 Session 数据的加密和解密功能。
    """

    SALT_FILE = ".salt"

    def __init__(self, session_dir: Path):
        """初始化加密类

        Args:
            session_dir: Session 存储目录
        """
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._salt_file = session_dir / self.SALT_FILE
        self._salt = self._get_or_create_salt()
        self._key = _derive_key(self._salt)

        if HAS_CRYPTO:
            self._fernet = Fernet(self._key)
        else:
            self._fernet = None

    def _get_or_create_salt(self) -> bytes:
        """获取或创建盐值

        Returns:
            16 字节的盐值
        """
        if self._salt_file.exists():
            try:
                with open(self._salt_file, "rb") as f:
                    salt = f.read()
                if len(salt) >= 16:
                    return salt[:16]
            except Exception:
                pass

        # 生成新的盐值
        salt = os.urandom(16)
        try:
            with open(self._salt_file, "wb") as f:
                f.write(salt)
            # 设置文件权限为 600
            os.chmod(self._salt_file, 0o600)
        except Exception:
            pass

        return salt

    def encrypt(self, data: Dict[str, Any]) -> str:
        """加密数据

        Args:
            data: 要加密的字典数据

        Returns:
            加密后的 base64 字符串
        """
        json_str = json.dumps(data, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')

        if self._fernet:
            encrypted = self._fernet.encrypt(json_bytes)
            return encrypted.decode('utf-8')
        else:
            # 降级方案：简单的 base64 + XOR 混淆
            xor_key = self._key[:len(json_bytes) % 32 + 1]
            xored = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(json_bytes))
            return base64.b64encode(xored).decode('utf-8')

    def decrypt(self, encrypted_str: str) -> Optional[Dict[str, Any]]:
        """解密数据

        Args:
            encrypted_str: 加密的字符串

        Returns:
            解密后的字典数据，失败返回 None
        """
        try:
            if self._fernet:
                decrypted = self._fernet.decrypt(encrypted_str.encode('utf-8'))
                return json.loads(decrypted.decode('utf-8'))
            else:
                # 降级方案
                xored = base64.b64decode(encrypted_str)
                xor_key = self._key[:len(xored) % 32 + 1]
                json_bytes = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(xored))
                return json.loads(json_bytes.decode('utf-8'))
        except Exception:
            return None

    @staticmethod
    def is_encrypted(content: str) -> bool:
        """检查内容是否已加密

        Args:
            content: 文件内容

        Returns:
            是否为加密格式
        """
        content = content.strip()
        # Fernet 格式以 gAAAAA 开头
        if content.startswith("gAAAAA"):
            return True
        # 检查是否为 JSON（未加密）
        try:
            json.loads(content)
            return False
        except json.JSONDecodeError:
            # 不是 JSON，可能是 base64 加密
            return True

    @classmethod
    def has_encryption_support(cls) -> bool:
        """检查是否支持强加密

        Returns:
            是否安装了 cryptography 库
        """
        return HAS_CRYPTO
