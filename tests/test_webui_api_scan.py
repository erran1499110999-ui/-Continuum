"""W2：扫描端点真实运行测试——真实服务器 + 真实 HTTP + 真实引擎扫描。

断言核心：
- HTTP 响应 == 直接调用 scan_directory 的序列化结果（逐字段等价比对）；
- 源目录零写入（前后内容快照比对）；
- 中文文件名路径样本；
- 错误路径全套（源缺失/非目录/空值/非法 JSON/非对象/超限/未知任务/无令牌）。
全程无 mock：服务器真实监听 127.0.0.1 随机端口，扫描真实执行。
"""
from __future__ import annotations

import hashlib
import http.client
import json
import threading
import time

import pytest

from continuity.scanners.scan import scan_directory
from continuity.webui.server import WebUIServer
from continuity.webui.views import scan_report_to_json
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


def _post_raw(server, path, raw_body: bytes, *, token=None):
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["X-Continuity-Token"] = token
    conn.request("POST", path, body=raw_body, headers=headers)
    resp = conn.getresponse()
    status = resp.status
    raw = resp.read()
    conn.close()
    return status, json.loads(raw.decode("utf-8")) if raw else None


def _get(server, path, *, token=None):
    conn = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    headers = {}
    if token is not None:
        headers["X-Continuity-Token"] = token
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


def _run_scan(server, source):
    """提交扫描任务并等待结束，返回最终 job 快照。"""
    status, payload = _post(server, "/api/jobs/scan", {"source": str(source)}, token=server.token)
    assert status == 202, payload
    snap = _wait_job(server, payload["job_id"])
    return snap


def _snapshot_tree(root):
    """目录内容快照（相对路径 → SHA-256），用于源目录零写入断言。"""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


# —— 核心等价性：HTTP 响应 == 直接调用引擎 ——

def test_scan_job_matches_direct_engine_call(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata", with_json_card=True)
    expected = scan_report_to_json(scan_directory(tree))

    snap = _run_scan(webui, tree)

    assert snap["state"] == "succeeded", snap
    assert snap["result"] == expected  # 逐字段等价比对（含枚举已转字符串）
    assert snap["error"] == ""
    assert snap["log_tail"] == [f"扫描完成: {len(expected['files'])} 个文件，{len(expected['findings'])} 项发现"]


def test_scan_source_stays_untouched(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata", with_json_card=True)
    before = _snapshot_tree(tree)

    snap = _run_scan(webui, tree)

    assert snap["state"] == "succeeded"
    assert _snapshot_tree(tree) == before  # 源目录零写入（内容与文件集合均不变）


def test_scan_chinese_filenames(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata", with_json_card=True)
    expected = scan_report_to_json(scan_directory(tree))

    snap = _run_scan(webui, tree)

    assert snap["state"] == "succeeded"
    assert snap["result"] == expected
    rels = {f["rel_path"] for f in snap["result"]["files"]}
    assert "cards/角色卡.json" in rels
    assert "cards/角色卡.png" in rels


def test_scan_findings_and_duplicates(webui, tmp_path):
    root = tmp_path / "d"
    root.mkdir()
    (root / "broken.json").write_text('{\n  "name": "坏样本",\n}\n', encoding="utf-8")
    (root / "empty.txt").write_text("", encoding="utf-8")
    (root / "a.txt").write_text("same-content", encoding="utf-8")
    (root / "b.txt").write_text("same-content", encoding="utf-8")

    snap = _run_scan(webui, root)

    assert snap["state"] == "succeeded"
    result = snap["result"]
    assert result == scan_report_to_json(scan_directory(root))
    problems = {(f["severity"], f["repair_level"], f["problem"]) for f in result["findings"]}
    assert ("warning", "r2", "疑似损坏或不完整的 JSON 文件") in problems
    assert ("info", None, "空文件") in problems
    assert len(result["duplicates"]) == 1
    assert sorted(result["duplicates"][0]) == ["a.txt", "b.txt"]


# —— 错误路径 ——

def test_scan_missing_source_400(webui, tmp_path):
    status, payload = _post(
        webui, "/api/jobs/scan", {"source": str(tmp_path / "nope")}, token=webui.token
    )
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "源目录不存在" in payload["error"]


def test_scan_source_is_file_400(webui, tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    status, payload = _post(webui, "/api/jobs/scan", {"source": str(f)}, token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "源目录不存在" in payload["error"]


def test_scan_empty_source_400(webui):
    status, payload = _post(webui, "/api/jobs/scan", {"source": "   "}, token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "不能为空" in payload["error"]


def test_scan_missing_key_400(webui):
    status, payload = _post(webui, "/api/jobs/scan", {}, token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "不能为空" in payload["error"]


def test_scan_invalid_json_400(webui):
    status, payload = _post_raw(webui, "/api/jobs/scan", b"not json", token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "请求体不是合法 JSON" in payload["error"]


def test_scan_non_object_body_400(webui):
    status, payload = _post_raw(webui, "/api/jobs/scan", b"[1, 2]", token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "请求体必须是 JSON 对象" in payload["error"]


def test_scan_oversized_body_400(webui):
    status, payload = _post_raw(webui, "/api/jobs/scan", b"x" * 70000, token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"
    assert "超过上限" in payload["error"]


def test_scan_unknown_job_404(webui):
    status, payload = _get(webui, "/api/jobs/does-not-exist", token=webui.token)
    assert status == 404
    assert payload["kind"] == "NotFound"


def test_scan_requires_token_403(webui, tmp_path):
    status, payload = _post(webui, "/api/jobs/scan", {"source": str(tmp_path)})
    assert status == 403
    assert payload["kind"] == "TokenError"


def test_scan_empty_body_400(webui):
    status, payload = _post_raw(webui, "/api/jobs/scan", b"", token=webui.token)
    assert status == 400
    assert payload["kind"] == "ValidationError"


def test_scan_jobs_stopped_503(webui, tmp_path):
    tree = make_st_sample_tree(tmp_path / "stdata")
    webui.jobs.stop(timeout=5)
    status, payload = _post(webui, "/api/jobs/scan", {"source": str(tree)}, token=webui.token)
    assert status == 503
    assert payload["kind"] == "JobsError"


def test_scan_second_submit_busy_409(webui, tmp_path):
    """回归（A5+A7）：已有任务运行中再次提交扫描 → 409 JobsBusy；完成后可再次提交。"""
    gate = threading.Event()
    blocker = webui.jobs.submit(lambda: gate.wait(timeout=5))
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and webui.jobs.get(blocker)["state"] != "running":
        time.sleep(0.01)
    assert webui.jobs.get(blocker)["state"] == "running"

    tree = make_st_sample_tree(tmp_path / "stdata")
    status, payload = _post(webui, "/api/jobs/scan", {"source": str(tree)}, token=webui.token)
    assert status == 409
    assert payload["kind"] == "JobsBusy"
    assert "已有任务" in payload["error"]

    gate.set()
    _wait_job(webui, blocker)

    snap = _run_scan(webui, tree)
    assert snap["state"] == "succeeded"
