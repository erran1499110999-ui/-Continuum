"""统一数据模型与基础枚举（企划书 5.3 / 5.4）。

技术栈：Pydantic v2（解析、验证、数据模型）。
所有持久化 JSON 通过 model_dump / model_validate 读写。
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


def utc_now_iso() -> str:
    """UTC 时间 ISO 8601 字符串。"""
    return datetime.now(timezone.utc).isoformat()


class ManifestError(ValueError):
    """清单读取/校验错误，信息面向用户。"""


class RepairLevel(str, enum.Enum):
    """修复等级（企划书 5.4）。"""

    R0 = "r0"  # 确定性修复：依据明确规则，可自动生成修复副本
    R1 = "r1"  # 可推断修复：有证据但不唯一，必须用户确认
    R2 = "r2"  # 人工处理：缺失内容无可靠来源，只给建议
    R3 = "r3"  # 不安全/不支持：隔离，不执行


class Severity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class FileKind(str, enum.Enum):
    """可识别文件类型。仅依据可验证的结构特征判断，不做字段猜测。"""

    CHARACTER_CARD_JSON = "character_card_json"
    CHARACTER_CARD_PNG = "character_card_png"
    CHAT_JSONL = "chat_jsonl"
    JSON = "json"  # 合法 JSON，但类型未确定
    PNG = "png"  # 合法 PNG，未发现角色卡元数据
    CORRUPT_PNG = "corrupt_png"  # PNG 结构损坏/截断/CRC 失败
    TEXT = "text"
    BINARY = "binary"
    UNKNOWN = "unknown"


class ScanFinding(BaseModel):
    """一次扫描/诊断发现（对应提示词 5 的字段要求）。"""

    file: str
    location: str = "-"
    problem: str
    evidence: str
    suggestion: str
    severity: Severity = Severity.WARNING
    repair_level: Optional[RepairLevel] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ManifestEntry(BaseModel):
    """备份包中的单个文件记录。"""

    rel_path: str = Field(min_length=1)
    size: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    kind: str = "unknown"
    warnings: List[str] = Field(default_factory=list)

    @field_validator("rel_path")
    @classmethod
    def _validate_rel_path(cls, v: str) -> str:
        """要求唯一、规范的 POSIX 相对路径：拒绝空段、.、..、绝对路径、盘符、反斜杠与首尾空白。"""
        if v != v.strip() or v.endswith("/") or v.startswith("/") or "\\" in v:
            raise ValueError(f"非规范的相对路径: {v!r}")
        parts = v.split("/")
        if any(p in ("", ".", "..") for p in parts):
            raise ValueError(f"非规范的相对路径: {v!r}")
        if ":" in parts[0]:
            raise ValueError(f"相对路径含盘符: {v!r}")
        return v


class BundleManifest(BaseModel):
    """备份包清单（企划书 5.1 / 提示词 4 的 manifest schema）。"""

    SCHEMA_VERSION: ClassVar[str] = "1.0"

    bundle_id: str = Field(min_length=1)
    bundle_version: str = "1.0"
    created_at: str
    schema_version: str = SCHEMA_VERSION
    source_client: Optional[str] = None
    source_client_version: Optional[str] = None
    tool_name: str = "continuity-studio"
    tool_version: str = ""
    entries: List[ManifestEntry] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> "BundleManifest":
        if self.schema_version != self.SCHEMA_VERSION:
            raise ValueError(
                f"不支持的清单 schema 版本: {self.schema_version!r}"
                f"（本工具支持 {self.SCHEMA_VERSION}）"
            )
        rels = [e.rel_path for e in self.entries]
        if len(rels) != len(set(rels)):
            raise ValueError("清单中存在重复的 rel_path")
        return self


class CharacterBundle(BaseModel):
    """统一角色包（企划书 5.3 概念模型）。

    当前阶段只承载清单与结构占位；迁移适配器完成后才填充
    character / conversations / memory / assets 等字段。
    runtime_config 绝不保存密钥。
    """

    bundle_id: str = Field(min_length=1)
    bundle_version: str = "1.0"
    created_at: str = Field(default_factory=utc_now_iso)
    source_client: Optional[str] = None
    source_client_version: Optional[str] = None
    character: Dict[str, Any] = Field(default_factory=dict)
    conversations: List[Dict[str, Any]] = Field(default_factory=list)
    memory: List[Dict[str, Any]] = Field(default_factory=list)
    assets: List[Dict[str, Any]] = Field(default_factory=list)
    runtime_config: Dict[str, Any] = Field(default_factory=dict)
    manifest: Optional[BundleManifest] = None
    warnings: List[str] = Field(default_factory=list)
