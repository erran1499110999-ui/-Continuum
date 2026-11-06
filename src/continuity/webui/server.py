"""本地 Web UI 服务器（W1）：仅绑定 127.0.0.1，纯标准库实现。

安全设计（见 docs/webui-plan.md 第 5 节）：
- 仅绑定 127.0.0.1，不提供监听其他地址的选项；
- 每次启动生成随机访问令牌（X-Continuity-Token 头），/api/* 一律校验；
- Host 头白名单（127.0.0.1 / localhost）防 DNS rebinding；
- 静态资源仅限包内 static/ 目录（resolve 后二次校验），无任何「读任意文件」端点；
- 所有响应带 nosniff/禁嵌入/CSP，前端渲染只用 textContent（见 static/app.js）。
"""
from __future__ import annotations

import logging
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from .. import __version__
from . import api as api_module
from .validation import host_is_allowed
from .views import json_bytes

logger = logging.getLogger("continuity.webui")

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_PATH = STATIC_DIR / "index.html"
TOKEN_HEADER = "X-Continuity-Token"
_TOKEN_PLACEHOLDER = b"__CONTINUITY_TOKEN__"

_MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
}

# default-src 'none' + 逐项放行：无内联脚本/样式、无外源、禁嵌入、禁表单外发
_CSP = (
    "default-src 'none'; "
    "connect-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self'; "
    "script-src 'self'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'"
)


class WebUIServer:
    """本地 Web UI 服务器：threading HTTP 服务 + 随机访问令牌。"""

    def __init__(
        self,
        port: int = 8765,
        *,
        token: Optional[str] = None,
        static_dir: Optional[Path] = None,
    ) -> None:
        self.token = token or secrets.token_urlsafe(32)
        self.static_dir = (static_dir or STATIC_DIR).resolve()
        self.index_bytes = (self.static_dir / "index.html").read_bytes()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
        self.httpd.daemon_threads = True
        self.httpd.webui = self  # type: ignore[attr-defined]  处理器经此访问配置

    @property
    def port(self) -> int:
        return int(self.httpd.server_address[1])

    def serve_forever(self) -> None:
        logger.info(
            "本地 Web UI 已启动: http://127.0.0.1:%d（仅本机可访问，不上传任何数据）",
            self.port,
        )
        self.httpd.serve_forever()

    def shutdown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


class _Handler(BaseHTTPRequestHandler):
    """请求处理器：安全头 + Host 白名单 + 静态/API 分发。"""

    server_version = "ContinuityStudioW1/0.1"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:  # 静默访问日志（调试级）
        logger.debug("%s %s", self.address_string(), fmt % args)

    # —— 请求入口 ——

    def do_GET(self) -> None:  # noqa: N802 — BaseHTTPRequestHandler 命名约定
        self._route()

    def do_POST(self) -> None:  # noqa: N802
        self._route()

    def _route(self) -> None:
        try:
            if not host_is_allowed(self.headers.get("Host", "")):
                self._send_json(
                    400,
                    {
                        "error": "仅允许通过 127.0.0.1 或 localhost 访问本服务",
                        "kind": "SecurityError",
                    },
                )
                return
            path = urlsplit(self.path).path
            if path == "/":
                self._serve_index()
            elif path.startswith("/static/"):
                self._serve_static(path[len("/static/"):])
            elif path.startswith("/api/"):
                self._serve_api(path)
            else:
                self._send_json(404, {"error": "未找到该页面或接口", "kind": "NotFound"})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # 客户端提前断开：静默结束
        except Exception:
            logger.exception("请求处理失败")
            try:
                self._send_json(500, {"error": "服务器内部错误", "kind": "InternalError"})
            except Exception:
                pass

    # —— 响应构建 ——

    def _send_bytes(self, status: int, content_type: str, body: bytes, *, csp: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        if csp:
            self.send_header("Content-Security-Policy", _CSP)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _send_json(self, status: int, payload: dict) -> None:
        self._send_bytes(status, "application/json; charset=utf-8", json_bytes(payload))

    # —— 首页与静态资源 ——

    def _serve_index(self) -> None:
        body = self.server.webui.index_bytes.replace(
            _TOKEN_PLACEHOLDER, self.server.webui.token.encode("ascii")
        )
        self._send_bytes(200, "text/html; charset=utf-8", body, csp=True)

    def _serve_static(self, rel: str) -> None:
        # 静态文件全部平铺于 static/ 顶层：任何目录成分（/、\、..、%2F 变体）一律 404
        if (
            not rel
            or "/" in rel
            or "\\" in rel
            or rel.lower() == "index.html"  # 防止绕过 token 注入直读原始 index
        ):
            self._send_json(404, {"error": "未找到该资源", "kind": "NotFound"})
            return
        target = (self.server.webui.static_dir / rel).resolve()
        if not target.is_relative_to(self.server.webui.static_dir) or not target.is_file():
            self._send_json(404, {"error": "未找到该资源", "kind": "NotFound"})
            return
        mime = _MIME_TYPES.get(target.suffix.lower())
        if mime is None:
            self._send_json(404, {"error": "未找到该资源", "kind": "NotFound"})
            return
        try:
            body = target.read_bytes()
        except OSError:
            self._send_json(404, {"error": "未找到该资源", "kind": "NotFound"})
            return
        self._send_bytes(200, mime, body)

    # —— API ——

    def _token_ok(self) -> bool:
        header = self.headers.get(TOKEN_HEADER, "")
        try:
            return secrets.compare_digest(header, self.server.webui.token)
        except TypeError:  # 非 ASCII 令牌直接拒绝
            return False

    def _serve_api(self, path: str) -> None:
        if not self._token_ok():
            self._send_json(403, {"error": "缺少或错误的访问令牌", "kind": "TokenError"})
            return
        if path == "/api/health" and self.command == "GET":
            self._send_json(200, api_module.health())
            return
        if path == "/api/version" and self.command == "GET":
            self._send_json(200, api_module.version())
            return
        self._send_json(404, {"error": "未找到该接口", "kind": "NotFound"})
