"""W1：任务队列真实运行测试——串行执行、状态机、错误透传、日志、停止。"""
from __future__ import annotations

import threading
import time

import pytest

from continuity.webui.jobs import JobManager

TERMINAL = frozenset({"succeeded", "failed"})


@pytest.fixture
def manager():
    mgr = JobManager()
    yield mgr
    mgr.stop(timeout=5)


def wait_state(mgr, job_id, *, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        snap = mgr.get(job_id)
        if snap and snap["state"] in TERMINAL:
            return snap
        time.sleep(0.02)
    raise AssertionError(f"job {job_id} 未在 {timeout}s 内结束: {mgr.get(job_id)}")


def test_success_result(manager):
    job_id = manager.submit(lambda: 42)
    snap = wait_state(manager, job_id)
    assert snap["state"] == "succeeded"
    assert snap["result"] == 42
    assert snap["error"] == ""
    assert snap["error_kind"] == ""
    assert snap["finished_at"] is not None


def test_serial_execution_and_order(manager):
    gate = threading.Event()
    order = []

    def first():
        order.append("first-start")
        gate.wait(timeout=5)
        order.append("first-end")
        return "a"

    def second():
        order.append("second-start")
        return "b"

    id1 = manager.submit(first)
    id2 = manager.submit(second)

    # 第一个任务被门闩挡住期间，第二个必须保持排队（串行队列）
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and manager.get(id1)["state"] != "running":
        time.sleep(0.01)
    assert manager.get(id1)["state"] == "running"
    assert manager.get(id2)["state"] == "queued"
    assert "second-start" not in order

    gate.set()
    snap1 = wait_state(manager, id1)
    snap2 = wait_state(manager, id2)
    assert snap1["state"] == "succeeded"
    assert snap2["state"] == "succeeded"
    assert snap2["result"] == "b"
    assert order == ["first-start", "first-end", "second-start"]
    assert snap1["finished_at"] <= snap2["finished_at"]


def test_failure_captured(manager):
    def boom():
        raise ValueError("任务爆炸")

    job_id = manager.submit(boom)
    snap = wait_state(manager, job_id)
    assert snap["state"] == "failed"
    assert snap["error"] == "任务爆炸"
    assert snap["error_kind"] == "ValueError"
    assert snap["result"] is None


def test_log_lines(manager):
    def work():
        manager.log("开始处理")
        manager.log("完成")
        return "done"

    job_id = manager.submit(work)
    snap = wait_state(manager, job_id)
    assert snap["state"] == "succeeded"
    assert snap["log_tail"] == ["开始处理", "完成"]


def test_unknown_job(manager):
    assert manager.get("does-not-exist") is None


def test_submit_after_stop_rejected(manager):
    manager.stop(timeout=5)
    with pytest.raises(RuntimeError):
        manager.submit(lambda: None)
