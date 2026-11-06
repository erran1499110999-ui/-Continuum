"""流式 SHA-256 计算，避免整文件载入内存。"""

from __future__ import annotations

import hashlib
from pathlib import Path

CHUNK_SIZE = 1024 * 1024  # 1 MiB


def sha256_file(path: Path) -> str:
    """返回文件的小写十六进制 SHA-256。"""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
