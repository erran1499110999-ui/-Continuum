"""P5：备份类端点真实运行测试——真实服务器 + 真实 HTTP + 真实引擎，无任何 mock。

覆盖：
- GET /api/ping：免 token 200、响应体仅 {"status":"ok"}（无版本指纹，Q12）、
  Host 白名单仍拦截伪造 Host；
- POST /api/jobs/backup：引擎等价比对、源零写入、来源客户端元数据、409 忙碌、错误路径；
- POST /api/jobs/emergency-backup：备份 + 可恢复性自检（verify 联动）；
- POST /api/jobs/restore：备份→恢复回环逐文件一致、目标已存在拒绝、坏备份包 failed 透传。
"""
from __future__ import annotations

import hashlib
import http.client
import json
import threading
import time

import pytest

from continuity.backup import create_backup
from continuity.webui.server import WebUIServer
from helpers import make_st_sample_tree

TERMINAL = frozenset({"succeeded", "failed"})


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


def _post(server, path, payload=None, *, token=None):
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["X-Continuity-Token"] = token
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    conn.request("POST", path, body=body, headers=headers)
    resp = conn.getresponse()
    status = resp.status
    raw = resp.read()
    conn.close()
    return status, json.loads(raw.decode("utf-8")) if raw else None


def _get(server, path, *, token=None, host=None):
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    headers = {}
    if token is not None:
        headers["X-Continuity-Token"] = token
    if host is not None:
        headers["Host"] = host
    conn.request("GET", path, headers=headers)
    resp = conn.getresponse()
    status = resp.status
    raw = resp.read()
    conn.close()
    return status, json.loads(raw.decode("utf-8")) if raw else None


def _wait_job(server, job_id, *, timeout=30.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status, snap = _get(server, f"/api/jobs/{job_id}", token=server.token)
        assert status == 200
        if snap["state"] in TERMINAL:
            return snap
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} 未在 {timeout}s 内结束")


def _run_job(server, path, payload):
    status, body = _post(server, path, payload, token=server.token)
    assert status == 202, body
    snap = _wait_job(server, body["job_id"])
    assert snap["state"] == "succeeded", snap
    return snap


def _snapshot_tree(root):
    """目录内容快照（相对路径 → SHA-256），用于源目录零写入断言。"""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


# —— /api/ping（Q12：免 token、无指纹、Host 白名单仍生效） ——

def test_ping_without_token_200(webui):
    status, payload = _get(webui, "/api/ping")
    assert status == 200
    # Q12：响应体只允许 {"status":"ok"}，不得携带版本号/工具名等指纹信息
    assert payload == {"status": "ok"}


def test_ping_response_has_no_fingerprint(webui):
    conn = http.client.HTTPConnection("127.0.0.1", webui.port, timeout=10)
    conn.request("GET", "/api/ping")
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    assert resp.status == 200
    for token in ("version", "continuity", "python", "tool", "0.1"):
        assert token not in raw.lower(), f"ping 响应含指纹信息: {token!r}"


def test_ping_host_whitelist_still_enforced(webui):
    status, _ = _get(webui, "/api/ping", host="evil.example")
    assert status == 400


# —— /api/jobs/backup ——

def test_backup_engine_equivalent(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    direct_bundle = tmp_path / "direct-bundle"
    direct = create_backup(tree, direct_bundle)

    snap = _run_job(webui, "/api/jobs/backup", {"source": str(tree), "bundle": str(tmp_path / "api-bundle")})

    result = snap["result"]
    # 引擎等价比对：条目（rel_path/size/sha256/kind）与警告必须一致
    assert result["manifest"]["entries"] == direct.model_dump(mode="json")["entries"]
    assert result["manifest"]["warnings"] == direct.warnings
    # 备份包产物真实存在
    assert (tmp_path / "api-bundle" / "manifest.json").is_file()
    assert (tmp_path / "api-bundle" / "files").is_dir()


def test_backup_source_zero_write(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    before = _snapshot_tree(tree)
    _run_job(webui, "/api/jobs/backup", {"source": str(tree), "bundle": str(tmp_path / "b")})
    assert _snapshot_tree(tree) == before


def test_backup_source_client_metadata(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    snap = _run_job(
        webui,
        "/api/jobs/backup",
        {
            "source": str(tree),
            "bundle": str(tmp_path / "b"),
            "source_client": "SillyTavern",
            "source_client_version": "1.19.0",
        },
    )
    manifest = snap["result"]["manifest"]
    assert manifest["source_client"] == "SillyTavern"
    assert manifest["source_client_version"] == "1.19.0"


def test_backup_second_submit_busy_409(webui, tmp_path):
    gate = threading.Event()
    webui.jobs.submit(lambda: gate.wait(timeout=5))
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and list(webui.jobs._jobs.values())[0].state != "running":
        time.sleep(0.01)
    tree = make_st_sample_tree(tmp_path / "stdata")
    status, payload = _post(
        webui, "/api/jobs/backup", {"source": str(tree), "bundle": str(tmp_path / "b")}, token=webui.token
    )
    gate.set()
    assert status == 409
    assert payload["kind"] == "JobsBusy"


@pytest.mark.parametrize(
    "payload,expect",
    [
        ({"bundle": "x"}, "源目录"),
        ({"source": "x"}, "源目录"),
        ({"source": "", "bundle": "x"}, "不能为空"),
        ({}, "不能为空"),
    ],
)
def test_backup_validation_errors(webui, tmp_path, payload, expect):
    payload = dict(payload)
    if "source" in payload and payload["source"] == "x":
        payload["source"] = str(tmp_path / "nope")
    if "bundle" in payload and payload["bundle"] == "x":
        payload["bundle"] = str(tmp_path / "b")
    status, body = _post(webui, "/api/jobs/backup", payload, token=webui.token)
    assert status == 400
    assert body["kind"] == "ValidationError"
    assert expect in body["error"]


def test_backup_bundle_exists_400(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    existing = tmp_path / "exists"
    existing.mkdir()
    status, body = _post(
        webui, "/api/jobs/backup", {"source": str(tree), "bundle": str(existing)}, token=webui.token
    )
    assert status == 400
    assert "已存在" in body["error"]


def test_backup_bundle_inside_source_400(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    status, body = _post(
        webui,
        "/api/jobs/backup",
        {"source": str(tree), "bundle": str(tree / "inner")},
        token=webui.token,
    )
    assert status == 400
    assert "不能位于源目录之内" in body["error"]


# —— /api/jobs/emergency-backup ——

def test_emergency_backup_with_selfcheck(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    snap = _run_job(
        webui,
        "/api/jobs/emergency-backup",
        {"source": str(tree), "output": str(tmp_path / "rescue")},
    )
    result = snap["result"]
    assert (tmp_path / "rescue" / "manifest.json").is_file()
    # 可恢复性自检：verify 联动结论必须 ok 且逐文件校验过
    assert result["verify"]["ok"] is True
    assert result["verify"]["checked"] == len(result["manifest"]["entries"])
    assert "可恢复性自检: 通过" in snap["log_tail"][-1]


def test_emergency_backup_output_exists_400(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    existing = tmp_path / "rescue"
    existing.mkdir()
    status, body = _post(
        webui,
        "/api/jobs/emergency-backup",
        {"source": str(tree), "output": str(existing)},
        token=webui.token,
    )
    assert status == 400
    assert "已存在" in body["error"]


# —— /api/jobs/restore ——

def test_restore_roundtrip_matches_source(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    before = _snapshot_tree(tree)
    bundle_dir = tmp_path / "bundle"
    _run_job(webui, "/api/jobs/backup", {"source": str(tree), "bundle": str(bundle_dir)})

    snap = _run_job(webui, "/api/jobs/restore", {"bundle": str(bundle_dir), "dest": str(tmp_path / "restored")})

    result = snap["result"]
    assert result["ok"] is True
    assert result["restored"] == len(before)
    # 回环保真：恢复产物逐文件哈希与源一致
    assert _snapshot_tree(tmp_path / "restored") == before


def test_restore_dest_exists_400(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    bundle_dir = tmp_path / "bundle"
    _run_job(webui, "/api/jobs/backup", {"source": str(tree), "bundle": str(bundle_dir)})
    existing = tmp_path / "dest"
    existing.mkdir()
    status, body = _post(
        webui, "/api/jobs/restore", {"bundle": str(bundle_dir), "dest": str(existing)}, token=webui.token
    )
    assert status == 400
    assert "已存在" in body["error"]


def test_restore_bundle_missing_400(webui, tmp_path):
    status, body = _post(
        webui,
        "/api/jobs/restore",
        {"bundle": str(tmp_path / "nope"), "dest": str(tmp_path / "dest")},
        token=webui.token,
    )
    assert status == 400
    assert "源目录不存在" in body["error"]


def test_restore_bad_bundle_job_failed(webui, tmp_path):
    """备份包缺 manifest 时由引擎报错 → job failed 透传用户文案（不伪造成功）。"""
    bad = tmp_path / "bad-bundle"
    (bad / "files").mkdir(parents=True)
    status, body = _post(
        webui,
        "/api/jobs/restore",
        {"bundle": str(bad), "dest": str(tmp_path / "dest")},
        token=webui.token,
    )
    assert status == 202
    snap = _wait_job(webui, body["job_id"])
    assert snap["state"] == "failed"
    assert "manifest" in snap["error"]
    assert not (tmp_path / "dest").exists()  # 失败不留部分恢复目录


def test_restore_requires_token_403(webui, tmp_path):
    status, body = _post(
        webui,
        "/api/jobs/restore",
        {"bundle": str(tmp_path / "b"), "dest": str(tmp_path / "d")},
    )
    assert status == 403
    assert body["kind"] == "TokenError"
