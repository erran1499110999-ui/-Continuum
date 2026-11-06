# Continuity Studio（角色连续性工作台）

本地优先的 AI 角色备份、诊断、修复与迁移工具（开发中，MVP 阶段）。
首个适配客户端：SillyTavern。

> 依据《AI 角色连续性平台商业企划书 v1.0（2026-11-06）》执行手册开发。

## 数据安全承诺
- **源文件只读**：扫描与备份绝不修改源目录；
- **恢复只写入新目录**，绝不覆盖任何现有数据；
- **备份一致性（尽力检测）**：备份期间源目录应保持静止——若文件在备份过程中发生变化
  （大小或修改时间），备份会中止并明确报告该文件。此为尽力检测，无法覆盖
  "同长度改写并恢复修改时间"等刻意场景；如需强一致性请先做文件系统快照；
- **本地优先**：默认不联网、不上传任何角色数据；
- **不执行**导入文件中的脚本、宏、HTML 或扩展代码。

## 快速开始
要求：Python 3.11+（开发环境为 Python 3.14.5）。

```powershell
# 0. 环境准备
#    - pydantic 使用系统安装；pytest 已解压到 .deps2（如缺失：python tools\fetch_wheels.py）
#    - 沙箱内 PATH 的 python 是 WindowsApps 存根，请使用绝对路径：
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'

# 1. 设置导入路径并运行测试（必须真实执行）
$env:PYTHONPATH = "src;.deps2"
$env:TMP = (Join-Path (Get-Location) '.tmp'); $env:TEMP = $env:TMP
& $py -m pytest

# 2. 生成合成样本（可选，仅用于开发与回归测试，不含真实用户数据）
& $py samples\synthetic\make_samples.py

# 3. 使用 CLI
& $py -m continuity.cli scan "D:\path\to\data"
& $py -m continuity.cli backup "D:\path\to\data" "D:\path\to\backup"
& $py -m continuity.cli restore "D:\path\to\backup" "D:\path\to\restored"
& $py -m continuity.cli verify "D:\path\to\backup"
& $py -m continuity.cli repair "D:\path\to\data" "D:\path\to\fixed"
& $py -m continuity.cli migrate "D:\path\to\st-data" "D:\path\to\migrated"
& $py -m continuity.cli version
```

> 受限环境适配（--basetemp、os.mkdir 0o700 改写、禁用 cacheprovider）见 `pyproject.toml` 与 `tests/conftest.py` 注释，勿删。
> 安装为命令 `continuity`（需联网安装构建依赖）：`pip install -e ".[dev]"`

## 当前进度（2026-11-06）
- [x] 项目骨架与规则文件（AGENTS.md）
- [x] 统一数据模型与 manifest schema（Pydantic）
- [x] 只读扫描器（类型识别、SHA-256、重复检测、结构异常提示）
- [x] 备份/恢复引擎（manifest + SHA-256、防路径穿越、恢复后逐文件校验）
- [x] 修复预览引擎（R0 自动修复 + diff、R2 建议、R3 隔离）——第 5–6 周
- [x] SillyTavern 迁移适配器与迁移验证报告——第 7–8 周
- [x] CLI（scan / backup / restore / verify / repair / migrate / version）
- [ ] 本地 Web UI——核心引擎稳定后

> 0.1.1 / 0.1.2：两轮外部代码审查的整改已完成（5+1 个 P1、4+4 个 P2，详见 CHANGELOG）。

## 目录结构
```
src/continuity/          # 核心逻辑
  cli.py                 # 命令行入口
  models.py              # 统一数据模型（CharacterBundle、Manifest、修复等级）
  hashing.py             # 流式 SHA-256
  scanners/              # 只读扫描：文件类型识别、目录扫描
  backup/                # 备份/恢复引擎与 manifest
  adapters/              # 客户端适配器（计划：SillyTavern）
  repair/                # 修复引擎（计划）
  migration/             # 迁移与验证（计划）
  reports/               # HTML/JSON 报告（计划）
tests/                   # pytest 测试套件
samples/synthetic/       # 合成样本生成器（不含真实用户数据）
docs/                    # 格式兼容矩阵等文档
```

## 边界声明
本工具只迁移用户有权处理的数据；不承诺跨模型人格完全一致；修复只能恢复可从备份、元数据或其他来源推断的结构，不能凭空恢复已丢失的对话内容。NFT 与加密资产交易不属于当前及近期产品范围。
