"""API 入参校验（W1）：纯函数，供 server/api 使用，后续阶段端点复用。

原则：校验只做「形状与安全」检查（必填、非法字符、目录关系、Host 白名单、
请求体解析），业务语义（manifest 校验、哈希校验等）一律交给核心引擎，
绝不重复实现或猜测（AGENTS.md 规则 9）。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_BODY_BYTES = 64 * 1024  # API 请求体上限（路径等参数远小于此值）

_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost"})


class ValidationError(ValueError):
    """入参校验失败，信息面向用户。"""


def require_path(value: Any, *, name: str = "路径") -> str:
    """路径参数必须是非空字符串，且不含控制字符（含 NUL）。"""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name}不能为空")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValidationError(f"{name}包含非法控制字符")
    return value


def require_source_dir(value: Any) -> Path:
    """源目录必须存在且为目录（只读输入，校验阶段不写任何内容）。"""
    raw = require_path(value, name="源目录")
    path = Path(raw).resolve()
    if not path.is_dir():
        raise ValidationError(f"源目录不存在: {path}")
    return path


def require_new_output_dir(value: Any, *, source: Any = None) -> Path:
    """输出目录必须不存在；若给出源目录，输出还不得位于源目录之内。

    与核心引擎（backup/repair/migration）的「输出必须为新目录、
    不得嵌套于源目录」规则保持一致，作为引擎之外的 UI 层预检。
    """
    raw = require_path(value, name="输出目录")
    # resolve() 对不存在的路径也适用（strict=False 默认），
    # 因此「输出目录不存在」与「嵌套于源目录」两项预检都基于解析后的绝对路径判断
    path = Path(raw).resolve()
    if path.exists():
        raise ValidationError(f"输出目录已存在，请选择新目录: {path}")
    if source is not None:
        src = Path(require_path(source, name="源目录")).resolve()
        if path == src or path.is_relative_to(src):
            raise ValidationError(f"输出目录不能位于源目录之内: {path}")
    return path


def host_is_allowed(host_header: str) -> bool:
    """Host 头白名单：仅接受 127.0.0.1 与 localhost（任意端口），防 DNS rebinding。

    解析细节：rsplit 一次去掉最右侧端口（"localhost:8765" → "localhost"）；
    含多个冒号的畸形主机名剥端口后仍不在白名单，自然被拒。
    """
    if not host_header:
        return False
    host = host_header.strip()
    if host.startswith("["):  # IPv6 字面量：本服务器只绑定 IPv4 回环，一律拒绝
        return False
    if ":" in host:
        host = host.rsplit(":", 1)[0]
    return host.lower() in _ALLOWED_HOSTS


def parse_json_body(data: bytes, *, max_bytes: int = MAX_BODY_BYTES) -> dict:
    """把请求体解析为 JSON 对象；超限/非法/非对象一律 ValidationError。"""
    if not isinstance(data, (bytes, bytearray)) or not data:
        raise ValidationError("请求体为空")
    if len(data) > max_bytes:
        raise ValidationError(f"请求体超过上限 {max_bytes} 字节")
    try:
        obj = json.loads(bytes(data).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"请求体不是合法 JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValidationError("请求体必须是 JSON 对象")
    return obj
