"""修复引擎（企划书第 5–6 周任务）。

R0 确定性修复自动生成修复副本；R1 可推断修复（须用户确认，规则待补）；
R2 仅建议；R3 隔离不执行。所有修复输出到新目录并附带差异报告。
"""

from .engine import RepairError, RepairReport, apply_repairs
from .rules import RepairFix, plan_file

__all__ = ["RepairError", "RepairReport", "apply_repairs", "RepairFix", "plan_file"]
