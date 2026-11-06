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
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from .. import __version__
from . import api as api_module
from .jobs import JobManager, JobQueueFullError
from .validation import MAX_BODY_BYTES, ValidationError, host_is_allowed, parse_json_body, require_source_dir
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


class _QuietThreadingHTTPServer(ThreadingHTTPServer):
    """网络级连接错误（客户端粗暴断连等）静默为 debug 日志。

    默认实现的 handle_error 会把完整 traceback 打印到 stderr——攻击者可通过
    反复 RST 刷屏日志；此处只记一条 debug 级摘要。
    """

    def handle_error(self, request, client_address) -> None:
        logger.debug("连接级错误（已静默） %s: %r", client_address, sys.exc_info()[1])


class WebUIServer:
    """本地 Web UI 服务器：threading HTTP 服务 + 随机访问令牌。"""

    def __init__(
        self,
        port: int = 8777,  # 默认端口（创始人裁决：原 8765 被百度输入法常驻占用）
        *,
        token: Optional[str] = None,
        static_dir: Optional[Path] = None,
        connection_timeout: float = 30.0,  # 空闲/慢连接超时（slowloris 防护）
    ) -> None:
        self.token = token or secrets.token_urlsafe(32)
        self.static_dir = (static_dir or STATIC_DIR).resolve()
        self.index_bytes = (self.static_dir / "index.html").read_bytes()
        self.connection_timeout = connection_timeout
        self.jobs = JobManager()  # 后台任务队列（W2 起：scan 等长任务串行执行）
        self.httpd = _QuietThreadingHTTPServer(("127.0.0.1", port), _Handler)
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
        self._serving = True
        self.httpd.serve_forever()

    def shutdown(self) -> None:
        # 仅当 serve_forever 真的在跑时才需要 shutdown() 解锁其循环；
        # 从未启动过服务时调用 shutdown() 会永久阻塞，必须跳过。
        if getattr(self, "_serving", False):
            self.httpd.shutdown()
        self.jobs.stop(timeout=5.0)  # 先停接客再收任务线程，保证任务完整收口
        self.httpd.server_close()


class _Handler(BaseHTTPRequestHandler):
    """请求处理器：安全头 + Host 白名单 + 静态/API 分发。"""

    server_version = "ContinuityStudioW1/0.1"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:  # 静默访问日志（调试级）
        logger.debug("%s %s", self.address_string(), fmt % args)

    def setup(self) -> None:  # noqa: N802 — socketserver 生命周期方法
        super().setup()
        # slowloris 防护：读超时后 readline 抛 TimeoutError，
        # BaseHTTPRequestHandler.handle_one_request 会关闭该连接并释放线程。
        self.connection.settimeout(self.server.webui.connection_timeout)

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
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, TimeoutError):
            pass  # 客户端断开或读超时：静默结束，不污染日志
        except Exception as exc:
            logger.error("请求处理失败（已响应 500）: %r", exc)
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

    def _read_body(self) -> bytes:
        """按 Content-Length 读取请求体（上限 MAX_BODY_BYTES，防超大请求）。"""
        raw = self.headers.get("Content-Length", "")
        try:
            length = int(raw)
        except ValueError:
            raise ValidationError("Content-Length 缺失或非法") from None
        if length < 0:
            raise ValidationError("Content-Length 非法")
        if length > MAX_BODY_BYTES:
            # 响应后立即断开：未读的超限请求体绝不能污染下一条请求的解析
            self.close_connection = True
            raise ValidationError(f"请求体超过上限 {MAX_BODY_BYTES} 字节")
        data = self.rfile.read(length)
        return data

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
        if path == "/api/jobs/scan" and self.command == "POST":
            self._handle_scan()
            return
        if path.startswith("/api/jobs/") and self.command == "GET":
            self._handle_job_status(path[len("/api/jobs/"):])
            return
        self._send_json(404, {"error": "未找到该接口", "kind": "NotFound"})

    # —— job 端点（W2：scan）——

    def _handle_scan(self) -> None:
        try:
            body = parse_json_body(self._read_body())
            source = require_source_dir(body.get("source"))
        except ValidationError as exc:
            self._send_json(400, {"error": str(exc), "kind": "ValidationError"})
            return
        try:
            job_id = self.server.webui.jobs.submit(
                lambda: api_module.scan_worker(str(source), log=self.server.webui.jobs.log)
            )
        except JobQueueFullError as exc:
            # 串行任务忙碌：按计划返回 409 提示等待（不再无限排队）
            self._send_json(409, {"error": str(exc), "kind": "JobsBusy"})
            return
        except RuntimeError as exc:  # 队列已停止
            self._send_json(503, {"error": str(exc), "kind": "JobsError"})
            return
        self._send_json(202, {"job_id": job_id})

    def _handle_job_status(self, job_id: str) -> None:
        snap = self.server.webui.jobs.get(job_id)
        if snap is None:
            self._send_json(404, {"error": "未找到该任务", "kind": "NotFound"})
            return
        self._send_json(200, snap)
