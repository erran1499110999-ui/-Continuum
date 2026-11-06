"""SillyTavern 迁移引擎：解析源数据 → 标准化导出到新目录 → 逐项验证并生成报告。

对应企划书提示词 6（适配器）与提示词 7（迁移验证）：
- 源目录只读；输出目录必须不存在且不得位于源目录之内；
- 每张角色卡都单独导出并逐项验证，绝不静默丢弃（0.1.1 修复）；
- 未知字段原样保留并写入 sidecar 清单；
- 聊天中无法解析的原始行保留到 bad-lines sidecar，绝不静默丢弃（0.1.1 修复）；
- 报告不写入绝对路径与原始字段值（隐私脱敏），差异以长度与摘要描述（0.1.1 修复）；
- "完整性"分数语义明确为"已检查支持项匹配率"，分母、排除项与各类别计数
  均写入报告（0.1.1 修复）；
- 附件复制受统一资源预算约束（0.1.1 修复）。
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional

from .. import __version__
from ..adapters.sillytavern import (
    AdapterError,
    export_card_v2,
    looks_like_world_info,
    parse_card_file,
    parse_chat_jsonl,
    parse_world_info,
    serialize_chat,
)
from ..hashing import sha256_file
from ..limits import DEFAULT_LIMITS, ResourceLimits
from ..models import FileKind, Severity, utc_now_iso
from ..scanners.scan import ScanError, ScanFile, scan_directory

CARD_OUT_FILENAME = "character-card.json"
SIDECAR_FILENAME = "unsupported-fields.json"
REPORT_FILENAME = "migration-report.json"
BAD_LINES_SUFFIX = ".bad-lines.txt"

# 逐项验证的角色卡字段（目标端 SillyTavern 支持的字段）
VERIFIED_CARD_FIELDS = (
    "name",
    "description",
    "personality",
    "scenario",
    "first_mes",
    "alternate_greetings",
    "tags",
    "creator",
    "creator_notes",
    "character_version",
    "mes_example",
    "system_prompt",
    "post_history_instructions",
)


class MigrationError(Exception):
    """迁移过程中的错误，信息面向用户。"""


@dataclass
class MigrationReport:
    created_at: str
    tool_version: str
    source_dir_name: str
    output_dir_name: str
    target_client: str = "SillyTavern"
    primary_card: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    completeness: Dict[str, Any] = field(default_factory=dict)
    unsupported_sidecar: str = ""
    warnings: List[str] = field(default_factory=list)
    needs_review: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _to_path(rel: str) -> Path:
    return Path(*PurePosixPath(rel).parts)


def _value_digest(v: Any) -> tuple:
    """返回 (utf-8 长度, sha256 前 16 位)——用于脱敏描述差异，绝不写入原始值。"""
    try:
        s = json.dumps(v, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        s = repr(v)
    b = s.encode("utf-8")
    return len(b), hashlib.sha256(b).hexdigest()[:16]


def _card_out_name(index: int, rel: str) -> str:
    """为第 index 张角色卡生成不含歧义的输出文件名。"""
    p = PurePosixPath(rel)
    if p.suffix.lower() == ".png":
        return f"{index:02d}_{p.stem}.from_png.json"
    return f"{index:02d}_{p.stem}.json"


def migrate_sillytavern(
    source_dir: Path,
    output_dir: Path,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> MigrationReport:
    """把 source_dir 中的 SillyTavern 数据迁移到新的 output_dir 并逐项验证。"""
    source = source_dir.resolve()
    if not source.is_dir():
        raise MigrationError(f"源目录不存在: {source_dir}")
    output = output_dir.resolve()
    if output.exists():
        raise MigrationError(f"迁移输出目录已存在，请选择新目录: {output_dir}")
    if output.is_relative_to(source):
        raise MigrationError(f"迁移输出目录不能位于源目录之内: {output_dir}")

    output.mkdir(parents=True)
    try:
        try:
            scan = scan_directory(source, limits)
        except ScanError as exc:
            raise MigrationError(str(exc)) from exc
        report = MigrationReport(
            created_at=utc_now_iso(),
            tool_version=__version__,
            source_dir_name=source.name,
            output_dir_name=output.name,
        )

        card_files = sorted(
            (f for f in scan.files if f.kind in (FileKind.CHARACTER_CARD_JSON, FileKind.CHARACTER_CARD_PNG)),
            key=lambda f: f.rel_path,
        )
        if not card_files:
            corrupt_pngs = [f for f in scan.files if f.kind is FileKind.CORRUPT_PNG]
            if corrupt_pngs:
                raise MigrationError(
                    "发现损坏或截断的 PNG（疑似角色卡），无法安全迁移，请修复或从备份恢复: "
                    + "、".join(f.rel_path for f in corrupt_pngs[:5])
                )
            raise MigrationError("未找到角色卡（PNG tEXt chara 块或含 spec=chara_card 的 JSON）")
        json_cards = [f for f in card_files if f.kind is FileKind.CHARACTER_CARD_JSON]
        primary = json_cards[0] if json_cards else card_files[0]
        report.primary_card = primary.rel_path

        parsed_cards: Dict[str, Any] = {}
        for f in card_files:
            try:
                parsed_cards[f.rel_path] = parse_card_file(
                    source / _to_path(f.rel_path), f.kind, limits=limits
                )
            except AdapterError as exc:
                raise MigrationError(str(exc)) from exc

        chat_files = [
            f for f in sorted(scan.files, key=lambda x: x.rel_path) if f.kind is FileKind.CHAT_JSONL
        ]
        world_files: List[ScanFile] = []
        for f in sorted(scan.files, key=lambda x: x.rel_path):
            if f.kind is FileKind.JSON:
                try:
                    obj = json.loads((source / _to_path(f.rel_path)).read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                if looks_like_world_info(obj):
                    world_files.append(f)

        handled = (
            {f.rel_path for f in card_files}
            | {f.rel_path for f in chat_files}
            | {f.rel_path for f in world_files}
        )
        corrupt_files = [f for f in scan.files if f.kind is FileKind.CORRUPT_PNG]
        asset_files = [
            f
            for f in sorted(scan.files, key=lambda x: x.rel_path)
            if f.rel_path not in handled and f.kind is not FileKind.CORRUPT_PNG
        ]

        # —— 标准化导出：主卡 + 每张卡 ——
        (output / CARD_OUT_FILENAME).write_text(
            json.dumps(export_card_v2(parsed_cards[primary.rel_path]), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (output / "cards").mkdir()
        for idx, f in enumerate(card_files):
            dst = output / "cards" / _card_out_name(idx, f.rel_path)
            dst.write_text(
                json.dumps(export_card_v2(parsed_cards[f.rel_path]), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        for f in chat_files:
            try:
                parsed = parse_chat_jsonl(source / _to_path(f.rel_path), limits=limits)
            except AdapterError as exc:
                raise MigrationError(str(exc)) from exc
            src_file = source / _to_path(f.rel_path)
            dst = output / "chats" / _to_path(f.rel_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(serialize_chat(parsed), encoding="utf-8")
            if parsed.bad_lines:
                # 字节级保留：原始 JSONL 完整字节副本 + 坏行字节索引
                original_rel = "chats/" + f.rel_path + ".original"
                shutil.copy2(src_file, output / "chats" / _to_path(f.rel_path + ".original"))
                sidecar_rel = "chats/" + f.rel_path + BAD_LINES_SUFFIX
                sidecar = output / "chats" / _to_path(f.rel_path + BAD_LINES_SUFFIX)
                sidecar.parent.mkdir(parents=True, exist_ok=True)
                with sidecar.open("wb") as sf:
                    sf.write(
                        "索引格式：'第 N 行: <该行原始字节（不含行结束符，含行内空白）>'\n"
                        "逐字节还原请使用同目录下 <文件名>.original 完整字节副本。\n".encode("utf-8")
                    )
                    for lineno, raw in parsed.bad_lines:
                        sf.write(f"第 {lineno} 行: ".encode("utf-8") + raw + b"\n")
                report.needs_review.append(
                    f"{f.rel_path}: 存在无法解析的行；原始文件字节副本保留于 {original_rel}，"
                    f"坏行字节索引保留于 {sidecar_rel}"
                )
            for w in parsed.warnings:
                report.warnings.append(f"{f.rel_path}: {w}")

        for f in world_files:
            parsed = parse_world_info(source / _to_path(f.rel_path))
            dst = output / "worldinfo" / _to_path(f.rel_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(parsed.raw, ensure_ascii=False, indent=2), encoding="utf-8")

        asset_hashes: Dict[str, str] = {}
        asset_total = 0
        for f in asset_files:
            src = source / _to_path(f.rel_path)
            size = src.stat().st_size
            if size > limits.max_file_bytes:
                raise MigrationError(
                    f"附件超过单文件上限 {limits.max_file_bytes} 字节: {f.rel_path}"
                )
            asset_total += size
            if asset_total > limits.max_total_bytes:
                raise MigrationError(f"附件累计大小超过上限 {limits.max_total_bytes} 字节")
            dst = output / "assets" / _to_path(f.rel_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            asset_hashes[f.rel_path] = sha256_file(dst)

        # 损坏 PNG：按字节原样保留为附件，明确进入待处理清单，绝不静默混入常规附件；
        # 与普通附件共用同一累计资源预算（第三轮审查 P2）
        damaged_rels: List[str] = []
        for f in corrupt_files:
            src = source / _to_path(f.rel_path)
            size = src.stat().st_size
            if size > limits.max_file_bytes:
                raise MigrationError(
                    f"损坏文件超过单文件上限 {limits.max_file_bytes} 字节: {f.rel_path}"
                )
            asset_total += size
            if asset_total > limits.max_total_bytes:
                raise MigrationError(
                    f"附件与损坏文件累计大小超过上限 {limits.max_total_bytes} 字节"
                )
            dst = output / "assets" / _to_path(f.rel_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if sha256_file(dst) != sha256_file(src):
                raise MigrationError(f"损坏文件复制后哈希不一致: {f.rel_path}")
            damaged_rels.append(f.rel_path)
            report.needs_review.append(
                f"{f.rel_path}: PNG 结构损坏或截断，已按字节原样保留为附件，"
                "未做内容校验，需人工确认"
            )

        # 无法读取/识别的文件（未进入文件清单）：明确标记未迁移，迁移结果不完整
        error_rels = sorted({f.file for f in scan.findings if f.severity is Severity.ERROR})
        for rel in error_rels:
            report.needs_review.append(f"{rel}: 无法读取或识别，未迁移，需人工确认")

        # —— sidecar：未知字段清单（按卡分列）——
        sidecar: Dict[str, Any] = {"unknown_fields": {}}
        for rel, card in parsed_cards.items():
            if card.unknown_keys:
                sidecar["unknown_fields"][rel] = card.unknown_keys
        (output / SIDECAR_FILENAME).write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        report.unsupported_sidecar = SIDECAR_FILENAME

        # —— 逐项验证（提示词 7）——
        _verify(
            report,
            source,
            output,
            parsed_cards,
            card_files,
            chat_files,
            world_files,
            asset_hashes,
            source_files_total=len(scan.files),
            limits=limits,
            unprocessed_files=error_rels,
            damaged_files=damaged_rels,
        )

        (output / REPORT_FILENAME).write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return report
    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise


def _verify(
    report: MigrationReport,
    source: Path,
    output: Path,
    parsed_cards: Dict[str, Any],
    card_files: List[ScanFile],
    chat_files: List[ScanFile],
    world_files: List[ScanFile],
    asset_hashes: Dict[str, str],
    *,
    source_files_total: int,
    limits: ResourceLimits,
    unprocessed_files: List[str],
    damaged_files: List[str],
) -> None:
    """把迁移输出逐项与源数据比较，填充报告 items 与"已检查支持项匹配率"。"""
    matched = 0
    checked = 0
    excluded: List[str] = []

    for idx, f in enumerate(card_files):
        rel = f.rel_path
        card = parsed_cards[rel]
        try:
            out_card = parse_card_file(
                output / "cards" / _card_out_name(idx, rel),
                FileKind.CHARACTER_CARD_JSON,
                limits=limits,
            )
        except AdapterError as exc:
            report.items.append(
                {"field": f"角色卡.{rel}", "status": "mismatch", "detail": f"输出角色卡无法解析: {exc}"}
            )
            checked += 1
            continue
        for fn in VERIFIED_CARD_FIELDS:
            field = f"角色卡.{rel}.{fn}"
            src_val = card.field_value(fn)
            out_val = out_card.field_value(fn)
            if src_val in (None, [], ""):
                report.items.append(
                    {
                        "field": field,
                        "status": "excluded",
                        "detail": "源端不存在或为空，未计入匹配率分母",
                    }
                )
                excluded.append(field)
                continue
            if src_val == out_val:
                report.items.append({"field": field, "status": "ok", "detail": "源与目标一致"})
                matched += 1
            else:
                n1, h1 = _value_digest(src_val)
                n2, h2 = _value_digest(out_val)
                report.items.append(
                    {
                        "field": field,
                        "status": "mismatch",
                        "detail": f"不一致（源长度 {n1}/摘要 {h1}，目标长度 {n2}/摘要 {h2}）",
                    }
                )
            checked += 1
        for k in card.unknown_keys:
            report.items.append(
                {
                    "field": f"角色卡.{rel}.{k}",
                    "status": "unsupported",
                    "detail": "未知字段，原样保留于输出与 sidecar，未计入匹配率分母",
                }
            )

    for f in chat_files:
        src_chat = parse_chat_jsonl(source / _to_path(f.rel_path), limits=limits)
        out_chat = parse_chat_jsonl(output / "chats" / _to_path(f.rel_path), limits=limits)
        if src_chat.warnings:
            report.items.append(
                {
                    "field": f"聊天.{f.rel_path}.消息",
                    "status": "needs_review",
                    "detail": (
                        f"{len(src_chat.messages)} 条可解析消息已迁移；"
                        f"{len(src_chat.warnings)} 处无法解析的行未迁移，"
                        f"原始字节已保留于 chats/{f.rel_path}{BAD_LINES_SUFFIX}，需人工确认"
                    ),
                }
            )
            checked += 1
        elif src_chat.messages == out_chat.messages:
            report.items.append(
                {
                    "field": f"聊天.{f.rel_path}.消息",
                    "status": "ok",
                    "detail": f"{len(src_chat.messages)} 条消息，顺序、时间戳与元数据一致",
                }
            )
            matched += 1
            checked += 1
        else:
            report.items.append(
                {
                    "field": f"聊天.{f.rel_path}.消息",
                    "status": "mismatch",
                    "detail": f"源 {len(src_chat.messages)} 条 != 目标 {len(out_chat.messages)} 条或内容不一致",
                }
            )
            checked += 1

    for f in world_files:
        src_w = parse_world_info(source / _to_path(f.rel_path))
        out_w = parse_world_info(output / "worldinfo" / _to_path(f.rel_path))
        if src_w.entries == out_w.entries:
            report.items.append(
                {
                    "field": f"世界书.{f.rel_path}.条目",
                    "status": "ok",
                    "detail": f"{len(src_w.entries)} 个条目，内容与触发条件一致",
                }
            )
            matched += 1
        else:
            report.items.append(
                {"field": f"世界书.{f.rel_path}.条目", "status": "mismatch", "detail": "条目内容不一致"}
            )
        checked += 1

    for rel, output_sha in asset_hashes.items():
        src_sha = sha256_file(source / _to_path(rel))
        if src_sha == output_sha:
            report.items.append(
                {"field": f"附件.{rel}", "status": "ok", "detail": "SHA-256 一致"}
            )
            matched += 1
        else:
            report.items.append(
                {"field": f"附件.{rel}", "status": "mismatch", "detail": "SHA-256 不一致"}
            )
        checked += 1

    score = (matched / checked) if checked else 1.0
    report.completeness = {
        "score_label": "已检查支持项匹配率",
        "score": round(score, 4),
        "matched": matched,
        "checked": checked,
        "denominator_explanation": (
            "分子/分母仅统计目标端（SillyTavern）支持且源端存在的字段："
            "全部角色卡的已知字段 + 聊天消息 + 世界书条目 + 附件哈希；"
            "未知字段（unsupported）与源端缺失字段（excluded）不计入分母，另行单列。"
        ),
        "excluded": excluded,
        "source_files_total": source_files_total,
        "migrated_cards": len(parsed_cards),
        "migrated_chats": len(chat_files),
        "migrated_worldinfo": len(world_files),
        "migrated_assets": len(asset_hashes),
        "coverage_complete": not unprocessed_files,
        "unprocessed_files": unprocessed_files,
        "damaged_files": damaged_files,
    }
