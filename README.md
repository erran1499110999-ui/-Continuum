# Continuity Studio（角色连续性工作台 · AI Character Continuity Workbench）

> **Local-first** AI character backup, diagnosis, repair and migration tool (MVP stage).
> First supported client: **SillyTavern**.
>
> **本地优先**的 AI 角色备份、诊断、修复与迁移工具（MVP 阶段）。首个适配客户端：**SillyTavern**。

---

## Data Safety Promise · 数据安全承诺

**English**

- **Source files are read-only**: scanning and backup never modify the source directory.
- **Restore only writes to a new directory**: existing data is never overwritten.
- **Backup consistency**: the source directory should remain quiescent during backup — if a file
  changes mid-backup, the backup aborts and reports that file explicitly; an inconsistent bundle
  is never produced.
- **Local-first**: no network upload of any character data by default.
- **No execution of imported content**: scripts, macros, HTML or extension code inside imported
  files are never executed (R3 isolation).
- **Honest repair levels**: R0 deterministic auto-fix / R2 manual advice / R3 isolation are always
  reported truthfully; data that cannot be recovered is never fabricated.

**中文**

- **源文件只读**：扫描与备份绝不修改源目录；
- **恢复只写入新目录**，绝不覆盖任何现有数据；
- **备份一致性**：备份期间源目录应保持静止——若文件在备份过程中发生变化，备份会中止并明确报告该文件，绝不产出不一致的备份包；
- **本地优先**：默认不联网、不上传任何角色数据；
- **不执行**导入文件中的脚本、宏、HTML 或扩展代码（R3 隔离）；
- **修复分级如实**：R0 确定性自动修复 / R2 仅给建议 / R3 隔离，绝不伪造无法恢复的数据。

---

## Quick Start · 快速开始

**Requirements / 环境要求**：Python 3.11+（开发环境实测 Python 3.14.5）。运行时依赖仅 `pydantic>=2`；
开发测试依赖 `pytest`（本仓库开发时以纯 wheel 解压于 `.deps2`）。

**Sandbox note / 受限环境注意**：在受限沙箱中，PATH 里的 `python` 是 WindowsApps 存根，必须使用
绝对路径 `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe`。若 `.deps2` 缺失，用
`python tools\fetch_wheels.py`（绝对路径 Python）恢复开发依赖。

```powershell
# 0. Environment / 环境准备
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = "D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2"   # 按你的工作区路径调整
$env:TMP = "D:\项目1agent角色平台\.tmp"; $env:TEMP = $env:TMP

# 1. Run tests (must actually execute) / 运行测试（必须真实执行）
& $py -m pytest

# 2. Generate synthetic samples (optional; dev/regression only, no real user data)
#    生成合成样本（可选，仅用于开发与回归测试，不含真实用户数据）
& $py samples\synthetic\make_samples.py
```

## CLI Usage · CLI 用法（7 个命令 / 7 commands）

| Command · 命令 | Purpose · 用途 |
|---|---|
| `continuity scan <dir>` | Read-only scan with findings, duplicates and symlink report · 只读扫描（发现、重复文件、符号链接报告） |
| `continuity backup <src> <bundle>` | Create a local backup bundle (source read-only) · 创建本地备份包（源目录只读） |
| `continuity restore <bundle> <dest>` | Restore to a new directory with per-file hash verification · 恢复到新目录并逐文件校验哈希 |
| `continuity verify <bundle>` | Bundle integrity check · 备份包完整性检查 |
| `continuity repair <src> <out>` | Repair preview: R0 auto-fix + diff, R2 advice, R3 isolation · 修复预览：R0 自动修复 + diff、R2 建议、R3 隔离 |
| `continuity migrate <src> <out>` | SillyTavern migration with per-item verification report · SillyTavern 迁移 + 逐项验证报告 |
| `continuity version` | Print tool version · 显示版本号 |

```powershell
& $py -m continuity.cli scan "D:\path\to\data"
& $py -m continuity.cli backup "D:\path\to\data" "D:\path\to\backup"
& $py -m continuity.cli restore "D:\path\to\backup" "D:\path\to\restored"
& $py -m continuity.cli verify "D:\path\to\backup"
& $py -m continuity.cli repair "D:\path\to\data" "D:\path\to\fixed"
& $py -m continuity.cli migrate "D:\path\to\st-data" "D:\path\to\migrated"
& $py -m continuity.cli version
```

> 安装为命令 `continuity`（需联网安装构建依赖）：`pip install -e ".[dev]"`。
> To install as the `continuity` command (network required for build deps): `pip install -e ".[dev]"`.

## Local Web UI · 本地 Web UI

Launch · 启动（纯标准库实现，零新增依赖 / pure-stdlib, zero extra dependencies）：

```powershell
& $py -m continuity.webui               # default port · 默认端口 8777
& $py -m continuity.webui --port 8899   # custom port · 指定端口
& $py -m continuity.webui --no-browser  # do not auto-open browser · 不自动打开浏览器
```

- The server binds **127.0.0.1 only** and never uploads any data · 服务器**仅绑定 127.0.0.1**，不上传任何数据。
- **Port note / 端口提示**：if the default port `8777` is occupied by another program, use
  `--port` to pick a free port. The original default `8765` was changed to `8777` by founder
  decision because `8765` was observed permanently occupied by an IME service on the dev machine
  (Baidu Pinyin listening on `0.0.0.0:8765`).
  如默认端口 `8777` 被其他程序占用，请用 `--port` 指定其它端口。原默认端口 `8765` 因在开发机上被
  输入法常驻占用（实测百度输入法监听 `0.0.0.0:8765`），经创始人裁决改为 `8777`。
- Current Web UI status / 当前 Web UI 进度：overview & scan pages are available (W1–W2);
  backup / verify / restore / repair / migrate / history pages land in W3–W7.
  概览与扫描页已可用（W1–W2）；备份/校验/恢复/修复预览/迁移/历史日志页将在 W3–W7 逐阶段开放。

## Running Tests · 运行测试

```powershell
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = "D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2"
$env:TMP = "D:\项目1agent角色平台\.tmp"; $env:TEMP = $env:TMP
& $py -m pytest
```

- Current result (after W1+W2 strict re-audit fixes, 2026-11-06): **187 collected = 186 passed + 1 skipped**
  (the 1 skip is the Windows symlink-privilege case, an environment limitation handled inside the test).
  当前结果（W1+W2 严格复审修复后，2026-11-06）：**187 collected = 186 passed + 1 skipped**
  （跳过 1 例为 Windows 符号链接权限，属环境限制，测试内已处理）。
- Restricted-environment adaptations (`--basetemp`, the `os.mkdir(0o700)` rewrite, disabling
  cacheprovider) are baked into `pyproject.toml` and `tests/conftest.py` — **do not remove them**.
  受限环境适配（`--basetemp`、`os.mkdir` 0o700 改写、禁用 cacheprovider）已固化在
  `pyproject.toml` 与 `tests/conftest.py` 中，**勿删**。

## Current Progress · 当前进度（2026-11-06）

- [x] Project skeleton & rules file (AGENTS.md) · 项目骨架与规则文件
- [x] Unified data model & manifest schema (Pydantic) · 统一数据模型与 manifest schema
- [x] Read-only scanner (type detection, SHA-256, duplicates, structural findings) · 只读扫描器
- [x] Backup / restore engine (manifest + SHA-256, path-traversal protection, per-file verification) · 备份/恢复引擎
- [x] Repair preview engine (R0 auto-fix + diff, R2 advice, R3 isolation) · 修复预览引擎
- [x] SillyTavern migration adapter & per-item verification report · SillyTavern 迁移适配器与验证报告
- [x] CLI (scan / backup / restore / verify / repair / migrate / version) · CLI 七命令
- [x] Local Web UI W1–W2 (skeleton, security, scan page) · 本地 Web UI W1–W2（骨架/安全/扫描页）
- [ ] Local Web UI W3–W7 (backup/verify/restore/repair/migrate/history pages) · 本地 Web UI W3–W7
- [ ] Usability testing (plan week 9–10) · 可用性测试（第 9–10 周）

> 0.1.1 / 0.1.2 / 0.1.3：three rounds of external code-review remediation are complete
> (P1/P2 items fixed with counter-case tests; see CHANGELOG).
> 0.1.1 / 0.1.2 / 0.1.3：三轮外部代码审查整改已完成（P1/P2 逐项修复并配反例测试，详见 CHANGELOG）。

## Directory Structure · 目录结构

```
src/continuity/          # core logic · 核心逻辑
  cli.py                 # CLI entry · 命令行入口
  models.py              # unified data model · 统一数据模型
  hashing.py             # streaming SHA-256 · 流式 SHA-256
  limits.py              # unified resource budget · 统一资源预算
  safety.py              # executable/script extension policy · 可执行/脚本扩展名策略
  pngutil.py             # streaming PNG chunk reading · 流式 PNG 块读取
  scanners/              # read-only scanning · 只读扫描
  backup/                # backup/restore engine & manifest · 备份/恢复引擎与清单
  repair/                # repair engine (R0/R2/R3 + diffs) · 修复引擎
  adapters/              # client adapters (SillyTavern) · 客户端适配器
  migration/             # migration & verification · 迁移与验证
  reports/               # HTML/JSON reports (planned) · HTML/JSON 报告（计划）
  webui/                 # local Web UI (pure stdlib, W1–W2 live) · 本地 Web UI（纯标准库）
tests/                   # pytest suite · pytest 测试套件
samples/synthetic/       # synthetic sample generator (no real user data) · 合成样本生成器
tools/fetch_wheels.py    # dev-only pure-wheel fetcher (.deps2) · 开发用纯 wheel 下载器
docs/                    # rules, plans, compatibility matrix, review guide · 规则/计划/兼容矩阵/审查指南
```

## Documentation · 文档指引

| Document · 文档 | Content · 内容 |
|---|---|
| `AGENTS.md` | Top-priority rules (10 unbreakable rules) & environment notes · 最高优先级规则（十项不可违反规则）与环境说明 |
| `docs/TEAM-COORDINATION.md` | Multi-session coordination & write scopes · 多会话协作板与写作用域 |
| `docs/webui-plan.md` | Local Web UI development plan (stages W1–W8) · 本地 Web UI 开发计划（W1–W8 分阶段） |
| `docs/format-compatibility.md` | File-type detection matrix · 格式兼容矩阵 |
| `docs/review-guide.md` | External review instructions & test baseline · 外部审查说明与测试基线 |
| `docs/research-*.md` | SillyTavern compatibility / Web UI / business / community research · 兼容性 / Web UI / 商业 / 社区调研 |
| `CHANGELOG.md` | Version history · 变更日志 |

## Known Limitations · 已知限制

- R1 (inferred repair) rules are not implemented yet — they require real-world samples
  (e.g., cross-checking PNG metadata against a same-name JSON).
  R1 可推断修复规则尚未实现（需真实样本：PNG 元数据与同名 JSON 比对等）。
- Only the SillyTavern adapter is supported; RisuAI and other clients are planned later.
  仅支持 SillyTavern 一个客户端适配器；RisuAI 等留待后续。
- Text detection supports UTF-8 only; UTF-16 / GBK detection is pending.
  文本识别仅支持 UTF-8；UTF-16 / GBK 编码识别待扩展。
- Embedded-reference detection for chat attachments (images/audio) is pending.
  聊天附件（图片/音频）的内嵌引用检测待补充。
- Standalone HTML report generation is not implemented (the Web UI presentation layer is the
  current focus; see `docs/webui-plan.md`). 独立 HTML 报告尚未实现（当前以 Web UI 展示层为主，见 webui-plan.md）。

## Boundary Statement · 边界声明

This tool only migrates data the user is entitled to process; it does not promise identical
personality across models; repair can only recover structure inferable from backups, metadata or
other sources, and cannot resurrect lost conversation content. NFT and crypto-asset trading are
out of current and near-term scope.

本工具只迁移用户有权处理的数据；不承诺跨模型人格完全一致；修复只能恢复可从备份、元数据或其他来源推断的结构，
不能凭空恢复已丢失的对话内容。NFT 与加密资产交易不属于当前及近期产品范围。
