# 验收清单 — 阶段一至三 + 0.1.1/0.1.2/0.1.3 外部审查整改

> 验收支持文档（qa-reviewer 独立审核，2026-11-06，第二轮修订）
> 依据：AGENTS.md（最新版）、CHANGELOG.md、docs/TEAM-COORDINATION.md（第二轮写作用域）
> 审核人写作用域：仅本文件；未修改任何源码/测试/配置，未执行 git commit。
> 审核方法：真实运行测试 + 静态交叉核对（git 首次 commit 前无历史基线，0.1.2/0.1.3 增量以「CHANGELOG 声明 ↔ 现行代码/测试」核对；commit 产生后另做工作区↔commit 一致性验证）。

## 0. 验收范围梳理

| 阶段 | 交付物 | 依据 |
|------|--------|------|
| 阶段一（骨架+模型） | pyproject、AGENTS.md、统一数据模型（Pydantic：BundleManifest/ManifestEntry/修复等级枚举） | CHANGELOG 0.1.0、AGENTS.md |
| 阶段二（扫描+备份/恢复） | 只读扫描器、备份/恢复引擎（manifest+SHA-256、verify、原子恢复） | 同上 |
| 阶段三（修复+迁移） | 修复引擎（R0/R2/R3+diff 报告）、SillyTavern 适配器、迁移引擎+验证报告、CLI | 同上 |
| 0.1.1 整改 | 5 个 P1 + 4 个 P2（多卡迁移、原子恢复、完整性分数语义、报告脱敏、资源预算、备份竞态、PNG 校验、路径规范化、坏行保留） | CHANGELOG 0.1.1 |
| 0.1.2 整改 | 1 个 P1 + 4 个 P2（迁移覆盖完整性、坏行字节保留、PNG 流式读取、verify 清单外文件、stat 签名变化检测） | CHANGELOG 0.1.2 |
| 0.1.3 整改 | 1 个 P1 + 4 个 P2（IDAT 增量 CRC、备份检测语义文档化、坏行索引语义、CLI 不完整退出码、损坏 PNG 资源预算） | CHANGELOG 0.1.3 |

## 1. 真实测试执行记录（规则 10：必须实际运行）

**执行命令**（照抄 AGENTS.md「环境说明」，两轮均真实执行）：

```powershell
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = 'D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'
$env:TMP = 'D:\项目1agent角色平台\.tmp'; $env:TEMP = $env:TMP
& $py -m pytest -v
```

| 轮次 | 时间 | 收集 | 结果 | 耗时 | 退出码 |
|------|------|------|------|------|--------|
| 第一轮（0.1.2 基线） | 2026-11-06 22:09 | 100 | **99 passed, 1 skipped**, 1 warning | 1.74s | 0 |
| 第二轮（0.1.3 基线，最新） | 2026-11-06 22:22 | 105 | **104 passed, 1 skipped**, 1 warning | 1.65s | 0 |

**第二轮各文件明细**：test_adapter 14、test_backup_engine 21 通过+1 跳过、test_cli 8、test_filetype 11、test_manifest 15、test_migration 14、test_pngutil 6、test_repair 9、test_scan 6（合计 104 passed + 1 skipped = 105 collected）。

- 1 skipped = `tests/test_backup_engine.py::test_symlink_skipped`——沙箱无法创建符号链接时的**环境条件跳过**（`pytest.skip` 包裹 OSError），非删除/禁用测试，两轮不变；
- 1 warning = 第三方 anyio pytest 插件 `PytestRemovedIn10Warning`（CallSpec2 更名），与本项目无关；
- Python 3.14.5（绝对路径解释器，非 PATH 存根）；pytest 9.2.0（.deps2）；临时文件全部落在 `.tmp`（已 gitignore），工作区无 `.pytest_cache` 残留；运行前确认无并发 pytest 进程，basetemp 无冲突。

**与记录比对（如实报告）**：
- CHANGELOG 0.1.3「真实运行：104 passed, 1 skipped」→ 与本次实测**完全一致** ✓；
- AGENTS.md 第 32 行「测试套件（104 例）」→ 实测收集 **105 项**（104 passed + 1 skipped），少计 1 例（把 passed 数当成了总数），见风险 R2；
- commit 1233289 的 message「104 测试通过」→ 为 passed 数，未计 1 例 skip（已入库无法修改，无害表述偏差）；
- 团队内流传的「103 passed + 1 skipped」→ 与实测不符（实测 104 passed），以本次真实运行为准。

**结论：通过。** 证据：上述两轮真实运行输出；pyproject 内置 `--basetemp=.tmp/pytest-basetemp2 -p no:cacheprovider` 与 conftest 沙箱适配未变（mtime 早于两轮测试，未被改动）。

## 2. 审查整改核对（0.1.1–0.1.3）

### 2.1 Git 状态核对（只读命令）

- 第一轮（22:09）：仓库 0 commit，全部文件 untracked，`git diff HEAD` 不可用；
- 第二轮（22:22）：创始人已于 22:19:31 执行首次 commit `1233289`（48 文件入库，含 src/tests/文档，**不含** continuity-studio-review.zip、_docx_text.txt、.tmp、.deps2——已通过 .gitignore 新增规则排除，第一轮 R1 建议被采纳）；
- 当前工作区 ↔ commit：`git diff HEAD --stat` 仅 `docs/TEAM-COORDINATION.md`（lead 第二轮写作用域更新，11 行新增，未提交）；**src/tests/pyproject/AGENTS/CHANGELOG 与 commit 完全一致，无代码漂移**；
- 结论：0.1.2/0.1.3 增量仍无历史基线（唯一 commit 是全量快照），增量核对方法为静态交叉核对 + 工作区/commit 一致性验证，已如实标注。

### 2.2 0.1.3 逐项核对

| CHANGELOG 声明 | 代码证据（文件:行） | 测试证据 | 结论 |
|----------------|---------------------|----------|------|
| P1 IDAT 增量 CRC：固定缓冲区逐段校验（类型字节+数据，不整块载入）；complete 仅在全块通过且读到 IEND 时为 True；损坏 IDAT 卡在扫描/迁移判定损坏 | `pngutil.py:83-107`（1 MiB 缓冲增量 `zlib.crc32`，截断/CRC 错误均记录）；`filetype.py` 内存路径本就校验 IDAT CRC；适配器使用流式读取 | `test_pngutil.py:8-14`（新，只破坏 IDAT CRC 必须检出且 complete=False）；`test_pngutil.py:53-65`（更新强化：大 IDAT 增量校验通过）；`test_migration.py:186-195`（端到端改用 IDAT 损坏场景：扫描判损坏→迁移报错→清理） | ✅ 落地 |
| P2 备份变化检测语义文档化（尽力检测，明确无法检出「同长度改写并恢复 mtime」） | `backup/engine.py:125-133`（docstring 注明局限、建议文件系统快照与源目录静止） | `test_backup_engine.py:138-154`（新，显式锁定已知局限：恢复 mtime 后签名不变） | ✅ 落地 |
| P2 坏行索引语义：保留原始字节仅去行结束符（含行内空白）+ 格式说明头，指向 .original 副本 | `adapters/sillytavern.py:194-212`（bad_lines 由 stripped 改为 rstrip 后的 line）；`migration/engine.py:213-219`（sidecar 头部写入索引格式说明与还原指引） | `test_adapter.py:105-110`（新，断言 `b"  {bad json  "` 保留行内/外围空白） | ✅ 落地 |
| P2 CLI 迁移不完整：明确输出「迁移不完整」并返回非零退出码 1 | `cli.py:156-160, 172-173` | `test_cli.py:65-79`（新，monkeypatch 模拟不可读，断言 `main(...) == 1` 且输出含「迁移不完整」） | ✅ 落地 |
| P2 损坏 PNG 资源预算：损坏文件复制纳入单文件与累计大小预算，与附件共用上限 | `migration/engine.py:250-264`（损坏文件先检查 max_file_bytes、计入 asset_total 的 max_total_bytes） | `test_migration.py:207-228`（新，受控 monkeypatch 专测迁移内部预算：损坏文件计入累计后超限报错并清理） | ✅ 落地 |

### 2.3 无删除测试 / 无降低断言 / 无硬编码伪装

- **数量算术自洽**：第一轮 99 passed + 1 skipped；0.1.3 净增 5 个新测试函数（test_adapter/test_backup_engine/test_cli/test_migration/test_pngutil 各 +1）→ 104 passed + 1 skipped = 105 collected。CHANGELOG「新增/更新反例测试 6 例」= 5 新增 + 1 更新（大 IDAT 测试），另单独记载「端到端损坏卡测试改用 IDAT 损坏场景」为第 2 处更新，完全对账；
- **旧测试全保留**：与第一轮通读版本逐一比对，旧测试函数无一删除；`test_stream_large_idat_skipped` → `test_stream_large_idat_crc_verified` 为**改名并加强断言**（新增 IDAT 无错误断言），`test_corrupt_card_png_fails_loudly` 破坏点由 IHDR CRC 改为更严苛的 IDAT CRC（旧版本该场景会漏检，新实现必须检出），均属**提升而非降低**；
- 全 tests 目录 grep 无 `assert True`/`assert 1 == 1` 占位；抽样通读新增测试断言均为真实行为断言（字节相等、异常、退出码、清理验证）；
- 0.1.1/0.1.2 各项修复证据（见第一轮清单）：代码与测试均未回退（工作区与 commit 一致，mtime 与测试结果双重印证）。

**结论：0.1.1/0.1.2/0.1.3 三轮整改均已落地，无测试删除、无断言降低、无硬编码伪装。通过。**

## 3. AGENTS.md 十条规则抽查

| 规则 | 检查内容与实测结果 | 证据 | 结论 |
|------|--------------------|------|------|
| 1. 原始输入只读，修复输出新目录 | 备份/修复/迁移三引擎：源只读打开；输出目录必须不存在且不得位于源内；失败清理输出，绝不覆盖 | `backup/engine.py`、`repair/engine.py:52-65`、`migration/engine.py`；测试含源目录快照相等断言 | ✅ |
| 2. 默认不上传数据 | 0.1.3 后复跑全 src grep：`requests/urllib/httpx/socket/urlopen/http(s)://` 0 命中；README「本地优先：默认不联网」 | grep 0 命中（第二轮复跑）；`README.md` | ✅ |
| 3. 不执行导入内容 | 复跑 grep：`eval/exec/subprocess/os.system/importlib/__import__/pickle` 0 命中；PNG 仅解析 tEXt 为 JSON；可执行/脚本扩展名 R3 隔离 | grep 0 命中；`safety.py`；`pngutil.py` | ✅ |
| 4. 不伪造数据，R0/R1/R2/R3 分级 | 四级 RepairLevel 枚举；R0 修复必须通过 json.loads 校验才采用；R2/R3 由扫描发现分级；R1 未实现属企划书已知限制 | `models.py:25-31`；`rules.py:54-67`；CHANGELOG 0.1.0 已知限制 | ✅（R1 待补=计划内限制） |
| 5. 每个动作有日志与差异报告 | 修复：repair-report.json + diffs/（前后 SHA-256、证据）；迁移：migration-report.json 逐项验证；备份：manifest + verify 报告 | `repair/engine.py`；`migration/engine.py` | ✅ |
| 6. 不删测试/不降断言/不硬编码 | 见 2.3：算术自洽、旧测试全保留、更新均为加强 | 2.3 节证据 | ✅ |
| 7. 先计划后修改，阶段完成停等验收 | 进程规则：每轮整改后有真实运行记录；本轮审核未执行 commit；创始人已执行验收相关首次 commit | AGENTS.md:33-34；CHANGELOG 各轮「真实运行」 | ✅ |
| 8. 无 NFT/代币/钱包/云端上传 | 复跑 grep：`NFT/token/wallet/钱包/代币/区块链/cloud/upload` 0 命中；README 边界声明排除加密资产 | grep 0 命中；`README.md` | ✅ |
| 9. 不猜字段，先建样本与兼容报告 | docs/format-compatibility.md 存在（置信度+未解决问题清单）；filetype 仅结构特征；未知字段原样保留写 sidecar | `format-compatibility.md`；`filetype.py`；`migration/engine.py` | ✅ |
| 10. 未实际运行的测试不得标通过 | 两轮均真实执行并记录输出；CHANGELOG 数字与真实运行一致 | 第 1 节两轮输出 | ✅ |

**结论：十项规则抽查无违例（0.1.3 变更文件复跑安全 grep 后仍然成立）。**

## 4. 已知风险与发现（第二轮更新）

| 编号 | 风险/发现 | 说明与建议 |
|------|-----------|-----------|
| R1 | ~~仓库 0 commit~~ **已解决** | 创始人已于 2026-11-06 22:19:31 完成首次 commit `1233289`；`continuity-studio-review.zip` 与 `_docx_text.txt` 已通过 .gitignore 新增规则排除，未入库 ✓ |
| R2 | **「测试例数」表述偏差（延续第一轮问题，未完全修正）** | 实测 105 collected = 104 passed + 1 skipped。CHANGELOG 0.1.3 表述准确；但 AGENTS.md 第 32 行「104 例」把 passed 数当总数（应写 105 例或「104 passed, 1 skipped」）；commit message「104 测试通过」同源偏差（已入库无法改）。第一轮建议的「99 passed, 1 skipped」措辞未被采纳。建议下次更新 AGENTS.md 时修正。 |
| R3 | 团队数字转述偏差 | 本轮任务转述「103 passed + 1 skipped」与实测（104 passed + 1 skipped）不符，验收决策请以本清单第 1 节真实运行记录为准。 |
| R4 | docs/TEAM-COORDINATION.md 有未提交修改 | lead 第二轮写作用域更新（11 行新增，含第二轮写作用域表与 Web UI 决策），属正常协作状态，需创始人后续一并 commit。 |
| R5 | `__version__` 仍为 0.1.0 | 0.1.1/0.1.2/0.1.3 为未发布整改版本，合理；发布时一并定版本号。 |
| R6 | 1 例符号链接测试在本沙箱跳过 | 环境限制（无法创建符号链接），conftest 已注明；建议创始人在完全权限环境补跑一次 `test_symlink_skipped`。 |
| R7 | R1 推断修复规则未实现 | 企划书已知限制，需真实样本；属下一阶段工作。 |
| R8 | `reports/` 包为占位（HTML 报告未实现） | 0.1.0 已知限制，属后续计划（本地 Web UI 线）。 |
| R9 | pytest 环境警告（第三方 anyio 插件 CallSpec2 更名） | 非本项目代码；pytest 10 升级时注意。 |

## 5. 验收结论汇总

| 验收项 | 实测结果 | 结论 |
|--------|----------|------|
| 阶段一至三交付物齐备（骨架/模型/扫描/备份恢复/修复/迁移/CLI） | 代码与文档齐备，见验收范围表 | 通过 |
| 完整 pytest 套件真实运行（0.1.3 基线） | **105 collected：104 passed, 1 skipped**, 1 warning, 1.65s, 退出码 0 | 通过 |
| 0.1.1 / 0.1.2 / 0.1.3 整改逐项落地 | 三轮共 7 个 P1 + 12 个 P2 全部核对对上；无删除测试/无降断言/无硬编码 | 通过 |
| 十条规则抽查（0.1.3 后复跑） | 无违例 | 通过 |
| Git 状态 | 首次 commit 1233289 已由创始人完成，内容与工作区一致（仅 TEAM-COORDINATION.md 待提交）；zip/派生文件已排除 | 通过（附 R2/R4 事项） |

**验收建议（一句话）**：可以验收——三轮审查整改（0.1.1–0.1.3）全部落地且测试真实通过（104 passed + 1 skipped），建议创始人顺手把 docs/TEAM-COORDINATION.md 的更新一并 commit，并将 AGENTS.md 的「104 例」修正为「105 例（104 passed + 1 skipped）」后即可进入下一阶段（本地 Web UI）。
