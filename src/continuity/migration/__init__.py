"""迁移与验证（企划书第 7–8 周任务）。

迁移后逐项比较源数据与目标导出结果，生成完整性报告。
首个适配器：SillyTavern。
"""

from .engine import MigrationError, MigrationReport, migrate_sillytavern

__all__ = ["MigrationError", "MigrationReport", "migrate_sillytavern"]
