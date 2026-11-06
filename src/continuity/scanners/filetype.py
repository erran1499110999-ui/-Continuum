"""只读文件类型识别。

原则（AGENTS.md 规则 9）：只依据可验证的结构特征判断，不猜测字段含义；
无法确定时返回 TEXT/JSON/UNKNOWN，由后续阶段用真实样本扩充兼容矩阵。
"""

from __future__ import annotations

import json
from pathlib import Path

from ..models import FileKind
from ..pngutil import PNG_MAGIC, read_png_info

_PNG_SCAN_LIMIT = 4 * 1024 * 1024  # PNG 块扫描最多读取 4 MiB（tEXt chara 块通常在文件前部）
_JSON_MAX_BYTES = 8 * 1024 * 1024
_JSONL_SAMPLE_LINES = 20

# 角色卡 JSON 的最低结构特征（仅用于识别，不校验字段语义）
_CARD_KEYS = frozenset({"name", "first_mes"})


def _read_prefix(path: Path, limit: int) -> bytes:
    with path.open("rb") as f:
        return f.read(limit)


def _is_json_value(line: str) -> bool:
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False


def identify_file(path: Path) -> FileKind:
    """只读识别单个文件的类型。IO 错误向上抛出，由调用方记录。"""
    if path.is_symlink():
        return FileKind.UNKNOWN
    if not path.is_file():
        raise FileNotFoundError(path)
    size = path.stat().st_size
    if size == 0:
        return FileKind.TEXT

    head = _read_prefix(path, min(size, 8))
    if head == PNG_MAGIC:
        data = _read_prefix(path, min(size, _PNG_SCAN_LIMIT))
        info = read_png_info(data)
        if size <= _PNG_SCAN_LIMIT:
            # 完整校验：块边界、CRC、IEND；损坏时绝不与"普通图片"混淆
            if info.errors or not info.complete:
                return FileKind.CORRUPT_PNG
            if "chara" in info.text_chunks:
                return FileKind.CHARACTER_CARD_PNG
            return FileKind.PNG
        # 超大 PNG：不整体校验（避免误报损坏），仅做前部 chara 探测
        if "chara" in info.text_chunks:
            return FileKind.CHARACTER_CARD_PNG
        return FileKind.PNG

    # 头部含 NUL 即二进制：文本编码几乎不可能包含 NUL（识别依据见 format-compatibility.md）
    if b"\x00" in head:
        return FileKind.BINARY

    if size > _JSON_MAX_BYTES:
        return FileKind.TEXT
    text = _read_prefix(path, min(size, _JSON_MAX_BYTES))
    try:
        decoded = text.decode("utf-8")
    except UnicodeDecodeError:
        # 非 UTF-8 视作二进制：当前版本不猜测编码（UTF-16/GBK 识别待扩展，见已知限制）
        return FileKind.BINARY

    stripped = decoded.lstrip()
    if stripped.startswith(("{", "[")):
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            pass
        else:
            # 卡判定只查结构特征（规则 9）：V1 平铺卡有 name+first_mes；V2 包裹卡以 spec 开头
            if isinstance(obj, dict) and (
                _CARD_KEYS.issubset(obj.keys())
                or (
                    isinstance(obj.get("spec"), str)
                    and obj["spec"].startswith("chara_card")
                )
            ):
                return FileKind.CHARACTER_CARD_JSON
            return FileKind.JSON

    # JSONL：抽样前若干非空行，多数为合法 JSON 即判定（容忍个别损坏行）
    # 启发式边界：至少 2 行合法且占比过半，避免把普通文本误判为聊天记录
    lines = [ln for ln in decoded.splitlines() if ln.strip()]
    if lines:
        sample = lines[:_JSONL_SAMPLE_LINES]
        parsed_count = sum(1 for ln in sample if _is_json_value(ln))
        if parsed_count >= 2 and parsed_count * 2 >= len(sample):
            return FileKind.CHAT_JSONL
    return FileKind.TEXT
