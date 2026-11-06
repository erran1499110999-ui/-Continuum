# Continuity Studio 外部审查说明（给 ChatGPT / 审查者）

> 本文件与代码一起打包，供外部 AI（如 ChatGPT）审查使用。
> 项目依据：《AI 角色连续性平台商业企划书 v1.0（2026-11-06）》（见同包的 business-plan-text.txt，系原文提取，可放心比对）。

## 一、项目一句话

本地优先的 AI 角色备份、诊断、修复与迁移工具（Continuity Studio），
首个适配客户端 SillyTavern。MVP 阶段：扫描 → 备份/恢复 → 修复预览 → 迁移验证。

> **0.1.1 / 0.1.2 / 0.1.3 更新说明**：本包为 0.1.3。0.1.1 修复第一轮审查的 5 P1+4 P2；
> 0.1.2 修复第二轮审查的 1 P1+4 P2；0.1.3 修复第三轮审查的 1 P1+4 P2
> （IDAT 流式增量 CRC 校验、备份检测"尽力"语义与局限测试、坏行索引空白保留与
> 格式说明、CLI 迁移不完整非零退出码、损坏文件纳入统一资源预算）。详见 CHANGELOG。
> 请重点复核 0.1.3 修复是否到位，以及是否引入新的回归。

## 二、建议的审查清单（请逐项给出结论与证据）

1. **功能完整性**：CLI 六个命令（scan / backup / restore / verify / repair / migrate）
   是否实现完整、互相自洽？对照企划书 90 天计划第 2–8 周任务。
2. **安全规则合规**（对照 AGENTS.md 十项不可违反规则）：
   - 原始文件只读，修复/迁移只写新目录；
   - 不执行导入内容（R3 隔离）——检查 adapters/sillytavern.py、repair/engine.py；
   - 防路径穿越（backup/engine.py 的 safe_join）、大小上限、符号链接跳过；
   - 不伪造数据（R0/R1/R2/R3 分级）——检查 repair/rules.py；
   - 未知字段绝不静默丢弃（migration/engine.py 的 sidecar 与 unsupported 清单）。
3. **数据完整性**：manifest schema（Pydantic 校验 + SHA-256）、备份恢复逐文件哈希校验、
   迁移后逐项验证与完整性分数的分母解释是否严谨。
4. **测试质量**：tests/ 覆盖是否充分、断言是否有效（防止"删测试过验收"）；
   本项目真实测试结果：**104 passed, 1 skipped**（跳过的 1 例是 Windows 符号链接权限，
   属环境限制，测试内已处理）。测试在本机 Python 3.14.5 下真实执行通过。

## 测试基线清单（0.1.3，供逐项比对）

以下为随包版本的真实收集数（`python -m pytest --collect-only -q`，本机 Python 3.14.5）。
项目尚无 Git 历史，此清单作为"是否删除/削弱过测试"的比对基线：

| 测试文件 | 用例数 |
|---|---|
| tests/test_adapter.py | 14 |
| tests/test_backup_engine.py | 22 |
| tests/test_cli.py | 8 |
| tests/test_filetype.py | 11 |
| tests/test_manifest.py | 15 |
| tests/test_migration.py | 14 |
| tests/test_pngutil.py | 6 |
| tests/test_repair.py | 9 |
| tests/test_scan.py | 6 |
| **合计** | **105（运行结果 104 passed + 1 skipped）** |
5. **代码质量**：模块划分（scanners/backup/repair/adapters/migration 分层）、
   适配器架构、错误信息是否面向用户、文档与注释是否与实现一致。
6. **与企划书的偏差**（已知、有意为之，请评估是否合理）：
   - R1 可推断修复规则尚未实现（企划书要求基于真实样本设计，本仓库只有合成样本）；
   - 仅支持 SillyTavern 一个客户端适配器（RisuAI 等为后续）；
   - 尚未实现 HTML 报告与本地 Web UI（企划书第 9–10 周任务）；
   - 文本识别仅支持 UTF-8；聊天附件内嵌引用检测未实现。

## 三、项目结构速览

```
src/continuity/
  models.py        # Pydantic 数据模型（BundleManifest、修复等级 R0-R3、文件类型）
  scanners/        # 只读扫描：filetype.py（类型识别）、scan.py（目录扫描+发现分级）
  backup/          # 备份/恢复引擎（manifest+SHA-256、safe_join 防穿越）+ verify
  repair/          # 修复引擎（rules.py：R0-001 尾逗号、R0-002 BOM；engine.py：修复副本+diff）
  adapters/        # SillyTavern 适配器（角色卡 V1/V2、PNG/JSON、聊天 JSONL、世界书）
  migration/       # 迁移引擎（导出+逐项验证+完整性分数+sidecar）
  cli.py           # 命令行入口（6 个命令）
tests/             # pytest：helpers/conftest/test_filetype/test_manifest/
                   #        test_backup_engine/test_scan/test_repair/test_adapter/
                   #        test_migration/test_cli
samples/synthetic/ # 合成样本生成器（不含任何真实用户数据）
docs/              # format-compatibility.md 格式兼容矩阵
```

## 四、本地复跑（可选，审查者可验证）

要求 Python 3.11+（开发机为 3.14.5），依赖：pydantic>=2（系统已装）、pytest>=8
（本仓库开发时解压于 .deps2，未随包提供；审查者可自行 `pip install pytest`）。

```bash
PYTHONPATH=src python -m pytest          # Windows PowerShell: $env:PYTHONPATH="src"; python -m pytest
python -m continuity.cli scan samples/synthetic/out
python -m continuity.cli backup samples/synthetic/out ./demo-bundle
python -m continuity.cli verify ./demo-bundle
python -m continuity.cli restore ./demo-bundle ./demo-restored
python -m continuity.cli repair samples/synthetic/out ./demo-fixed
python -m continuity.cli migrate samples/synthetic/out ./demo-migrated
```

> 注意：本开发环境为受限沙箱，pytest 的 basetemp 与 cacheprovider 适配写在
> pyproject.toml 与 tests/conftest.py 注释中；在普通环境下这些设置无害，无需移除。

## 五、隐私说明

本包内**不含任何真实用户数据**：所有样本均由 samples/synthetic/make_samples.py
与 tests/helpers.py 程序化生成。business-plan-text.txt 为内部企划书全文提取，
如不希望与外部 AI 分享可自行删除该文件后再上传。

## 六、给审查者的额外提问（欢迎超出清单）

- 是否存在会导致数据损坏或静默丢失的边界情况？
- 完整性分数的计算与解释是否可能误导用户？
- CLI 的错误处理对非技术用户是否足够友好？
- 下一个阶段（本地 Web UI）最值得优先解决的技术风险是什么？
