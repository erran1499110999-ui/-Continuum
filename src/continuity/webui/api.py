"""API 处理器（W1：health / version；W2：scan job）。

约定：处理器为无状态纯函数，返回可 JSON 化的 dict；
HTTP 事务（token、Host、状态码、JSON 编码）由 server.py 统一处理。
后续阶段在此增量添加 job 端点（backup/verify/restore/repair/migrate）。
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Optional

from .. import __version__
from ..scanners.scan import scan_directory
from .views import scan_report_to_json

TOOL_NAME = "continuity-studio"


def health() -> Dict[str, str]:
    """服务健康检查（不含任何路径/数据信息）。"""
    return {"status": "ok"}


def version() -> Dict[str, str]:
    """工具版本信息。"""
    return {"tool": TOOL_NAME, "version": __version__}


def scan_worker(source: str, *, log: Optional[Callable[[str], None]] = None) -> Dict[str, object]:
    """在 job 工作线程内执行只读扫描，返回序列化报告（源目录绝不写入）。

    资源上限等引擎错误（ScanError/OSError）会在此抛出，由 JobManager
    捕获为 failed 状态并把面向用户的错误信息透传给前端。
    """
    report = scan_directory(Path(source))
    data = scan_report_to_json(report)
    if log is not None:
        log(f"扫描完成: {len(report.files)} 个文件，{len(report.findings)} 项发现")
    return data
