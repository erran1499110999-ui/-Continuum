"""生成合成样本数据（不含任何真实用户数据），供扫描器/适配器开发与回归测试使用。

用法：python samples/synthetic/make_samples.py [输出目录]
默认输出到 samples/synthetic/out/（已加入 .gitignore）。
"""

from __future__ import annotations

import base64
import json
import struct
import sys
import zlib
from pathlib import Path

CARD = {
    "spec": "chara_card_v2",
    "spec_version": "2.0",
    "data": {
        "name": "合成样本·测试角色",
        "description": "仅用于格式识别与解析测试的合成角色卡。",
        "personality": "谨慎、友好",
        "first_mes": "你好，我是合成样本角色。",
        "alternate_greetings": ["又见面了。"],
        "tags": ["synthetic", "test"],
        "creator_notes": "合成数据",
    },
}

CHAT_LINES = [
    {
        "name": "合成样本·测试角色",
        "is_user": False,
        "mes": "你好，我是合成样本角色。",
        "send_date": 1767697200000,
    },
    {"name": "用户", "is_user": True, "mes": "你好，测试一下。", "send_date": 1767697201000},
    {"name": "合成样本·测试角色", "is_user": False, "mes": "收到。", "send_date": 1767697202000},
]

# 世界书最小结构（entries + character_book 双字段是识别依据，见 looks_like_world_info）
WORLD_INFO = {
    "entries": {"0": {"keys": ["测试关键词"], "content": "合成世界观条目"}},
    "character_book": {},
}


def png_chunk(ctype: bytes, data: bytes) -> bytes:
    """构造单个 PNG 块：长度 + 类型 + 数据 + CRC（规范 ISO/IEC 15948）。"""
    body = ctype + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def make_card_png(card: dict) -> bytes:
    """把角色卡 JSON 嵌入 PNG tEXt chara 块（base64），生成 1×1 合法卡图。"""
    payload = base64.b64encode(json.dumps(card, ensure_ascii=False).encode("utf-8"))
    # 1x1、8bit、真彩色 IHDR；IDAT 为单像素红色（filter 0 + RGB）
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xff\x00\x00")
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", ihdr),
            png_chunk(b"tEXt", b"chara\x00" + payload),
            png_chunk(b"IDAT", idat),
            png_chunk(b"IEND", b""),
        ]
    )


def main() -> int:
    # 覆盖四类识别场景：合法卡（JSON/PNG）、聊天、世界书、两类损坏样本
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "out"
    out.mkdir(parents=True, exist_ok=True)
    (out / "st_card.json").write_text(
        json.dumps(CARD, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "st_card.png").write_bytes(make_card_png(CARD))
    (out / "st_chat.jsonl").write_text(
        "".join(json.dumps(line, ensure_ascii=False) + "\n" for line in CHAT_LINES),
        encoding="utf-8",
    )
    (out / "st_worldinfo.json").write_text(
        json.dumps(WORLD_INFO, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "broken_trailing_comma.json").write_text('{\n  "name": "坏样本",\n}\n', encoding="utf-8")
    (out / "unknown.bin").write_bytes(bytes(range(256)) * 4)
    print(f"合成样本已生成到: {out}")
    for p in sorted(out.iterdir()):
        print(f"  {p.name} ({p.stat().st_size} 字节)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
