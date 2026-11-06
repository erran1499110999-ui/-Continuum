"""Continuity Studio 命令行入口。

用法：
  continuity scan <目录>                  只读扫描并输出报告
  continuity backup <源目录> <备份目录>    创建备份包（源目录只读）
  continuity restore <备份目录> <目标目录> 恢复到新目录并逐文件校验哈希
  continuity verify <备份目录>             备份包完整性检查
  continuity repair <源目录> <输出目录>    只读诊断并生成修复副本（R0 自动修复）
  continuity migrate <源目录> <输出目录>   SillyTavern 迁移并逐项验证
  continuity version                       显示版本号
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional

from . import __version__
from .backup import BackupError, create_backup, restore_backup, verify_bundle
from .migration import MigrationError, migrate_sillytavern
from .repair import RepairError, apply_repairs
from .scanners import ScanError, scan_directory


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="continuity",
        description="Continuity Studio：本地优先的 AI 角色备份、诊断、修复与迁移工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="只读扫描目录并输出报告")
    p_scan.add_argument("path", help="要扫描的目录")

    p_backup = sub.add_parser("backup", help="创建本地备份包（源目录只读，绝不修改）")
    p_backup.add_argument("source", help="源目录")
    p_backup.add_argument("bundle", help="备份包目录（必须不存在）")
    p_backup.add_argument("--source-client", default=None, help="来源客户端名称，如 SillyTavern")
    p_backup.add_argument("--source-client-version", default=None, help="来源客户端版本")

    p_restore = sub.add_parser("restore", help="恢复到新目录并逐文件校验哈希")
    p_restore.add_argument("bundle", help="备份包目录")
    p_restore.add_argument("dest", help="目标目录（必须不存在，绝不覆盖）")

    p_verify = sub.add_parser("verify", help="备份包完整性检查")
    p_verify.add_argument("bundle", help="备份包目录")

    p_repair = sub.add_parser("repair", help="只读诊断并生成修复副本（R0 自动修复，R2 仅建议，R3 隔离）")
    p_repair.add_argument("source", help="源目录（只读，绝不修改）")
    p_repair.add_argument("output", help="修复输出目录（必须不存在）")
    p_repair.add_argument("--show-diffs", action="store_true", help="在终端打印修复差异")

    p_migrate = sub.add_parser("migrate", help="SillyTavern 迁移：解析→标准化导出→逐项验证报告")
    p_migrate.add_argument("source", help="源目录（只读，绝不修改）")
    p_migrate.add_argument("output", help="迁移输出目录（必须不存在）")

    sub.add_parser("version", help="显示版本号")
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "version":
        print(f"continuity-studio {__version__}")
        return 0

    if args.command == "scan":
        report = scan_directory(Path(args.path))
        counts = Counter(f.kind.value for f in report.files)
        print(f"扫描完成: {len(report.files)} 个文件（目录: {report.root}）")
        for kind in sorted(counts):
            print(f"  {kind}: {counts[kind]}")
        if report.skipped_symlinks:
            print(f"跳过符号链接 {len(report.skipped_symlinks)} 个（不跟随）")
        if report.duplicates:
            print(f"内容重复的文件组: {len(report.duplicates)}")
            for group in report.duplicates:
                print("  " + "、".join(group))
        for f in report.findings:
            print(f"[{f.severity.value}] {f.file}@{f.location}: {f.problem}")
            print(f"    建议: {f.suggestion}")
        return 0

    if args.command == "backup":
        manifest = create_backup(
            Path(args.source),
            Path(args.bundle),
            source_client=args.source_client,
            source_client_version=args.source_client_version,
        )
        print(f"备份完成: {len(manifest.entries)} 个文件")
        print(f"备份包: {args.bundle}")
        print(f"清单: {Path(args.bundle) / 'manifest.json'}")
        for w in manifest.warnings:
            print(f"警告: {w}")
        return 0

    if args.command == "restore":
        report = restore_backup(Path(args.bundle), Path(args.dest))
        print(f"恢复完成: {report.restored} 个文件（目标: {args.dest}）")
        for e in report.errors:
            print(f"错误: {e}", file=sys.stderr)
        for w in report.warnings:
            print(f"警告: {w}")
        return 0 if report.ok else 2

    if args.command == "verify":
        report = verify_bundle(Path(args.bundle))
        print(f"完整性检查: 已校验 {report.checked} 个文件，结果: {'通过' if report.ok else '未通过'}")
        for rel in report.mismatches:
            print(f"哈希不一致: {rel}")
        for rel in report.missing:
            print(f"缺失文件: {rel}")
        for rel in report.extra_files:
            print(f"未在清单中的额外文件: {rel}")
        for w in report.warnings:
            print(f"警告: {w}")
        return 0 if report.ok else 2

    if args.command == "repair":
        report = apply_repairs(Path(args.source), Path(args.output))
        print(
            f"修复副本生成: 共 {report.files_total} 个文件，"
            f"自动修复 {report.files_repaired} 个（R0 动作 {report.r0_applied} 项）"
        )
        print(f"报告: {Path(args.output) / 'repair-report.json'}")
        for f in report.fixes:
            print(f"  [{f['rule_id']}] {f['file']}: {f['reason']}")
            if args.show_diffs:
                print(f["diff"])
        if report.r2_advice:
            print(f"仅提供人工建议（R2）: {len(report.r2_advice)} 项")
            for a in report.r2_advice:
                print(f"  R2 {a['file']}: {a['suggestion']}")
        if report.r3_isolated:
            print(f"已隔离、绝不执行（R3）: {len(report.r3_isolated)} 个")
            for i in report.r3_isolated:
                print(f"  R3 {i['file']}: {i['problem']}")
        return 0

    if args.command == "migrate":
        report = migrate_sillytavern(Path(args.source), Path(args.output))
        print(f"迁移完成（目标客户端: {report.target_client}）")
        for item in report.items:
            print(f"  [{item['status']}] {item['field']}: {item['detail']}")
        comp = report.completeness
        print(
            f"已检查支持项匹配率: {comp['score'] * 100:.1f}%"
            f"（源文件 {comp['source_files_total']} 个：角色卡 {comp['migrated_cards']}、"
            f"聊天 {comp['migrated_chats']}、世界书 {comp['migrated_worldinfo']}、"
            f"附件 {comp['migrated_assets']}；校验 {comp['checked']} 项，"
            f"匹配 {comp['matched']} 项；排除 {len(comp['excluded'])} 项，见报告）"
        )
        if not comp.get("coverage_complete", True):
            print(
                f"迁移不完整: 部分源文件未迁移（{len(comp.get('unprocessed_files', []))} 个），"
                "详见报告的 unprocessed_files"
            )
        if comp.get("damaged_files"):
            print(
                f"警告: {len(comp['damaged_files'])} 个损坏 PNG 已按字节保留为附件，需人工确认"
            )
        if report.needs_review:
            print(f"需人工确认: {len(report.needs_review)} 项")
            for n in report.needs_review:
                print(f"  {n}")
        for w in report.warnings:
            print(f"警告: {w}")
        print(f"报告: {Path(args.output) / 'migration-report.json'}")
        # 覆盖不完整 = 非成功退出码（第三轮审查 P2）
        return 0 if comp.get("coverage_complete", True) else 1

    return 2


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (BackupError, RepairError, MigrationError, ScanError, OSError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
