# 验收清单 — 阶段一至三 + 0.1.1/0.1.2 外部审查整改

> 验收支持文档（qa-reviewer 独立审核，2026-11-06）
> 依据：AGENTS.md（最新版，54 行）、CHANGELOG.md、docs/TEAM-COORDINATION.md
> 审核人写作用域：仅本文件；未修改任何源码/测试/配置，未执行 git commit。

## 0. 验收范围梳理

| 阶段 | 交付物 | 依据 |
|------|--------|------|
| 阶段一（骨架+模型） | pyproject、AGENTS.md、统一数据模型（Pydantic：BundleManifest/ManifestEntry/修复等级枚举） | CHANGELOG 0.1.0、AGENTS.md |
| 阶段二（扫描+备份/恢复） | 只读扫描器、备份/恢复引擎（manifest+SHA-256、verify、原子恢复） | 同上 |
| 阶段三（修复+迁移） | 修复引擎（R0/R2/R3+diff 报告）、SillyTavern 适配器、迁移引擎+验证报告、CLI | 同上 |
| 0.1.1 整改 | 5 个 P1 + 4 个 P2（多卡迁移、原子恢复、完整性分数语义、报告脱敏、资源预算、备份竞态、PNG 校验、路径规范化、坏行保留） | CHANGELOG 0.1.1 |
| 0.1.2 整改 | 1 个 P1 + 4 个 P2（迁移覆盖完整性、坏行字节保留、PNG 流式读取、verify 清单外文件、stat 签名变化检测） | CHANGELOG 0.1.2 |

## 1. 真实测试执行记录（规则 10：必须实际运行）

**执行命令**（照抄 AGENTS.md「环境说明」，真实执行）：

```powershell
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = 'D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'
$env:TMP = 'D:\项目1agent角色平台\.tmp'; $env:TEMP = $env:TMP
& $py -m pytest -v
```

**真实输出摘要**（2026-11-06 22:09 运行，完整输出已核对）：

- Python 3.14.5（绝对路径解释器，非 PATH 存根）；pytest 9.2.0（.deps2）
- `collected 100 items`
- 各文件：test_adapter 13、test_backup_engine 20 通过+1 跳过、test_cli 7、test_filetype 11、test_manifest 15、test_migration 13、test_pngutil 5、test_repair 9、test_scan 6
- **结果：99 passed, 1 skipped, 1 warning in 1.74s，退出码 0**
- 1 skipped = `tests/test_backup_engine.py::test_symlink_skipped`——沙箱无法创建符号链接时的**环境条件跳过**（`pytest.skip` 包裹 OSError），非删除/禁用测试；
- 1 warning = 第三方 anyio pytest 插件 `PytestRemovedIn10Warning`（CallSpec2 更名），与本项目代码无关，不影响通过。

**与历史记录比对**：CHANGELOG 0.1.2 声明「99 passed, 1 skipped」→ 与本次真实运行**完全一致**。AGENTS.md「测试套件（99 例）」的表述与实测收集 100 项（99 通过 + 1 跳过）略有出入，建议 AGENTS.md 措辞更新为「99 passed, 1 skipped」（见风险 R2）。

**结论：通过**。证据：本次运行输出；命令与 pyproject 内置 `--basetemp=.tmp/pytest-basetemp2 -p no:cacheprovider` 一致，测试临时文件全部落在 `.tmp`（已 gitignore），工作区无 `.pytest_cache` 残留。

## 2. 0.1.2 整改核对

**Git 状态核对（只读命令，如实报告）**：

- `git log --oneline -20` → 空输出；
- `git status` → `On branch master / No commits yet`，全部文件 untracked；
- `git diff HEAD --stat` / `git diff HEAD` → `fatal: ... does not have any commits yet`。

即：**仓库尚无任何 commit**，不存在可做历史 diff 的基线。因此 0.1.2 整改增量无法用 git diff 验证，改由「CHANGELOG 声明 ↔ 现行代码/测试」静态交叉核对 + 审查快照一致性核对完成（方法差异已如实标注）。

**逐项核对结果**（0.1.2）：

| CHANGELOG 声明 | 代码证据（文件:行） | 测试证据 | 结论 |
|----------------|---------------------|----------|------|
| P1 无法读取/识别文件进入 unprocessed_files 且 coverage_complete=false | `src/continuity/migration/engine.py:262-264, 440-460`；CLI 警告 `cli.py:156-160` | `test_migration.py:142-160`（monkeypatch 模拟不可读，断言 coverage_complete False、未复制） | ✅ 落地 |
| P1 损坏 PNG 按字节保留进 damaged_files + 需人工确认清单，不混入常规附件 | `migration/engine.py:246-259`（原样复制+哈希复核+needs_review）；CLI `cli.py:161-164` | `test_migration.py:122-139`（字节相等断言） | ✅ 落地 |
| P2 坏行字节级保留：二进制逐行读取；`.original` 完整字节副本 + `.bad-lines.txt` 二进制索引 | `adapters/sillytavern.py:174-214`（rb 读取、bad_lines 保留原始字节）；`migration/engine.py:206-219` | `test_migration.py:104-119`（`original.read_bytes() == chat.read_bytes()` 字节级断言） | ✅ 落地 |
| P2 PNG 流式读取：IDAT seek 跳过、非 IDAT 逐块读+CRC 校验、元数据上限 | `pngutil.py:56-108`；适配器改用流式 `sillytavern.py:146` | `test_pngutil.py` 全部 5 例（流式/内存等价、截断、IHDR CRC、元数据上限、大 IDAT 跳过） | ✅ 落地 |
| P2 verify 清单外文件 = 完整性失败；restore 警告不恢复 | `backup/engine.py:322-329`（ok=False）、`288-292`（警告） | `test_backup_engine.py:112-118`（`assert not report.ok`） | ✅ 落地 |
| P2 stat 签名（大小+mtime 纳秒）前后比对 | `backup/engine.py:125-132, 191-202` | `test_backup_engine.py:121-135`（同长度改写检出、未变稳定） | ✅ 落地 |
| 新增反例测试 9 例 | —— | 上述 6 个测试点共 9 例（migration 3 + pngutil 5 + backup 2，含 parametrize 与既有断言强化） | ✅ 落地 |

**无删除测试 / 无降低断言 / 无硬编码伪装**：
- 测试数量算术一致：0.1.1 记录 90 passed + 1 skipped → 0.1.2 新增 9 例 → 99 passed + 1 skipped = 本次实测 100 收集。数量对得上，无删除；
- 全 tests 目录 grep：无 `assert True`、无占位断言、无空测试体；抽样通读 `test_migration.py`、`test_backup_engine.py`、`test_pngutil.py`，断言均为真实行为断言（字节相等、标志位、异常、清理验证）；
- 唯一 skip 是环境条件跳过（符号链接），且保留完整测试体（环境允许时会真实执行）。

**审查快照一致性**：`continuity-studio-review.zip` 内 46 个文件与当前工作区逐字节 SHA-256 比对**全部一致**（含 src/tests/AGENTS.md/CHANGELOG）——审查快照后无代码漂移。注：该 zip 是审查后快照，非 0.1.1→0.1.2 增量基线。

**结论：0.1.2（及 0.1.1）整改均已落地，无测试删除、无断言降低、无硬编码伪装。通过（方法备注：git 无提交历史，核对方式为静态交叉核对）。**

## 3. AGENTS.md 十条规则抽查

| 规则 | 检查内容与实测结果 | 证据 | 结论 |
|------|--------------------|------|------|
| 1. 原始输入只读，修复输出新目录 | 备份/修复/迁移三个引擎：源以只读方式打开；输出目录必须不存在且不得位于源内；失败清理输出目录，绝不覆盖 | `backup/engine.py:135-156, 223-242`；`repair/engine.py:52-65`；`migration/engine.py:112-121`；测试 `test_full_roundtrip`/`test_backup_restore_roundtrip` 均有源目录快照相等断言 | ✅ |
| 2. 默认不上传数据 | 全 src 无任何网络调用：grep `requests/urllib/httpx/socket/urlopen/http(s)://` 0 命中；README「本地优先：默认不联网」 | grep 结果；`README.md:13` | ✅ |
| 3. 不执行导入内容 | 全 src 无 `eval/exec/subprocess/os.system/importlib/__import__/pickle`；PNG 仅解析 tEXt 块为 JSON；可执行/脚本扩展名（.exe/.js/.html 等）一律 R3 隔离不解析 | grep 结果；`safety.py`；`pngutil.py`；`scan.py:53-63` | ✅ |
| 4. 不伪造数据，R0/R1/R2/R3 分级 | `models.py` 定义四级 RepairLevel；`rules.py` 仅实现 R0-001/R0-002，且修复文本**必须通过 json.loads 校验才采用**（否则返回 None 不修复）；R2/R3 由扫描发现分级；R1 未实现但已文档化为已知限制（需真实样本） | `models.py:25-31`；`rules.py:54-67, 99-100`；CHANGELOG 0.1.0 已知限制 | ✅（R1 待补=计划内限制） |
| 5. 每个动作有日志与差异报告 | 修复：repair-report.json + diffs/*.diff（含前后 SHA-256、证据）；迁移：migration-report.json 逐项验证；备份：manifest.json + verify 报告 | `repair/engine.py:101-120, 144-148`；`migration/engine.py:292-294` | ✅ |
| 6. 不删测试/不降断言/不硬编码 | 见第 2 节：数量算术一致、无占位断言、抽样通读为真实断言 | 第 2 节证据 | ✅ |
| 7. 先计划后修改，阶段完成停等验收 | 进程规则：AGENTS.md「当前状态」明确停等创始人验收；本轮审核未执行任何 commit；CHANGELOG 每轮记录「真实运行」数字 | AGENTS.md:33-34；CHANGELOG | ✅ |
| 8. 无 NFT/代币/钱包/云端上传 | 全 src grep `NFT/token/wallet/钱包/代币/区块链/cloud/upload` 0 命中；README 边界声明排除加密资产 | grep 结果；`README.md:76` | ✅ |
| 9. 不猜字段，先建样本与兼容报告 | `docs/format-compatibility.md` 存在（含置信度、未解决问题清单）；`filetype.py` 仅结构特征识别；未知字段原样保留写 sidecar | `format-compatibility.md`；`filetype.py`；`migration/engine.py:266-274` | ✅ |
| 10. 未实际运行的测试不得标通过 | 本次全套真实执行（1.74s），CHANGELOG 记录数字与真实运行一致 | 第 1 节输出 | ✅ |

**结论：十项规则抽查无违例。** 其中 R1 推断修复未实现属于企划书明确记载的已知限制（需真实样本），非规则违例；第 9 条「遇到格式不确定先建样本和兼容性报告」已以合成样本 + 兼容矩阵落实。

## 4. 已知风险与发现

| 编号 | 风险/发现 | 说明与建议 |
|------|-----------|-----------|
| R1 | **Git 仓库 0 commit，全部文件未跟踪** | 创始人首次 commit 将是全量快照。`continuity-studio-review.zip` 与 `_docx_text.txt`（企划书提取文本）目前会随 `git add .` 进入仓库，建议 commit 前加入 .gitignore 或移出仓库目录。 |
| R2 | AGENTS.md「测试套件（99 例）」表述与实测不符 | 实测收集 100 项（99 passed + 1 skipped）。建议改为「99 passed, 1 skipped」。 |
| R3 | `__version__` 仍为 0.1.0 | 0.1.1/0.1.2 为未发布整改版本，合理；commit 时可一并决定版本号。 |
| R4 | 1 例符号链接测试在本沙箱跳过 | 环境限制（无法创建符号链接），conftest 已注明；建议创始人在完全权限环境补跑一次 `test_symlink_skipped`。 |
| R5 | R1 推断修复规则未实现 | 企划书已知限制，需真实样本；不影响阶段一至三验收，属下一阶段工作。 |
| R6 | `reports/` 包为占位（HTML 报告未实现） | 0.1.0 已知限制，属后续计划（本地 Web UI 线）。 |
| R7 | pytest 环境警告（第三方 anyio 插件 CallSpec2 更名） | 非本项目代码；pytest 10 升级时注意。 |

## 5. 验收结论汇总

| 验收项 | 实测结果 | 结论 |
|--------|----------|------|
| 阶段一至三交付物齐备（骨架/模型/扫描/备份恢复/修复/迁移/CLI） | 代码与文档齐备，见验收范围表 | 通过 |
| 完整 pytest 套件真实运行 | 99 passed, 1 skipped, 1 warning, 1.74s, 退出码 0 | 通过 |
| 0.1.1 / 0.1.2 整改逐项落地 | 静态交叉核对全部对上，无删除测试/无降断言/无硬编码 | 通过 |
| 十条规则抽查 | 无违例 | 通过 |

**验收建议（一句话）**：可以验收并 commit——测试真实全通过、两轮整改逐项落地、十条规则无违例；建议创始人 commit 前仅处理一件事：把 `continuity-studio-review.zip` 与 `_docx_text.txt` 加入 .gitignore 或移出仓库，再执行首次提交。
