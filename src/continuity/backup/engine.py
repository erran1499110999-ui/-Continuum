"""本地备份引擎：只读源目录 → 备份包 → 恢复到新目录并逐文件校验哈希。

安全规则（企划书提示词 4）：
- 源目录全程只读，备份过程绝不修改源；
- 备份以"单次读取同时完成复制与哈希"避免先哈希后复制的并发竞态，
  若文件在备份期间发生变化则中止并报告；
- 恢复先对全部清单条目做预校验（路径安全、单文件与总大小、存在性），
  恢复到临时目录并在全部哈希通过后原子发布到目标目录；
  失败时清理临时结果，绝不留下貌似完整的部分恢复目录；
- manifest 相对路径禁止绝对路径、盘符、.. 与反斜杠，并有 resolve 二次校验；
- 符号链接默认跳过并记录警告，不跟随。
"""

from __future__ import annotations

import hashlib
import os
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import List, Optional, Set, Tuple

from .. import __version__
from ..hashing import sha256_file
from ..models import BundleManifest, ManifestEntry, utc_now_iso
from ..scanners.filetype import identify_file
from .manifest import read_manifest, write_manifest

FILES_DIR_NAME = "files"
_COPY_CHUNK = 1024 * 1024  # 1 MiB


class BackupError(Exception):
    """备份/恢复过程中的错误，信息面向用户。"""


@dataclass
class BackupOptions:
    max_file_bytes: int = 256 * 1024 * 1024  # 单文件上限 256 MiB
    max_total_bytes: int = 2 * 1024 ** 3  # 总大小上限 2 GiB


@dataclass
class RestoreReport:
    restored: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    extra_files: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class VerifyReport:
    ok: bool = True
    checked: int = 0
    mismatches: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    extra_files: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def safe_join(base: Path, rel_path: str) -> Path:
    """把清单相对路径安全地拼接到 base 下。

    拒绝空路径、绝对路径、盘符、.. 与反斜杠；并用 resolve 后的
    is_relative_to 二次校验，防止符号链接逃逸。
    """
    if rel_path in ("", "."):
        raise BackupError(f"拒绝不安全的相对路径: {rel_path!r}")
    # POSIX 语义拆分：\ 不参与分段，因此 Windows 反斜杠只能藏在段内，由下面循环逐段拒绝
    parts = PurePosixPath(rel_path)
    if parts.is_absolute() or ".." in parts.parts:
        raise BackupError(f"拒绝不安全的相对路径: {rel_path!r}")
    for part in parts.parts:
        if "\\" in part or ":" in part or "\x00" in part:
            raise BackupError(f"拒绝不安全的相对路径: {rel_path!r}")
    # resolve 二次校验：即使以上全过，若中间目录是符号链接可把目标带出 base，此处兜底拦截
    base_res = base.resolve()
    target = base_res / Path(*parts.parts)
    if not target.resolve(strict=False).is_relative_to(base_res):
        raise BackupError(f"路径逃逸 base 目录: {rel_path!r}")
    return target


def _rel_of(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _extra_files(files_dir: Path, known: Set[str]) -> List[str]:
    extra: List[str] = []
    for dirpath, dirnames, filenames in os.walk(files_dir, followlinks=False):
        dir_p = Path(dirpath)
        dirnames.sort()
        dirnames[:] = [d for d in dirnames if not (dir_p / d).is_symlink()]
        for name in sorted(filenames):
            if (dir_p / name).is_symlink():
                continue
            rel = _rel_of(files_dir, dir_p / name)
            if rel not in known:
                extra.append(rel)
    return extra


def _copy_and_hash(src: Path, dst: Path) -> Tuple[int, str]:
    """单次读取源文件：流式写入目标副本并同步计算 SHA-256。

    返回 (读取字节数, 十六进制哈希)。清单哈希与备份内容必然一致；
    源文件变化检测由调用方通过 _stat_signature 前后比对完成。
    """
    h = hashlib.sha256()
    total = 0
    with src.open("rb") as fin, dst.open("wb") as fout:
        while True:
            chunk = fin.read(_COPY_CHUNK)
            if not chunk:
                break
            total += len(chunk)
            h.update(chunk)
            fout.write(chunk)
    return total, h.hexdigest()


def _stat_signature(path: Path) -> Tuple[int, int]:
    """返回文件变化签名（大小 + 最后修改时间，纳秒）。

    备份前后比较该签名属于**尽力检测**：无法检出"同长度改写并恢复 mtime"
    等刻意场景；如需强一致性请使用文件系统快照，并强烈建议备份期间
    保持源目录静止（见 README 数据安全承诺）。
    """
    st = path.stat()
    return st.st_size, st.st_mtime_ns


def create_backup(
    source_dir: Path,
    bundle_dir: Path,
    *,
    options: Optional[BackupOptions] = None,
    source_client: Optional[str] = None,
    source_client_version: Optional[str] = None,
) -> BundleManifest:
    """把 source_dir 中所有常规文件只读备份到新的 bundle_dir。

    bundle_dir 必须不存在，且不得位于 source_dir 之内。
    """
    opts = options or BackupOptions()
    source = source_dir.resolve()
    if not source.is_dir():
        raise BackupError(f"源目录不存在: {source_dir}")
    bundle = bundle_dir.resolve()
    if bundle.exists():
        raise BackupError(f"备份目标已存在，请选择新目录: {bundle_dir}")
    if bundle.is_relative_to(source):
        raise BackupError(f"备份目标不能位于源目录之内: {bundle_dir}")

    bundle.mkdir(parents=True)
    (bundle / FILES_DIR_NAME).mkdir()
    try:
        entries: List[ManifestEntry] = []
        warnings: List[str] = []
        total = 0
        for dirpath, dirnames, filenames in os.walk(source, followlinks=False):
            dir_p = Path(dirpath)
            dirnames.sort()
            kept: List[str] = []
            for name in dirnames:
                if (dir_p / name).is_symlink():
                    warnings.append(f"跳过符号链接目录: {_rel_of(source, dir_p / name)}")
                else:
                    kept.append(name)
            dirnames[:] = kept
            for name in sorted(filenames):
                src = dir_p / name
                rel = _rel_of(source, src)
                if src.is_symlink():
                    warnings.append(f"跳过符号链接: {rel}")
                    continue
                size = src.stat().st_size
                if size > opts.max_file_bytes:
                    raise BackupError(
                        f"文件超过单文件上限 {opts.max_file_bytes} 字节: {rel}"
                    )
                total += size
                if total > opts.max_total_bytes:
                    raise BackupError(
                        f"备份总大小超过上限 {opts.max_total_bytes} 字节（处理到 {rel} 时超出）"
                    )
                dst = bundle / FILES_DIR_NAME / Path(*PurePosixPath(rel).parts)
                dst.parent.mkdir(parents=True, exist_ok=True)
                # 竞态防线：复制+哈希单次读取完成，前后 stat 签名比对捕捉期间变化
                sig_before = _stat_signature(src)
                try:
                    copied, sha = _copy_and_hash(src, dst)
                except OSError as exc:
                    raise BackupError(f"无法读取文件: {rel}（{exc}）") from exc
                sig_after = _stat_signature(src)
                if copied != size or sig_before != sig_after:
                    raise BackupError(
                        f"文件在备份期间发生变化，已中止: {rel}"
                        f"（初始 {size} 字节，实际读取 {copied} 字节；"
                        f"修改时间 {sig_before[1]} → {sig_after[1]}）"
                    )
                shutil.copystat(src, dst)
                kind = identify_file(src).value
                entries.append(ManifestEntry(rel_path=rel, size=copied, sha256=sha, kind=kind))
        manifest = BundleManifest(
            bundle_id=str(uuid.uuid4()),
            bundle_version="1.0",
            created_at=utc_now_iso(),
            source_client=source_client,
            source_client_version=source_client_version,
            tool_version=__version__,
            entries=entries,
            warnings=warnings,
        )
        write_manifest(bundle, manifest)
        return manifest
    except Exception:
        shutil.rmtree(bundle, ignore_errors=True)
        raise


def restore_backup(
    bundle_dir: Path,
    dest_dir: Path,
    *,
    options: Optional[BackupOptions] = None,
) -> RestoreReport:
    """把备份包恢复到新的 dest_dir，逐文件校验大小与哈希。

    先对全部清单条目预校验（路径安全、存在性、单文件与总大小上限），
    再恢复到临时目录；全部哈希通过后原子发布为 dest_dir。
    任何失败都会清理临时结果并抛出 BackupError，绝不留下部分恢复目录。
    """
    opts = options or BackupOptions()
    bundle = bundle_dir.resolve()
    manifest = read_manifest(bundle)
    dest = dest_dir.resolve()
    if dest.exists():
        raise BackupError(f"恢复目标已存在，为不覆盖任何数据请选择新目录: {dest_dir}")
    if dest.is_relative_to(bundle):
        raise BackupError(f"恢复目标不能位于备份包之内: {dest_dir}")

    files_dir = bundle / FILES_DIR_NAME
    if not files_dir.is_dir():
        raise BackupError(f"备份包缺少 {FILES_DIR_NAME} 目录: {bundle_dir}")

    # —— 预校验全部条目，任何问题都在创建输出之前失败 ——
    total = 0
    for entry in manifest.entries:
        safe_join(files_dir, entry.rel_path)
        safe_join(dest, entry.rel_path)
        if entry.size > opts.max_file_bytes:
            raise BackupError(
                f"文件超过单文件上限 {opts.max_file_bytes} 字节: {entry.rel_path}"
            )
        total += entry.size
        if total > opts.max_total_bytes:
            raise BackupError(f"备份包总大小超过上限 {opts.max_total_bytes} 字节")
    for entry in manifest.entries:
        src = safe_join(files_dir, entry.rel_path)
        if not src.is_file():
            raise BackupError(f"备份包中缺少清单列出的文件: {entry.rel_path}")
        if src.stat().st_size != entry.size:
            raise BackupError(f"文件大小与清单不符: {entry.rel_path}")

    # staging 与 dest 同父目录且命名固定（dest.name + ".restoring"）：
    # 保证 staging.replace(dest) 是同卷原子改名，不会产生跨盘复制
    staging = dest.with_name(dest.name + ".restoring")
    if staging.exists():
        raise BackupError(f"临时恢复目录已存在，请先处理: {staging}")
    staging.mkdir(parents=True)
    try:
        report = RestoreReport()
        for entry in manifest.entries:
            src = safe_join(files_dir, entry.rel_path)
            dst = safe_join(staging, entry.rel_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            actual = sha256_file(dst)
            if actual != entry.sha256:
                raise BackupError(
                    f"恢复后哈希校验失败: {entry.rel_path}"
                    f"（清单 {entry.sha256}，实际 {actual}）"
                )
            report.restored += 1

        report.extra_files = _extra_files(files_dir, {e.rel_path for e in manifest.entries})
        report.warnings.extend(manifest.warnings)
        if report.extra_files:
            report.warnings.append(
                f"备份包中存在未被清单记录的文件（{len(report.extra_files)} 个），"
                "这些文件不会被恢复"
            )
        staging.replace(dest)  # 原子发布：全部校验通过后目录才以目标名出现
        return report
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_bundle(bundle_dir: Path) -> VerifyReport:
    """重新计算备份包内所有文件的哈希并与清单比对（完整性检查）。"""
    bundle = bundle_dir.resolve()
    manifest = read_manifest(bundle)
    files_dir = bundle / FILES_DIR_NAME
    report = VerifyReport()
    if not files_dir.is_dir():
        report.missing.append(FILES_DIR_NAME)
        report.ok = False
        return report
    known = {e.rel_path for e in manifest.entries}
    for entry in manifest.entries:
        src = safe_join(files_dir, entry.rel_path)
        if not src.is_file():
            report.missing.append(entry.rel_path)
            report.ok = False
            continue
        actual = sha256_file(src)
        report.checked += 1
        if actual != entry.sha256 or src.stat().st_size != entry.size:
            report.mismatches.append(entry.rel_path)
            report.ok = False
    report.extra_files = _extra_files(files_dir, known)
    if report.extra_files:
        # 清单外文件 = 完整性失败（可能是误操作、恶意植入或备份包被修改）
        report.ok = False
        report.warnings.append(
            f"备份包中存在未被清单记录的文件（{len(report.extra_files)} 个），"
            "完整性检查视为未通过"
        )
    return report
