"""API 处理器（W1：health / version）。

约定：处理器为无状态纯函数，返回可 JSON 化的 dict；
HTTP 事务（token、Host、状态码、JSON 编码）由 server.py 统一处理。
后续阶段在此增量添加 job 端点（scan/backup/verify/restore/repair/migrate）。
"""
from __future__ import annotations

from typing import Dict

from .. import __version__

TOOL_NAME = "continuity-studio"


def health() -> Dict[str, str]:
    """服务健康检查（不含任何路径/数据信息）。"""
    return {"status": "ok"}


def version() -> Dict[str, str]:
    """工具版本信息。"""
    return {"tool": TOOL_NAME, "version": __version__}
