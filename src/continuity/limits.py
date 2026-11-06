"""统一资源预算：所有命令共享的文件数、字节数与解析上限（企划书 5.5 资源耗尽防护）。

超限时命令应失败并给出明确报告，绝不输出貌似完整的结果。
"""

from __future__ import annotations

from dataclasses import dataclass

MIB = 1024 * 1024
GIB = 1024 ** 3


@dataclass(frozen=True)
class ResourceLimits:
    """全部命令共享的硬上限；超限即失败并给出明确报告，绝不输出貌似完整的结果。"""

    max_file_bytes: int = 256 * MIB  # 单文件上限
    max_total_bytes: int = 2 * GIB  # 累计字节上限
    max_files: int = 100_000  # 文件数上限
    max_depth: int = 32  # 目录深度上限
    max_json_bytes: int = 8 * MIB  # 文本类 JSON 解析上限
    max_chat_lines: int = 200_000  # 聊天 JSONL 行数上限
    max_card_png_bytes: int = 16 * MIB  # 角色卡 PNG 读取上限


DEFAULT_LIMITS = ResourceLimits()
