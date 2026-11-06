"""SillyTavern 适配器：角色卡（PNG/JSON，V1/V2）、聊天 JSONL、World Info 的只读解析与标准化导出。

原则（AGENTS.md 规则 3、9）：
- 只解析数据，绝不执行任何导入内容；
- 未知字段原样保留（迁移时写入 sidecar 清单，绝不静默丢弃）；
- 字段语义仅依据可验证结构，不猜测。
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..limits import DEFAULT_LIMITS, ResourceLimits
from ..models import FileKind
from ..pngutil import read_png_info_stream

CHARA_KEY = "chara"

# 角色卡已知字段（V1 平铺 / V2 data 内通用）。
# 作用有二：解析时按字段映射到 ParsedCard；导出与未知字段分离时作为白名单——
# 不在本清单内的键一律进 unknown_keys/sidecar，绝不静默丢弃（规则 9）。
CARD_FIELDS = (
    "name",
    "description",
    "personality",
    "scenario",
    "first_mes",
    "alternate_greetings",
    "mes_example",
    "creator_notes",
    "system_prompt",
    "post_history_instructions",
    "tags",
    "creator",
    "character_version",
    "extensions",
)


class AdapterError(Exception):
    """适配器解析错误，信息面向用户。"""


@dataclass
class ParsedCard:
    format_version: str
    name: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None
    scenario: Optional[str] = None
    first_mes: Optional[str] = None
    alternate_greetings: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    creator: Optional[str] = None
    creator_notes: Optional[str] = None
    character_version: Optional[str] = None
    mes_example: Optional[str] = None
    system_prompt: Optional[str] = None
    post_history_instructions: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)
    unknown_keys: List[str] = field(default_factory=list)

    def field_value(self, field_name: str) -> Any:
        return getattr(self, field_name)


def _split_unknown(data: Dict[str, Any]) -> List[str]:
    # 排序输出：未知字段清单进入报告/sidecar，顺序稳定便于 diff 与审查
    return sorted(k for k in data if k not in CARD_FIELDS)


def _apply_fields(card: ParsedCard, data: Dict[str, Any]) -> None:
    card.name = data.get("name")
    card.description = data.get("description")
    card.personality = data.get("personality")
    card.scenario = data.get("scenario")
    card.first_mes = data.get("first_mes")
    ag = data.get("alternate_greetings")
    card.alternate_greetings = list(ag) if isinstance(ag, list) else []
    tags = data.get("tags")
    card.tags = list(tags) if isinstance(tags, list) else []
    card.creator = data.get("creator")
    card.creator_notes = data.get("creator_notes")
    card.character_version = data.get("character_version")
    card.mes_example = data.get("mes_example")
    card.system_prompt = data.get("system_prompt")
    card.post_history_instructions = data.get("post_history_instructions")


def parse_card_dict(raw: Dict[str, Any]) -> ParsedCard:
    """解析角色卡 JSON 对象（V1 平铺 / V2 包裹），未知字段记录但不丢弃。"""
    card = ParsedCard(format_version="v1")
    if isinstance(raw.get("spec"), str) and raw["spec"].startswith("chara_card_v2"):
        data = raw.get("data")
        if not isinstance(data, dict):
            raise AdapterError("角色卡 V2 缺少 data 对象")
        _apply_fields(card, data)
        card.format_version = "v2"
        card.raw = raw
        card.unknown_keys = _split_unknown(data)
        return card
    _apply_fields(card, raw)
    card.raw = raw
    card.unknown_keys = _split_unknown(raw)
    return card


def export_card_v2(card: ParsedCard) -> Dict[str, Any]:
    """标准化导出为 Character Card V2 结构；未知字段原样保留在 data 内。

    关键点：data 以 raw 为基础覆盖已知字段——未知字段随 raw 原样带出，
    实现「标准字段被规范化、其余字节级结构不被丢弃」的迁移目标。
    """
    data: Dict[str, Any] = dict(
        card.raw.get("data", {}) if card.format_version == "v2" else card.raw
    )
    data["name"] = card.name
    data["description"] = card.description
    data["personality"] = card.personality
    data["scenario"] = card.scenario
    data["first_mes"] = card.first_mes
    data["alternate_greetings"] = card.alternate_greetings
    data["tags"] = card.tags
    data["creator"] = card.creator
    data["creator_notes"] = card.creator_notes
    data["character_version"] = card.character_version
    data["mes_example"] = card.mes_example
    data["system_prompt"] = card.system_prompt
    data["post_history_instructions"] = card.post_history_instructions
    return {"spec": "chara_card_v2", "spec_version": "2.0", "data": data}


def parse_card_file(
    path: Path,
    kind: FileKind,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> ParsedCard:
    """只读解析角色卡文件（PNG tEXt chara 块或 JSON）。

    PNG 会做结构校验（块边界、CRC），损坏/截断时报错，绝不猜测内容；
    超过资源上限（角色卡 PNG 大小）时报错，绝不输出貌似完整的结果。
    """
    if kind is FileKind.CHARACTER_CARD_PNG:
        size = path.stat().st_size
        if size > limits.max_card_png_bytes:
            raise AdapterError(
                f"角色卡 PNG 超过大小上限 {limits.max_card_png_bytes} 字节: {path}"
            )
        info = read_png_info_stream(path)  # 流式逐块读取，不全量载入内存
        if info.errors:
            raise AdapterError(f"PNG 结构损坏或截断: {path}（{'；'.join(info.errors)}）")
        payload = info.text_chunks.get(CHARA_KEY)
        if not payload:
            raise AdapterError(f"PNG 角色卡缺少 {CHARA_KEY!r} 块内容: {path}")
        try:
            # validate=True：严格拒绝含非 base64 字符的 payload（损坏检测，规则 9）
            raw = json.loads(base64.b64decode(payload, validate=True))
        except (ValueError, json.JSONDecodeError) as exc:
            raise AdapterError(f"PNG 角色卡 chara 块解析失败: {path}（{exc}）") from exc
        if not isinstance(raw, dict):
            raise AdapterError(f"角色卡内容不是 JSON 对象: {path}")
        return parse_card_dict(raw)
    if kind in (FileKind.CHARACTER_CARD_JSON, FileKind.JSON):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise AdapterError(f"角色卡内容不是 JSON 对象: {path}")
        return parse_card_dict(raw)
    raise AdapterError(f"不支持的角色卡文件类型: {kind.value}")


@dataclass
class ParsedChat:
    messages: List[Dict[str, Any]]
    warnings: List[str] = field(default_factory=list)
    bad_lines: List[Tuple[int, bytes]] = field(default_factory=list)


def parse_chat_jsonl(
    path: Path,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> ParsedChat:
    """只读解析聊天 JSONL；无法解析的行跳过并保留原始字节（绝不编造、绝不静默丢弃）。

    以二进制方式逐行读取：UTF-8 解码失败或 JSON 解析失败的行都进入
    bad_lines（保留该行原始字节、仅去除行结束符），由迁移引擎写入字节级
    sidecar；逐字节还原请使用迁移产出的 <原始文件>.original 完整副本；
    非 UTF-8 文件不会整体崩溃，只会逐行进入坏行清单。
    """
    messages: List[Dict[str, Any]] = []
    warnings: List[str] = []
    bad_lines: List[Tuple[int, bytes]] = []
    with path.open("rb") as f:
        for lineno, raw_line in enumerate(f, 1):
            if lineno > limits.max_chat_lines:
                raise AdapterError(
                    f"聊天文件超过行数上限 {limits.max_chat_lines}: {path}"
                )
            # 只剥行结束符（\r\n 或 \n），保留行内空白——坏行索引要求字节级忠实（0.1.3）
            line = raw_line.rstrip(b"\r\n")
            stripped = line.strip()
            if not stripped:
                continue
            try:
                text = stripped.decode("utf-8")
            except UnicodeDecodeError as exc:
                warnings.append(f"第 {lineno} 行不是 UTF-8 文本，未迁移: {exc}")
                bad_lines.append((lineno, line))
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                warnings.append(f"第 {lineno} 行不是合法 JSON，未迁移: {exc}")
                bad_lines.append((lineno, line))
                continue
            if not isinstance(obj, dict):
                warnings.append(f"第 {lineno} 行不是 JSON 对象，未迁移")
                bad_lines.append((lineno, line))
                continue
            messages.append(obj)
    return ParsedChat(messages=messages, warnings=warnings, bad_lines=bad_lines)


def serialize_chat(chat: ParsedChat) -> str:
    """把解析后的消息序列化为 JSONL（保留原始键与顺序）。"""
    return "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in chat.messages)


def looks_like_world_info(obj: Any) -> bool:
    """结构特征判断：World Info / Lorebook 的最低可验证结构（规则 9：不猜字段）。"""
    return (
        isinstance(obj, dict)
        and isinstance(obj.get("entries"), dict)
        and isinstance(obj.get("character_book"), dict)
    )


@dataclass
class ParsedWorldInfo:
    entries: Dict[str, Any]
    raw: Dict[str, Any]


def parse_world_info(path: Path) -> ParsedWorldInfo:
    """只读解析 World Info / Lorebook JSON，原样保留所有字段。"""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not looks_like_world_info(raw):
        raise AdapterError(f"不是可识别的 World Info 结构（需含 entries 与 character_book）: {path}")
    return ParsedWorldInfo(entries=raw["entries"], raw=raw)
