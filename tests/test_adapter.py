"""SillyTavern 适配器测试：角色卡（V1/V2、PNG/JSON）、聊天、世界书。"""

import base64
import json

import pytest

from continuity.adapters.sillytavern import (
    AdapterError,
    export_card_v2,
    parse_card_dict,
    parse_card_file,
    parse_chat_jsonl,
    parse_world_info,
    serialize_chat,
)
from continuity.models import FileKind

from helpers import ST_CARD_V2, ST_CHAT_LINES, ST_WORLD, make_card_png


def test_parse_v2_card_png(tmp_path):
    p = tmp_path / "card.png"
    p.write_bytes(make_card_png(ST_CARD_V2))
    card = parse_card_file(p, FileKind.CHARACTER_CARD_PNG)
    assert card.format_version == "v2"
    assert card.name == "合成样本·测试角色"
    assert card.first_mes == "你好，我是合成样本角色。"
    assert card.alternate_greetings == ["又见面了。"]
    assert card.tags == ["synthetic", "test"]
    assert "unknown_custom_field" in card.unknown_keys


def test_parse_v2_card_json(tmp_path):
    p = tmp_path / "card.json"
    p.write_text(json.dumps(ST_CARD_V2, ensure_ascii=False), encoding="utf-8")
    card = parse_card_file(p, FileKind.CHARACTER_CARD_JSON)
    assert card.format_version == "v2"
    assert card.name == "合成样本·测试角色"


def test_parse_v1_flat_card():
    v1 = {
        "name": "V1角色",
        "description": "平铺结构",
        "first_mes": "你好。",
        "custom_extra": "保留我",
    }
    card = parse_card_dict(v1)
    assert card.format_version == "v1"
    assert card.name == "V1角色"
    assert card.unknown_keys == ["custom_extra"]


def test_export_v2_roundtrip_preserves_unknown():
    src = parse_card_dict(json.loads(json.dumps(ST_CARD_V2)))
    exported = export_card_v2(src)
    assert exported["spec"] == "chara_card_v2"
    out = parse_card_dict(exported)
    assert out.name == src.name
    assert out.personality == src.personality
    assert out.alternate_greetings == src.alternate_greetings
    # 未知字段原样保留
    assert out.raw["data"]["unknown_custom_field"] == {"x": 1}


def test_chat_roundtrip(tmp_path):
    p = tmp_path / "chat.jsonl"
    p.write_text(
        "".join(json.dumps(line, ensure_ascii=False) + "\n" for line in ST_CHAT_LINES),
        encoding="utf-8",
    )
    parsed = parse_chat_jsonl(p)
    assert len(parsed.messages) == 3
    assert parsed.warnings == []
    serialized = serialize_chat(parsed)
    p2 = tmp_path / "chat2.jsonl"
    p2.write_text(serialized, encoding="utf-8")
    parsed2 = parse_chat_jsonl(p2)
    assert parsed2.messages == parsed.messages
    # 元数据与未知字段保留
    assert parsed2.messages[0]["send_date"] == 1767697200000
    assert parsed2.messages[0]["swipes"] == ["你好。", "嗨！"]
    assert parsed2.messages[0]["custom_flag"] is True


def test_chat_unparseable_line_warning(tmp_path):
    p = tmp_path / "chat.jsonl"
    p.write_text('{"is_user": true, "mes": "ok"}\n这不是JSON\n', encoding="utf-8")
    parsed = parse_chat_jsonl(p)
    assert len(parsed.messages) == 1
    assert len(parsed.warnings) == 1
    assert parsed.bad_lines == [(2, "这不是JSON".encode("utf-8"))]  # 原始坏行字节被保留


def test_chat_non_utf8_line_warning(tmp_path):
    p = tmp_path / "chat.jsonl"
    p.write_bytes(b'{"is_user": true, "mes": "ok"}\n' + b"\xff\xfe bad bytes\n")
    parsed = parse_chat_jsonl(p)
    assert len(parsed.messages) == 1
    assert len(parsed.warnings) == 1
    assert parsed.bad_lines == [(2, b"\xff\xfe bad bytes")]  # 非 UTF-8 不崩溃，逐行进坏行清单


def test_chat_bad_line_preserves_inner_spaces(tmp_path):
    """第三轮审查 P2：坏行索引保留行内/外围空白，仅去除行结束符。"""
    p = tmp_path / "chat.jsonl"
    p.write_bytes(b'{"ok": 1}\n  {bad json  \n')
    parsed = parse_chat_jsonl(p)
    assert parsed.bad_lines == [(2, b"  {bad json  ")]


def test_world_info(tmp_path):
    p = tmp_path / "world.json"
    p.write_text(json.dumps(ST_WORLD, ensure_ascii=False), encoding="utf-8")
    world = parse_world_info(p)
    assert len(world.entries) == 1
    assert world.entries["0"]["keys"] == ["测试关键词", "关键词2"]


def test_png_missing_chara_raises(tmp_path):
    from helpers import make_png

    p = tmp_path / "img.png"
    p.write_bytes(make_png())
    with pytest.raises(AdapterError, match="chara"):
        parse_card_file(p, FileKind.CHARACTER_CARD_PNG)


def test_png_bad_base64_raises(tmp_path):
    from helpers import make_png

    p = tmp_path / "bad.png"
    p.write_bytes(make_png([("chara", b"!!!not-base64!!!")]))
    with pytest.raises(AdapterError, match="解析失败"):
        parse_card_file(p, FileKind.CHARACTER_CARD_PNG)


def test_v2_missing_data_raises():
    with pytest.raises(AdapterError, match="data"):
        parse_card_dict({"spec": "chara_card_v2"})


def test_chat_line_limit_raises(tmp_path):
    from continuity.limits import ResourceLimits

    p = tmp_path / "chat.jsonl"
    p.write_text("".join(json.dumps({"i": i}) + "\n" for i in range(5)), encoding="utf-8")
    with pytest.raises(AdapterError, match="行数上限"):
        parse_chat_jsonl(p, limits=ResourceLimits(max_chat_lines=2))


def test_card_png_size_limit_raises(tmp_path):
    from continuity.limits import ResourceLimits

    p = tmp_path / "card.png"
    p.write_bytes(make_card_png(ST_CARD_V2))
    with pytest.raises(AdapterError, match="大小上限"):
        parse_card_file(
            p, FileKind.CHARACTER_CARD_PNG, limits=ResourceLimits(max_card_png_bytes=1)
        )
