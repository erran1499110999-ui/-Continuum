"""后台任务队列（W1）：单工作线程串行执行。

本地单用户工具，任务串行可避免输出目录争用与资源预算冲突。
后续阶段（W2 起）的扫描/备份/恢复/修复/迁移端点都经由本队列执行；
任务状态为内存快照（不落盘）；落盘的历史记录见 history.py（W7 接入）。
"""
from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

STATE_QUEUED = "queued"
STATE_RUNNING = "running"
STATE_SUCCEEDED = "succeeded"
STATE_FAILED = "failed"
TERMINAL_STATES = frozenset({STATE_SUCCEEDED, STATE_FAILED})
ACTIVE_STATES = frozenset({STATE_QUEUED, STATE_RUNNING})

# 已完成任务的内存保留上限（防任务字典无限增长；同时队列本身至多 1 个活动任务）
MAX_FINISHED_JOBS = 64


class JobQueueFullError(RuntimeError):
    """已有任务正在排队或运行，拒绝新提交（对应 HTTP 409）。"""


@dataclass
class Job:
    """一次后台任务的完整状态（内存快照）。"""

    id: str
    fn: Callable[[], Any]
    state: str = STATE_QUEUED
    result: Any = None
    error: str = ""
    error_kind: str = ""
    log_lines: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """对外快照（log_tail 只保留尾部，避免大响应）。"""
        return {
            "id": self.id,
            "state": self.state,
            "error": self.error,
            "error_kind": self.error_kind,
            "log_tail": list(self.log_lines[-50:]),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result": self.result,
        }


class JobManager:
    """线程安全的任务队列：submit 后由唯一工作线程按提交顺序串行执行。

    任务函数抛出的异常一律捕获为 failed 状态（error/error_kind），
    绝不拖垮工作线程；任务函数内可通过 manager.log(...) 追加日志行。
    """

    def __init__(self, max_log_lines: int = 200) -> None:
        self._queue: "queue.Queue[Optional[str]]" = queue.Queue()
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()
        self._local = threading.local()
        self._stopped = False
        self._max_log_lines = max_log_lines
        self._worker = threading.Thread(
            target=self._run_worker, name="continuity-webui-jobs", daemon=True
        )
        self._worker.start()

    # —— 对外接口 ——

    def submit(self, fn: Callable[[], Any]) -> str:
        """提交任务并返回 job id。

        单任务串行（与 docs/webui-plan.md 第 3 节一致）：同一时刻至多 1 个
        待处理/运行任务，忙碌时抛 JobQueueFullError（server 映射 409）；
        队列停止后提交抛 RuntimeError（server 映射 503）。
        """
        with self._lock:
            if self._stopped:
                raise RuntimeError("任务队列已停止，无法提交新任务")
            # ACTIVE_STATES 检查在锁内完成：提交与完成并发时不会误判忙碌/漏判
            if any(j.state in ACTIVE_STATES for j in self._jobs.values()):
                raise JobQueueFullError("已有任务正在排队或运行，请等待其完成后再提交")
            job = Job(id=uuid.uuid4().hex[:12], fn=fn)
            self._jobs[job.id] = job
        self._queue.put(job.id)
        return job.id

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        """读取任务快照；未知 id 返回 None。"""
        with self._lock:
            job = self._jobs.get(job_id)
            return job.to_dict() if job is not None else None

    def log(self, line: str) -> None:
        """把一行日志写入当前线程正在执行的任务（供任务函数内部调用）。

        实现：工作线程执行任务前把 job 存入线程局部变量（threading.local），
        任务函数内调用 manager.log 时经线程局部变量找到所属任务——
        单工作线程下天然无并发写，跨线程调用则静默忽略。
        """
        job: Optional[Job] = getattr(self._local, "job", None)
        if job is None:
            return
        with self._lock:
            job.log_lines.append(line)
            if len(job.log_lines) > self._max_log_lines:
                del job.log_lines[: len(job.log_lines) - self._max_log_lines]

    def stop(self, timeout: float = 5.0) -> None:
        """停止工作线程：完成已排队任务后退出；可重复调用。"""
        with self._lock:
            if self._stopped:
                return
            self._stopped = True
        self._queue.put(None)
        self._worker.join(timeout)

    # —— 内部 ——

    def _run_worker(self) -> None:
        while True:
            job_id = self._queue.get()
            if job_id is None:
                break
            with self._lock:
                job = self._jobs.get(job_id)
            if job is None:
                continue
            job.state = STATE_RUNNING
            job.started_at = time.time()
            self._local.job = job
            try:
                job.result = job.fn()
                job.state = STATE_SUCCEEDED
            except Exception as exc:  # 任务异常一律记录，不拖垮工作线程
                job.state = STATE_FAILED
                job.error = str(exc) or type(exc).__name__
                job.error_kind = type(exc).__name__
            finally:
                job.finished_at = time.time()
                self._local.job = None
                with self._lock:
                    self._prune_locked()

    def _prune_locked(self) -> None:
        """已完成任务只保留最近 MAX_FINISHED_JOBS 个（调用方必须已持锁）。

        动机：任务字典随使用无限增长会耗尽内存（复审项 A7）；
        有活动任务时字典最多 64 个已完成 + 1 个活动任务，保持有界。
        """
        finished = [j for j in self._jobs.values() if j.state in TERMINAL_STATES]
        if len(finished) <= MAX_FINISHED_JOBS:
            return
        oldest = sorted(finished, key=lambda j: j.finished_at or 0.0)
        for job in oldest[: len(finished) - MAX_FINISHED_JOBS]:
            self._jobs.pop(job.id, None)
