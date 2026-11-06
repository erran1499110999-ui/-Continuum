"""本地操作历史（W1 骨架，W7 接入 /api/history 与历史页）。

只存「操作元数据与统计摘要」（时间、操作类型、目录名、结果摘要），
绝不存任何文件内容（AGENTS.md 规则 2）。单进程 + 线程锁保证追加安全。
存储位置：优先工作区 .tmp/webui-history.jsonl（开发沙箱，已被 .gitignore）；
不可写时回退 %LOCALAPPDATA%\\ContinuityStudio\\history.jsonl。
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

_FILENAME = "webui-history.jsonl"


def default_history_path() -> Path:
    """解析默认历史文件路径（见模块 docstring）。

    history.py 位于 <workspace>/src/continuity/webui/ 下，
    parents[3] 即工作区根目录。
    """
    workspace = Path(__file__).resolve().parents[3]
    tmp = workspace / ".tmp" / _FILENAME
    try:
        tmp.parent.mkdir(parents=True, exist_ok=True)
        return tmp
    except OSError:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
        fallback = Path(base) / "ContinuityStudio"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback / _FILENAME


class HistoryStore:
    """JSONL 追加式本地历史（读容忍坏行，绝不因历史文件损坏而崩溃）。"""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path is not None else default_history_path()
        self._lock = threading.Lock()

    def append(self, record: Dict[str, Any]) -> None:
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load(self) -> List[Dict[str, Any]]:
        if not self.path.is_file():
            return []
        records: List[Dict[str, Any]] = []
        with self._lock:
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # 坏行跳过，不崩溃（历史仅辅助展示）
                if isinstance(obj, dict):
                    records.append(obj)
        return records
