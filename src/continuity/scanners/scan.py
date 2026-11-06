"""目录级只读扫描：类型识别、SHA-256、重复检测、结构异常提示。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from ..hashing import sha256_file
from ..limits import DEFAULT_LIMITS, ResourceLimits
from ..models import FileKind, RepairLevel, ScanFinding, Severity
from ..safety import EXECUTABLE_EXTENSIONS, SCRIPT_EXTENSIONS
from .filetype import identify_file


class ScanError(Exception):
    """扫描过程中的错误（含资源上限），信息面向用户。"""


@dataclass
class ScanFile:
    rel_path: str
    kind: FileKind
    size: int
    sha256: str
    warnings: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    root: str
    files: List[ScanFile] = field(default_factory=list)
    findings: List[ScanFinding] = field(default_factory=list)
    duplicates: List[List[str]] = field(default_factory=list)
    skipped_symlinks: List[str] = field(default_factory=list)


def _structural_findings(path: Path, rel: str, kind: FileKind, size: int) -> List[ScanFinding]:
    findings: List[ScanFinding] = []
    if size == 0:
        findings.append(
            ScanFinding(
                file=rel,
                problem="空文件",
                evidence="文件大小为 0 字节",
                suggestion="确认该文件是否为占位或未完成导出",
                severity=Severity.INFO,
            )
        )
        return findings
    suffix = path.suffix.lower()
    if suffix in EXECUTABLE_EXTENSIONS or suffix in SCRIPT_EXTENSIONS:
        findings.append(
            ScanFinding(
                file=rel,
                problem="可能包含可执行内容的文件",
                evidence=f"扩展名 {suffix}",
                suggestion="隔离处理：本工具绝不执行、不解析此类文件",
                severity=Severity.INFO,
                repair_level=RepairLevel.R3,
            )
        )
    if kind is FileKind.CORRUPT_PNG:
        findings.append(
            ScanFinding(
                file=rel,
                problem="PNG 结构损坏或不完整",
                evidence="块边界、CRC 或 IEND 校验失败",
                suggestion="从备份恢复原始文件（R2）；本工具不自动修复二进制损坏",
                severity=Severity.WARNING,
                repair_level=RepairLevel.R2,
            )
        )
    if kind is FileKind.TEXT:
        with path.open("rb") as f:
            head = f.read(1024).decode("utf-8", errors="replace").lstrip()
        if head.startswith("{"):
            findings.append(
                ScanFinding(
                    file=rel,
                    location="文件开头",
                    problem="疑似损坏或不完整的 JSON 文件",
                    evidence="文件以 { 开头但无法按 JSON 解析",
                    suggestion=(
                        "末尾多余逗号可由修复引擎自动修复（R0）；"
                        "截断或编码问题仅提供人工建议（R2），请从备份恢复"
                    ),
                    severity=Severity.WARNING,
                    repair_level=RepairLevel.R2,
                )
            )
    return findings


def scan_directory(root: Path, limits: ResourceLimits = DEFAULT_LIMITS) -> ScanReport:
    """只读扫描 root 目录，返回文件清单、发现与重复组。

    受统一资源预算约束（文件数、累计字节、单文件大小、目录深度），
    超限时抛出 ScanError，绝不输出貌似完整的结果。
    """
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"目录不存在: {root}")
    report = ScanReport(root=str(root))
    by_hash: Dict[str, List[str]] = {}
    file_count = 0
    total_bytes = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dir_p = Path(dirpath)
        depth = len(dir_p.relative_to(root).parts)
        if depth > limits.max_depth:
            raise ScanError(f"目录深度超过上限 {limits.max_depth}: {dir_p}")
        dirnames.sort()
        kept: List[str] = []
        for name in dirnames:
            child = dir_p / name
            if child.is_symlink():
                report.skipped_symlinks.append(child.relative_to(root).as_posix())
            else:
                kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = dir_p / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                report.skipped_symlinks.append(rel)
                continue
            try:
                size = path.stat().st_size
                if size > limits.max_file_bytes:
                    raise ScanError(
                        f"文件超过单文件上限 {limits.max_file_bytes} 字节: {rel}"
                    )
                file_count += 1
                if file_count > limits.max_files:
                    raise ScanError(f"文件数超过上限 {limits.max_files}")
                total_bytes += size
                if total_bytes > limits.max_total_bytes:
                    raise ScanError(f"累计大小超过上限 {limits.max_total_bytes} 字节")
                sha = sha256_file(path)
                kind = identify_file(path)
            except OSError as exc:
                report.findings.append(
                    ScanFinding(
                        file=rel,
                        problem="无法读取或识别文件",
                        evidence=str(exc),
                        suggestion="检查文件权限或是否被其他程序占用",
                        severity=Severity.ERROR,
                    )
                )
                continue
            findings = _structural_findings(path, rel, kind, size)
            report.files.append(
                ScanFile(
                    rel_path=rel,
                    kind=kind,
                    size=size,
                    sha256=sha,
                    warnings=[f.problem for f in findings],
                )
            )
            report.findings.extend(findings)
            by_hash.setdefault(sha, []).append(rel)
    report.duplicates = [paths for paths in by_hash.values() if len(paths) > 1]
    return report
