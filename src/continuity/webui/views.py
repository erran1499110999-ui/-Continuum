"""报告/响应 → JSON 序列化适配（W1 骨架）。

W2 起填充引擎报告（ScanReport/VerifyReport/RestoreReport/RepairReport/
MigrationReport）到 JSON 的适配函数；W1 只提供统一的基础工具，
被 server.py 用于所有 JSON 响应。
"""
from __future__ import annotations

import json
from typing import Any


def json_bytes(obj: Any) -> bytes:
    """对象 → UTF-8 JSON 字节（ensure_ascii=False，保留中文可读性）。"""
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")
