"""客户端适配器：核心数据模型与客户端格式分离（企划书 5.1）。

每个适配器只做只读解析、标准化导出与兼容性报告，不修改源文件。
首个适配器：SillyTavern。
"""

from .sillytavern import (
    AdapterError,
    ParsedCard,
    ParsedChat,
    ParsedWorldInfo,
    export_card_v2,
    looks_like_world_info,
    parse_card_dict,
    parse_card_file,
    parse_chat_jsonl,
    parse_world_info,
    serialize_chat,
)

__all__ = [
    "AdapterError",
    "ParsedCard",
    "ParsedChat",
    "ParsedWorldInfo",
    "export_card_v2",
    "looks_like_world_info",
    "parse_card_dict",
    "parse_card_file",
    "parse_chat_jsonl",
    "parse_world_info",
    "serialize_chat",
]
