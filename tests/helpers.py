"""测试与样本共用的合成数据构造工具（纯标准库，无第三方依赖）。"""

from __future__ import annotations

import base64
import json
import struct
import zlib
from typing import List, Optional, Tuple

CHARA_KEY = "chara"


def png_chunk(ctype: bytes, data: bytes) -> bytes:
    body = ctype + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def make_png(text_chunks: Optional[List[Tuple[str, bytes]]] = None) -> bytes:
    """构造合法的 1x1 PNG；text_chunks 为 (keyword, value) 列表（写入 tEXt 块）。"""
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)  # 1x1, 8bit, truecolor
    idat = zlib.compress(b"\x00\xff\x00\x00")  # filter 0 + RGB(255,0,0)
    parts = [b"\x89PNG\r\n\x1a\n", png_chunk(b"IHDR", ihdr)]
    for keyword, value in text_chunks or []:
        parts.append(png_chunk(b"tEXt", keyword.encode("latin-1") + b"\x00" + value))
    parts += [png_chunk(b"IDAT", idat), png_chunk(b"IEND", b"")]
    return b"".join(parts)


def make_card_png(card: Optional[dict] = None) -> bytes:
    """构造带 tEXt chara 块（base64 角色卡 JSON）的 PNG。"""
    card = card or {
        "spec": "chara_card_v2",
        "data": {"name": "测试角色", "first_mes": "你好。"},
    }
    payload = base64.b64encode(json.dumps(card, ensure_ascii=False).encode("utf-8"))
    return make_png([(CHARA_KEY, payload)])


def corrupt_idat(data: bytes) -> bytes:
    """破坏 PNG 图像数据块（IDAT）的首个数据字节 → IDAT CRC 校验失败。"""
    b = bytearray(data)
    pos = data.find(b"IDAT")
    assert pos > 0, "找不到 IDAT 块"
    b[pos + 4] ^= 0xFF
    return bytes(b)


ST_CARD_V2 = {
    "spec": "chara_card_v2",
    "spec_version": "2.0",
    "data": {
        "name": "合成样本·测试角色",
        "description": "仅用于迁移测试的合成角色卡。",
        "personality": "谨慎、友好",
        "scenario": "测试场景",
        "first_mes": "你好，我是合成样本角色。",
        "alternate_greetings": ["又见面了。"],
        "tags": ["synthetic", "test"],
        "creator": "synthetic",
        "creator_notes": "合成数据",
        "character_version": "1.0",
        "mes_example": "<START>\n示例对话",
        "unknown_custom_field": {"x": 1},
    },
}

ST_CHAT_LINES = [
    {
        "name": "合成样本·测试角色",
        "is_user": False,
        "mes": "你好。",
        "send_date": 1767697200000,
        "swipes": ["你好。", "嗨！"],
        "custom_flag": True,
    },
    {"name": "用户", "is_user": True, "mes": "测试。", "send_date": 1767697201000},
    {"name": "合成样本·测试角色", "is_user": False, "mes": "收到。", "send_date": 1767697202000},
]

ST_WORLD = {
    "entries": {
        "0": {
            "keys": ["测试关键词", "关键词2"],
            "content": "合成世界观条目",
            "comment": "合成",
            "insertion_order": 0,
        }
    },
    "character_book": {"name": "world1", "description": "合成世界书"},
}


def make_st_sample_tree(root: Path, with_json_card: bool = True) -> Path:
    """构造合成 SillyTavern 数据目录（角色卡、聊天、世界书、附件），不含真实用户数据。"""
    (root / "cards").mkdir(parents=True)
    (root / "chats").mkdir()
    (root / "worlds").mkdir()
    (root / "assets").mkdir()
    if with_json_card:
        (root / "cards" / "角色卡.json").write_text(
            json.dumps(ST_CARD_V2, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    (root / "cards" / "角色卡.png").write_bytes(make_card_png(ST_CARD_V2))
    (root / "chats" / "chat1.jsonl").write_text(
        "".join(json.dumps(line, ensure_ascii=False) + "\n" for line in ST_CHAT_LINES),
        encoding="utf-8",
    )
    (root / "worlds" / "world1.json").write_text(
        json.dumps(ST_WORLD, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (root / "assets" / "portrait.png").write_bytes(make_png())
    (root / "README.md").write_text("# 合成样本说明\n", encoding="utf-8")
    return root
