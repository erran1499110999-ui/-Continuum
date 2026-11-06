"""文件类型识别测试（仅依据可验证的结构特征）。"""

import json

from continuity.models import FileKind
from continuity.scanners.filetype import identify_file

from helpers import make_card_png, make_png


def test_card_png(tmp_path):
    p = tmp_path / "card.png"
    p.write_bytes(make_card_png())
    assert identify_file(p) is FileKind.CHARACTER_CARD_PNG


def test_plain_png(tmp_path):
    p = tmp_path / "img.png"
    p.write_bytes(make_png())
    assert identify_file(p) is FileKind.PNG


def test_truncated_png_is_corrupt(tmp_path):
    p = tmp_path / "bad.png"
    data = make_png([("chara", b"abc")])
    p.write_bytes(data[:40])  # 在 tEXt 块完整写入前截断
    assert identify_file(p) is FileKind.CORRUPT_PNG


def test_corrupt_png_bad_crc(tmp_path):
    p = tmp_path / "crc.png"
    data = bytearray(make_png([("chara", b"abc")]))
    data[16] ^= 0xFF  # 破坏 IHDR 数据 → CRC 校验失败
    p.write_bytes(bytes(data))
    assert identify_file(p) is FileKind.CORRUPT_PNG


def test_card_json(tmp_path):
    p = tmp_path / "card.json"
    p.write_text(json.dumps({"name": "n", "first_mes": "hi"}), encoding="utf-8")
    assert identify_file(p) is FileKind.CHARACTER_CARD_JSON


def test_v2_card_json(tmp_path):
    p = tmp_path / "card.json"
    p.write_text(
        json.dumps({"spec": "chara_card_v2", "data": {"name": "n"}}), encoding="utf-8"
    )
    assert identify_file(p) is FileKind.CHARACTER_CARD_JSON


def test_plain_json(tmp_path):
    p = tmp_path / "conf.json"
    p.write_text(json.dumps({"foo": 1}), encoding="utf-8")
    assert identify_file(p) is FileKind.JSON


def test_chat_jsonl(tmp_path):
    p = tmp_path / "chat.jsonl"
    p.write_text("\n".join(json.dumps({"i": i}) for i in range(3)) + "\n", encoding="utf-8")
    assert identify_file(p) is FileKind.CHAT_JSONL


def test_broken_json_is_text(tmp_path):
    p = tmp_path / "broken.json"
    p.write_text('{"name": "x",\n}', encoding="utf-8")  # 末尾多余逗号
    assert identify_file(p) is FileKind.TEXT


def test_binary(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(bytes(range(256)))
    assert identify_file(p) is FileKind.BINARY


def test_empty_file_is_text(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_bytes(b"")
    assert identify_file(p) is FileKind.TEXT
