"""PNG 结构读取工具（只读，标准库实现，不执行任何内容）。

0.1.1 起：校验块边界与 CRC，并把"未完整读取/校验失败"与"普通 PNG"区分开，
避免把损坏/截断文件误判为"无角色卡元数据的普通图片"。
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass, field
from typing import Dict, List

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

_CRC_CHUNK = 1024 * 1024  # IDAT 增量 CRC 的缓冲区大小


@dataclass
class PngInfo:
    text_chunks: Dict[str, bytes] = field(default_factory=dict)
    complete: bool = False  # 读到 IEND 且全程无错误
    errors: List[str] = field(default_factory=list)


def read_png_info(data: bytes) -> PngInfo:
    """解析 PNG 块结构：返回 tEXt 块内容、完整性标记与错误列表（只解析，不执行）。"""
    info = PngInfo()
    if not data.startswith(PNG_MAGIC):
        info.errors.append("缺少 PNG 魔数")
        return info
    pos = 8
    while True:
        if pos + 8 > len(data):
            info.errors.append("文件在块头处截断")
            break
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        ctype = data[pos + 4 : pos + 8]
        end = pos + 12 + length
        if end > len(data):
            info.errors.append(f"块 {ctype!r} 长度越界（文件截断）")
            break
        cdata = data[pos + 8 : pos + 8 + length]
        (crc,) = struct.unpack(">I", data[pos + 8 + length : end])
        expected = zlib.crc32(ctype + cdata) & 0xFFFFFFFF
        if crc != expected:
            info.errors.append(f"块 {ctype!r} CRC 校验失败")
        if ctype == b"tEXt" and crc == expected:
            keyword, _, text = cdata.partition(b"\x00")
            info.text_chunks[keyword.decode("latin-1", errors="replace")] = text
        if ctype == b"IEND":
            info.complete = not info.errors
            break
        pos = end
    return info


def read_png_info_stream(
    path,
    *,
    max_metadata_bytes: int = 1 * 1024 * 1024,
    max_chunk_bytes: int = 64 * 1024 * 1024,
    max_chunks: int = 10_000,
) -> PngInfo:
    """流式解析 PNG 块结构（逐块读取，不全量载入内存）。

    所有块（含图像数据块 IDAT）都做 CRC 校验：IDAT 以固定大小缓冲区
    增量计算 CRC，其余块逐块读取；complete 只在全部校验通过且读到 IEND
    时才为 True。非 IDAT 块长度受 max_metadata_bytes 约束。
    """
    info = PngInfo()
    with path.open("rb") as f:
        if f.read(8) != PNG_MAGIC:
            info.errors.append("缺少 PNG 魔数")
            return info
        for _ in range(max_chunks):
            header = f.read(8)
            if len(header) < 8:
                info.errors.append("文件在块头处截断")
                break
            (length,) = struct.unpack(">I", header[:4])
            ctype = header[4:8]
            if ctype == b"IDAT":
                if length > max_chunk_bytes:
                    info.errors.append(f"图像数据块长度超过上限 {max_chunk_bytes}")
                    break
                # 固定缓冲区增量 CRC（覆盖类型字节 + 数据），不整块载入内存
                crc = zlib.crc32(ctype)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(remaining, _CRC_CHUNK))
                    if not chunk:
                        info.errors.append("文件在图像数据处截断")
                        remaining = -1
                        break
                    crc = zlib.crc32(chunk, crc)
                    remaining -= len(chunk)
                if remaining < 0:
                    break
                crc_bytes = f.read(4)
                if len(crc_bytes) < 4:
                    info.errors.append("文件在图像数据 CRC 处截断")
                    break
                (stored_crc,) = struct.unpack(">I", crc_bytes)
                if (crc & 0xFFFFFFFF) != stored_crc:
                    info.errors.append("块 b'IDAT' CRC 校验失败")
                continue
            if length > max_metadata_bytes:
                info.errors.append(f"块 {ctype!r} 长度超过上限 {max_metadata_bytes}")
                break
            cdata = f.read(length)
            crc_bytes = f.read(4)
            if len(cdata) < length or len(crc_bytes) < 4:
                info.errors.append("文件在块数据处截断")
                break
            (crc,) = struct.unpack(">I", crc_bytes)
            expected = zlib.crc32(ctype + cdata) & 0xFFFFFFFF
            if crc != expected:
                info.errors.append(f"块 {ctype!r} CRC 校验失败")
                continue
            if ctype == b"tEXt":
                keyword, _, text = cdata.partition(b"\x00")
                info.text_chunks[keyword.decode("latin-1", errors="replace")] = text
            if ctype == b"IEND":
                info.complete = not info.errors
                break
        else:
            info.errors.append(f"块数量超过上限 {max_chunks}")
    return info


def read_png_text_chunks(data: bytes) -> Dict[str, bytes]:
    """兼容接口：仅返回 tEXt 块；新代码请使用 read_png_info 以获取损坏信息。"""
    return read_png_info(data).text_chunks
