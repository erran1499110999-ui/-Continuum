"""PNG 工具测试：流式读取与内存读取等价、截断/CRC 检出、元数据上限。"""

from continuity.pngutil import read_png_info, read_png_info_stream

from helpers import corrupt_idat, make_card_png, make_png


def test_stream_detects_bad_idat_crc(tmp_path):
    """第三轮审查 P1：只破坏 IDAT CRC，流式读取必须检出且不得报告完整。"""
    p = tmp_path / "idat.png"
    p.write_bytes(corrupt_idat(make_card_png()))
    info = read_png_info_stream(p)
    assert any("IDAT" in e for e in info.errors)
    assert not info.complete


def test_stream_equals_buffer_for_card(tmp_path):
    p = tmp_path / "card.png"
    p.write_bytes(make_card_png())
    buf = read_png_info(p.read_bytes())
    stream = read_png_info_stream(p)
    assert stream.text_chunks == buf.text_chunks
    assert "chara" in stream.text_chunks
    assert stream.complete is True
    assert stream.errors == []


def test_stream_detects_truncation(tmp_path):
    p = tmp_path / "bad.png"
    p.write_bytes(make_png([("chara", b"abc")])[:40])
    info = read_png_info_stream(p)
    assert info.errors  # 截断被检出，绝不当作正常 PNG


def test_stream_detects_bad_crc_in_ihdr(tmp_path):
    p = tmp_path / "crc.png"
    data = bytearray(make_png([("chara", b"abc")]))
    data[16] ^= 0xFF  # 破坏 IHDR 数据 → CRC 校验失败
    p.write_bytes(bytes(data))
    info = read_png_info_stream(p)
    assert any("CRC" in e for e in info.errors)
    assert not info.complete


def test_stream_metadata_cap(tmp_path):
    p = tmp_path / "big.png"
    p.write_bytes(make_png([("chara", b"x" * 2000)]))
    info = read_png_info_stream(p, max_metadata_bytes=100)
    assert any("上限" in e for e in info.errors)
    assert "chara" not in info.text_chunks


def test_stream_large_idat_crc_verified(tmp_path):
    """大 IDAT 也经固定缓冲区增量 CRC 校验（不整块载入内存）。"""
    from helpers import png_chunk

    p = tmp_path / "photo.png"
    ihdr = make_png()[:33]  # 签名 + IHDR
    parts = [ihdr, png_chunk(b"IDAT", b"\x00\x00\x00\x00" * 2000)]
    p.write_bytes(parts[0] + parts[1])
    info = read_png_info_stream(p, max_metadata_bytes=100)
    # 无 IEND → 不完整；大 IDAT 通过 CRC 校验且不触发元数据上限错误
    assert info.complete is False
    assert not any("上限" in e for e in info.errors)
    assert not any("IDAT" in e for e in info.errors)
