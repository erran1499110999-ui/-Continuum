"""修复规则框架与 R0 确定性规则（企划书 5.4 / 提示词 5）。

原则（AGENTS.md 规则 4、9）：
- 每条规则有唯一 rule_id；
- 只做有证据、可解释的修改，绝不编造内容；
- 规则只产出文本差异（diff），由引擎写入新目录，绝不修改原始文件。
"""

from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..models import FileKind, RepairLevel

_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")
_MAX_ITERATIONS = 100


@dataclass
class RepairFix:
    """一次修复动作（规则 ID、等级、原因、证据、差异）。"""

    rule_id: str
    level: RepairLevel
    file: str
    reason: str
    evidence: str
    diff: str


def _unified_diff(before: str, after: str, fromfile: str, tofile: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def _is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def fix_trailing_commas(text: str) -> Optional[str]:
    """R0：迭代移除 JSON 末尾多余逗号，直到可解析或规则无法继续。

    仅当结果能通过 json.loads 校验时才返回修复文本，否则返回 None。
    """
    current = text
    for _ in range(_MAX_ITERATIONS):
        if _is_valid_json(current):
            return current
        new = _TRAILING_COMMA_RE.sub(r"\1", current)
        if new == current:
            return None
        current = new
    return None


def plan_file(rel: str, kind: FileKind, text: str) -> Tuple[List[RepairFix], str]:
    """为单个文本文件规划修复步骤（顺序应用），返回 (修复列表, 最终文本)。"""
    fixes: List[RepairFix] = []
    current = text

    if kind in (FileKind.TEXT, FileKind.JSON, FileKind.CHARACTER_CARD_JSON):
        # R0-002：去除 UTF-8 BOM
        if current.startswith("\ufeff"):
            fixed = current[1:]
            fixes.append(
                RepairFix(
                    rule_id="R0-002",
                    level=RepairLevel.R0,
                    file=rel,
                    reason="去除 UTF-8 BOM（确定性修复）",
                    evidence="文件以 BOM 字符开头，部分解析器会因此拒绝该文件",
                    diff=_unified_diff(current, fixed, rel, rel + ".fixed"),
                )
            )
            current = fixed

    # R0-001：JSON 末尾多余逗号（仅对疑似 JSON 的文本）
    if kind is FileKind.TEXT and current.lstrip().startswith(("{", "[")):
        if not _is_valid_json(current):
            evidence = "JSON 解析失败"
            try:
                json.loads(current)
            except json.JSONDecodeError as exc:
                evidence = f"JSON 解析失败: {exc}"
            fixed = fix_trailing_commas(current)
            if fixed is not None and _is_valid_json(fixed):
                fixes.append(
                    RepairFix(
                        rule_id="R0-001",
                        level=RepairLevel.R0,
                        file=rel,
                        reason="移除 JSON 末尾多余逗号（确定性修复）",
                        evidence=evidence,
                        diff=_unified_diff(current, fixed, rel, rel + ".fixed"),
                    )
                )
                current = fixed
    return fixes, current
