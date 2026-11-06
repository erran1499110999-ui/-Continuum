"""报告/响应 → JSON 序列化适配。

W1 提供统一基础工具（json_bytes）；W2 起逐引擎填充报告序列化函数：
枚举一律转 .value 字符串，None 保持 null；绝不把导入内容当作 HTML 输出。
"""
from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, List

from ..scanners.scan import ScanReport


def json_bytes(obj: Any) -> bytes:
    """对象 → UTF-8 JSON 字节（ensure_ascii=False，保留中文可读性）。"""
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def _enum_value(value: Any) -> Any:
    """枚举 → .value 字符串；非枚举原样返回（None → null）。

    引擎报告里的 FileKind/Severity/RepairLevel 都是 enum，json.dumps 无法直接
    序列化——统一在此转字符串，UI 侧拿到的是纯 JSON 可消费值。
    """
    return value.value if isinstance(value, Enum) else value


def scan_report_to_json(report: ScanReport) -> Dict[str, Any]:
    """ScanReport → 可 JSON 化的 dict（与 CLI 输出同源，UI 不做二次推断）。"""
    return {
        "root": report.root,
        "files": [
            {
                "rel_path": f.rel_path,
                "kind": _enum_value(f.kind),
                "size": f.size,
                "sha256": f.sha256,
                "warnings": list(f.warnings),
            }
            for f in report.files
        ],
        "findings": [
            {
                "file": f.file,
                "location": f.location,
                "problem": f.problem,
                "evidence": f.evidence,
                "suggestion": f.suggestion,
                "severity": _enum_value(f.severity),
                "repair_level": _enum_value(f.repair_level),
                "confidence": f.confidence,
            }
            for f in report.findings
        ],
        "duplicates": [list(group) for group in report.duplicates],
        "skipped_symlinks": list(report.skipped_symlinks),
    }
