"""报告输出（计划阶段：HTML/JSON 报告与人工抽样清单）。

当前阶段尚未实现。注意职责边界：
- 引擎内置 JSON 报告（manifest.json / repair-report.json / migration-report.json）
  由各引擎自行写入输出目录，不经过本包；
- 本地 Web UI 的展示层由 src/continuity/webui/ 承担（W1–W8）；
- 本包预留的是「独立 HTML 报告文件」这一线（可分发、可打印的报告产物），
  立项与实现另行排期。
"""
