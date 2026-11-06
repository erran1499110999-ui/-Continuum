"""API 处理器（W1：health / version；W2：scan；P5：ping / backup / emergency-backup / restore）。

约定：处理器为无状态纯函数，返回可 JSON 化的 dict；
HTTP 事务（token、Host、状态码、JSON 编码）由 server.py 统一处理。
后续阶段在此增量添加 job 端点（repair/migrate 等）。
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Optional

from .. import __version__
from ..backup import create_backup, restore_backup, verify_bundle
from ..scanners.scan import scan_directory
from .views import scan_report_to_json

TOOL_NAME = "continuity-studio"


def health() -> Dict[str, str]:
    """服务健康检查（不含任何路径/数据信息）。"""
    return {"status": "ok"}


def ping() -> Dict[str, str]:
    """免 token 的存活探测（供 ST 插件 Image() 探测本机服务）。

    安全约束（Q12）：响应只允许 {"status":"ok"}，绝不携带版本号/工具名等
    指纹信息——避免向探测方泄露本地软件版本。
    """
    return {"status": "ok"}


def version() -> Dict[str, str]:
    """工具版本信息。"""
    return {"tool": TOOL_NAME, "version": __version__}


def scan_worker(source: str, *, log: Optional[Callable[[str], None]] = None) -> Dict[str, object]:
    """在 job 工作线程内执行只读扫描，返回序列化报告（源目录绝不写入）。

    错误传播约定：引擎抛出的 ScanError/OSError（资源上限、权限等）不在此捕获，
    由 JobManager 捕获为 failed 状态并把面向用户的错误文案透传给前端——
    保证 HTTP 错误与 CLI 错误来自同一引擎、同一文案。
    """
    report = scan_directory(Path(source))
    data = scan_report_to_json(report)
    if log is not None:
        log(f"扫描完成: {len(report.files)} 个文件，{len(report.findings)} 项发现")
    return data


def backup_worker(
    source: str,
    bundle: str,
    *,
    source_client: Optional[str] = None,
    source_client_version: Optional[str] = None,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, object]:
    """在 job 工作线程内执行备份（复用 backup/engine.py create_backup，薄壳不重写逻辑）。

    引擎保证：bundle 必须不存在且不在 source 内、源只读、单次读取复制+哈希、
    期间变化即中止；失败自动清理不完整备份包。
    """
    manifest = create_backup(
        Path(source),
        Path(bundle),
        source_client=source_client,
        source_client_version=source_client_version,
    )
    data: Dict[str, object] = {
        "bundle": str(bundle),
        "manifest": manifest.model_dump(mode="json"),
    }
    if log is not None:
        log(f"备份完成: {len(manifest.entries)} 个文件")
    return data


def emergency_backup_worker(
    source: str,
    output: str,
    *,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, object]:
    """一键急救备份：create_backup 的简化入口 + 可恢复性自检。

    备份完成后立即对刚产出的备份包跑 verify_bundle（重新计算哈希比对清单），
    把「是否可恢复」的自检结论随结果返回——急救场景要的不是"看起来做了"，
    而是"现在就能恢复"。
    """
    manifest = create_backup(Path(source), Path(output))
    verify = verify_bundle(Path(output))
    data: Dict[str, object] = {
        "bundle": str(output),
        "manifest": manifest.model_dump(mode="json"),
        "verify": {
            "ok": verify.ok,
            "checked": verify.checked,
            "mismatches": verify.mismatches,
            "missing": verify.missing,
            "extra_files": verify.extra_files,
            "warnings": verify.warnings,
        },
    }
    if log is not None:
        log(
            f"急救备份完成: {len(manifest.entries)} 个文件；"
            f"可恢复性自检: {'通过' if verify.ok else '未通过'}"
        )
    return data


def restore_worker(
    bundle: str,
    dest: str,
    *,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, object]:
    """在 job 工作线程内执行恢复（复用 restore_backup：预校验 + 临时目录 + 原子发布）。

    恢复绝不覆盖现有目录：dest 必须不存在；任何失败清理临时结果，
    绝不留下貌似完整的部分恢复目录（引擎保证，薄壳直接透传结论）。
    """
    report = restore_backup(Path(bundle), Path(dest))
    data: Dict[str, object] = {
        "restored": report.restored,
        "errors": report.errors,
        "warnings": report.warnings,
        "extra_files": report.extra_files,
        "ok": report.ok,
    }
    if log is not None:
        log(f"恢复完成: {report.restored} 个文件（{'校验通过' if report.ok else '存在问题'}）")
    return data
