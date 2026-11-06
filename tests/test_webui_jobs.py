"""W1：任务队列真实运行测试——串行执行、状态机、错误透传、日志、停止。

W2 复审修复后语义（docs/webui-plan.md 第 3 节）：同一时刻至多 1 个
待处理/运行任务，忙碌时 submit 抛 JobQueueFullError；已完成任务
内存保留上限 64。
"""
from __future__ import annotations

import threading
import time

import pytest

from continuity.webui.jobs import JobManager, JobQueueFullError

TERMINAL = frozenset({"succeeded", "failed"})


@pytest.fixture
def manager():
    mgr = JobManager()
    yield mgr
    mgr.stop(timeout=5)


def wait_state(mgr, job_id, *, timeout=5.0):
    """轮询等待任务进入终态（succeeded/failed），超时即失败。

    所有测试用同一等待路径，避免各自 sleep+断言的时序写法不一致。
    """
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


def test_second_submit_rejected_while_active(manager):
    """回归（A5）：已有任务排队/运行时，新提交被拒（JobQueueFullError）。"""
    gate = threading.Event()

    def first():
        gate.wait(timeout=5)
        return "a"

    id1 = manager.submit(first)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and manager.get(id1)["state"] != "running":
        time.sleep(0.01)
    assert manager.get(id1)["state"] == "running"

    with pytest.raises(JobQueueFullError):
        manager.submit(lambda: "b")

    gate.set()
    snap = wait_state(manager, id1)
    assert snap["state"] == "succeeded"
    assert snap["result"] == "a"


def test_submit_after_completion_ok(manager):
    """回归（A5）：前一个任务结束后，新提交恢复正常。"""
    wait_state(manager, manager.submit(lambda: "first"))
    snap2 = wait_state(manager, manager.submit(lambda: "second"))
    assert snap2["state"] == "succeeded"
    assert snap2["result"] == "second"


def test_finished_jobs_pruned_to_cap(manager):
    """回归（A7）：已完成任务内存保留有上限（64），字典不会无限增长。"""
    for i in range(70):
        job_id = manager.submit(lambda i=i: i)
        wait_state(manager, job_id)
    finished = [j for j in manager._jobs.values() if j.state in TERMINAL]
    assert len(finished) <= 64
    assert len(manager._jobs) == len(finished)  # 无活动任务时字典即保留区
    assert len(manager._jobs) <= 64


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
