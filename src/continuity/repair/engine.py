"""修复引擎：只读诊断 + 生成修复副本（企划书 5.4 / 提示词 5）。

- 原始文件只读，修复结果写入全新的输出目录；
- R0 确定性修复自动生成修复副本；R1 可推断修复（须用户确认，规则待补）；
  R2 仅输出人工处理建议；R3 隔离不执行；
- 每个修复动作记录 rule_id、原因、证据、修复前后 SHA-256 与文本差异；
- 修复报告写入输出目录的 repair-report.json，差异写入 diffs/。
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional

from .. import __version__
from ..hashing import sha256_file
from ..models import FileKind, RepairLevel, utc_now_iso
from ..scanners.scan import scan_directory
from .rules import plan_file

REPORT_FILENAME = "repair-report.json"
DIFFS_DIR_NAME = "diffs"

# 只对不超过该大小的文本文件做自动修复（防止大文件导致内存问题）
_MAX_REPAIR_BYTES = 8 * 1024 * 1024


class RepairError(Exception):
    """修复过程中的错误，信息面向用户。"""


@dataclass
class RepairReport:
    created_at: str
    tool_version: str
    source_root: str
    output_root: str
    files_total: int = 0
    files_repaired: int = 0
    r0_applied: int = 0
    fixes: List[Dict[str, Any]] = field(default_factory=list)
    r2_advice: List[Dict[str, Any]] = field(default_factory=list)
    r3_isolated: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def apply_repairs(source_dir: Path, output_dir: Path) -> RepairReport:
    """只读扫描 source_dir，把修复后的完整副本写入新的 output_dir。

    output_dir 必须不存在，且不得位于 source_dir 之内；失败时清理输出目录。
    """
    source = source_dir.resolve()
    if not source.is_dir():
        raise RepairError(f"源目录不存在: {source_dir}")
    output = output_dir.resolve()
    if output.exists():
        raise RepairError(f"修复输出目录已存在，请选择新目录: {output_dir}")
    if output.is_relative_to(source):
        raise RepairError(f"修复输出目录不能位于源目录之内: {output_dir}")

    output.mkdir(parents=True)
    try:
        scan = scan_directory(source)
        report = RepairReport(
            created_at=utc_now_iso(),
            tool_version=__version__,
            source_root=str(source),
            output_root=str(output),
            files_total=len(scan.files),
        )
        diffs_dir = output / DIFFS_DIR_NAME

        for sf in sorted(scan.files, key=lambda f: f.rel_path):
            src = source / Path(*PurePosixPath(sf.rel_path).parts)
            dst = output / Path(*PurePosixPath(sf.rel_path).parts)
            dst.parent.mkdir(parents=True, exist_ok=True)

            fixes = []
            final_bytes: Optional[bytes] = None
            if (
                sf.kind in (FileKind.TEXT, FileKind.JSON, FileKind.CHARACTER_CARD_JSON)
                and sf.size <= _MAX_REPAIR_BYTES
            ):
                try:
                    text = src.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text = None
                if text is not None:
                    fixes, final_text = plan_file(sf.rel_path, sf.kind, text)
                    if fixes:
                        final_bytes = final_text.encode("utf-8")

            if final_bytes is not None:
                dst.write_bytes(final_bytes)
                after_sha = sha256_file(dst)
                report.files_repaired += 1
                report.r0_applied += len(fixes)
                for fix in fixes:
                    report.fixes.append(
                        {
                            "rule_id": fix.rule_id,
                            "level": fix.level.value,
                            "file": sf.rel_path,
                            "reason": fix.reason,
                            "evidence": fix.evidence,
                            "before_sha256": sf.sha256,
                            "after_sha256": after_sha,
                            "diff": fix.diff,
                        }
                    )
                    if fix.diff:
                        # 差异文件按 rel_path 展平命名（"/" → "__"），避免输出目录嵌套
                        diffs_dir.mkdir(exist_ok=True)
                        (diffs_dir / (sf.rel_path.replace("/", "__") + ".diff")).write_text(
                            fix.diff, encoding="utf-8"
                        )
            else:
                # 无修复动作的文件（非文本/超限/无规则命中）：原样字节复制，绝不改动
                shutil.copy2(src, dst)

        repaired_files = {f["file"] for f in report.fixes}
        for finding in scan.findings:
            if finding.repair_level is RepairLevel.R2 and finding.file not in repaired_files:
                report.r2_advice.append(
                    {
                        "file": finding.file,
                        "problem": finding.problem,
                        "evidence": finding.evidence,
                        "suggestion": finding.suggestion,
                    }
                )
            elif finding.repair_level is RepairLevel.R3:
                report.r3_isolated.append(
                    {
                        "file": finding.file,
                        "problem": finding.problem,
                        "reason": finding.suggestion,
                    }
                )

        report_path = output / REPORT_FILENAME
        report_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return report
    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise
