"""W1：真实启动 Web UI 服务器并验证健康/版本/安全行为（不做任何 mock）。

服务器在 127.0.0.1 随机端口以真实线程运行（serve_forever），
客户端使用标准库 urllib/http.client 发送真实 HTTP 请求。
"""
from __future__ import annotations

import http.client
import json
import threading

import pytest

from continuity import __version__
from continuity.webui.server import WebUIServer


@pytest.fixture
def webui():
    server = WebUIServer(port=0)
    thread = threading.Thread(
        target=server.serve_forever, name="webui-test-server", daemon=True
    )
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=5)


def _raw(server, path, *, token=None, host=None):
    """http.client 原始请求：可精确控制 Host/路径（含穿越样式的原始字符串）。"""
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    headers = {}
    if host is not None:
        headers["Host"] = host
    if token is not None:
        headers["X-Continuity-Token"] = token
    conn.request("GET", path, headers=headers)
    resp = conn.getresponse()
    status = resp.status
    resp_headers = dict(resp.getheaders())
    body = resp.read()
    conn.close()
    return status, resp_headers, body


# —— 健康与版本 ——

def test_health_ok(webui):
    status, _, body = _raw(webui, "/api/health", token=webui.token)
    assert status == 200
    assert json.loads(body.decode("utf-8")) == {"status": "ok"}


def test_version_matches_tool(webui):
    status, _, body = _raw(webui, "/api/version", token=webui.token)
    assert status == 200
    payload = json.loads(body.decode("utf-8"))
    assert payload == {"tool": "continuity-studio", "version": __version__}


# —— 令牌 ——

def test_api_without_token_403(webui):
    status, _, body = _raw(webui, "/api/health")
    assert status == 403
    assert json.loads(body.decode("utf-8"))["kind"] == "TokenError"


def test_api_wrong_token_403(webui):
    status, _, body = _raw(webui, "/api/health", token="wrong-token")
    assert status == 403
    assert json.loads(body.decode("utf-8"))["kind"] == "TokenError"


# —— Host 白名单 ——

def test_host_whitelist_rejects_foreign_host(webui):
    status, _, body = _raw(webui, "/api/health", token=webui.token, host="evil.example")
    assert status == 400
    assert json.loads(body.decode("utf-8"))["kind"] == "SecurityError"


def test_host_whitelist_rejects_other_loopback_forms(webui):
    for host in ("127.0.0.2", "localhost.evil", "[::1]:8765"):
        status, _, _ = _raw(webui, "/", host=host)
        assert status == 400, host


def test_host_whitelist_allows_localhost(webui):
    status, _, body = _raw(
        webui, "/api/health", token=webui.token, host=f"localhost:{webui.port}"
    )
    assert status == 200
    assert json.loads(body.decode("utf-8")) == {"status": "ok"}


# —— 首页与安全头 ——

def test_index_served_with_token_and_csp(webui):
    status, headers, body = _raw(webui, "/")
    assert status == 200
    assert headers.get("Content-Type", "").startswith("text/html")
    assert "Content-Security-Policy" in headers
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert webui.token.encode("ascii") in body
    assert b"__CONTINUITY_TOKEN__" not in body  # 占位符已被真实令牌替换
    assert "概览".encode("utf-8") in body


# —— 静态资源 ——

def test_static_css_served(webui):
    status, headers, body = _raw(webui, "/static/style.css")
    assert status == 200
    assert headers.get("Content-Type", "").startswith("text/css")
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert body.startswith(b"/*")


def test_static_missing_404(webui):
    status, _, body = _raw(webui, "/static/nope.js")
    assert status == 404
    assert json.loads(body.decode("utf-8"))["kind"] == "NotFound"


@pytest.mark.parametrize(
    "path",
    [
        "/static/../server.py",
        "/static/..%2F..%2Fserver.py",
        "/static/%2e%2e%2f%2e%2e%2fserver.py",
        "/static/sub/../app.js",
    ],
)
def test_static_traversal_rejected(webui, path):
    status, _, body = _raw(webui, path)
    assert status == 404
    assert json.loads(body.decode("utf-8"))["kind"] == "NotFound"


def test_static_index_not_bypassable(webui):
    # 直接请求静态 index.html 不得泄露未注入令牌的原始页面
    status, _, body = _raw(webui, "/static/index.html")
    assert status == 404
    assert b"__CONTINUITY_TOKEN__" not in body


# —— 未知路径 ——

def test_unknown_api_404(webui):
    status, _, body = _raw(webui, "/api/nope", token=webui.token)
    assert status == 404
    assert json.loads(body.decode("utf-8"))["kind"] == "NotFound"


def test_unknown_page_404(webui):
    status, _, body = _raw(webui, "/nope")
    assert status == 404
    assert json.loads(body.decode("utf-8"))["kind"] == "NotFound"
