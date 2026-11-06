# Continuity Studio 外部审查说明（给 ChatGPT / 审查者）

> 本文件与代码一起打包，供外部 AI（如 ChatGPT）审查使用。
> 项目依据：《AI 角色连续性平台商业企划书 v1.0（2026-11-06）》（原文提取件是否随包由创始人决定，见「隐私说明」）。
> 版本：2026-11-07 更新（此前 0.1.1/0.1.2/0.1.3 三轮外部审查均基于本文件旧版；本版覆盖当前全量代码）。

## 一、项目一句话

本地优先的 AI 角色备份、诊断、修复与迁移工具（Continuity Studio），
首个适配客户端 SillyTavern。当前已交付：核心 Python 引擎 + CLI 七命令、
本地 Web UI（扫描/备份/急救备份/恢复端点 + 前端）、SillyTavern 扩展插件
（P1–P5：内存态体检 + 唤起 + 深链引导）。

> **外部审查历史**：0.1.1 修复第一轮审查的 5 P1+4 P2；0.1.2 修复第二轮审查的
> 1 P1+4 P2；0.1.3 修复第三轮审查的 1 P1+4 P2（详见 CHANGELOG）。
> 请重点复核：历轮修复是否到位、当前新增代码（Web UI / 插件 / 前端）是否引入新回归。

## 二、建议的审查清单（请逐项给出结论与证据）

1. **功能完整性**：CLI 七个命令（scan / backup / restore / verify / repair / migrate / version）
   与 Web UI 端点（/api/health、/api/version、/api/ping、/api/jobs/{scan,backup,emergency-backup,restore}、
   /api/jobs/<id>）是否实现完整、互相自洽；插件（体检 H1–H5、唤起、深链）与前端（hash 路由
   #emergency/#backup/#restore）三方契约是否一致。
2. **安全规则合规**（对照 AGENTS.md 十项不可违反规则）：
   - 原始文件只读，修复/迁移/恢复只写新目录（backup/engine.py、repair/engine.py、migration/engine.py）；
   - 不执行导入内容（R3 隔离）——检查 adapters/sillytavern.py、repair/engine.py、插件 index.js（textContent 渲染）；
   - 防路径穿越（backup/engine.py 的 safe_join、webui/server.py 静态服务 resolve 二次校验）、大小上限、符号链接跳过；
   - 不伪造数据（R0/R1/R2/R3 分级）——检查 repair/rules.py；
   - 未知字段绝不静默丢弃（migration/engine.py 的 sidecar 与 unsupported 清单）；
   - 插件侧：零外部网络（仅 127.0.0.1）、零密钥、无 staging 依赖、restore 深链永不自动执行。
3. **数据完整性**：manifest schema（Pydantic 校验 + SHA-256）、备份恢复逐文件哈希校验、
   急救备份的 verify 联动自检、迁移后逐项验证与完整性分数的分母解释是否严谨。
4. **测试质量**：tests/ 覆盖是否充分、断言是否有效（防止"删测试过验收"）；
   本项目真实测试结果：**401 collected = 400 passed + 1 skipped**（跳过的 1 例是
   Windows 符号链接权限，属环境限制，测试内已处理）；另有 node:test 24 例（插件纯函数单测）。
   均在 Python 3.14.5 下真实执行通过（QA 留档）。逐文件基线见下表。

## 测试基线清单（2026-11-07，供逐项比对）

以下为随包版本的真实收集数（`python -m pytest --collect-only`，本机 Python 3.14.5）：

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
| tests/test_st_plugin_static.py | 53 |
| tests/test_webui_api_backup.py | 20 |
| tests/test_webui_api_scan.py | 16 |
| tests/test_webui_frontend_static.py | 141 |
| tests/test_webui_jobs.py | 8 |
| tests/test_webui_server.py | 22 |
| tests/test_webui_validation.py | 36 |
| **pytest 合计** | **401（运行结果 400 passed + 1 skipped）** |
| extensions/sillytavern/tests/checks.test.mjs（node:test） | 24（沙箱内以 `node <file>` 单进程执行，官方 `node --test` 被沙箱禁 spawn 报 EPERM） |

5. **代码质量**：模块划分（scanners/backup/repair/adapters/migration/webui 分层）、
   适配器架构、错误信息是否面向用户、文档与注释是否与实现一致（AGENTS.md 第 6/11 条：注释强制）。
6. **与企划书的偏差**（已知、有意为之，请评估是否合理）：
   - R1 可推断修复规则尚未实现（需真实样本；仓库只有合成样本）；
   - 仅支持 SillyTavern 一个客户端适配器（RisuAI 等为后续）；
   - 独立 HTML 报告尚未实现（Web UI 展示层已上线，报告 JSON 落盘已有）；
   - 文本识别仅支持 UTF-8；聊天附件内嵌引用检测未实现；
   - 插件定位为「薄壳入口」，深度功能在本地 Web UI/引擎（见 docs/st-plugin-plan.md）。

## 三、项目结构速览

```
src/continuity/
  models.py        # Pydantic 数据模型（BundleManifest、修复等级 R0-R3、文件类型）
  limits.py        # 统一资源预算（单文件/累计字节/文件数/深度/行数/PNG 上限）
  safety.py        # 可执行/脚本扩展名清单（R3 隔离依据）
  pngutil.py       # PNG 流式块读取（IDAT 增量 CRC，0.1.3）
  scanners/        # 只读扫描：filetype.py（类型识别）、scan.py（目录扫描+发现分级）
  backup/          # 备份/恢复引擎（manifest+SHA-256、safe_join 防穿越）+ verify
  repair/          # 修复引擎（rules.py：R0-001 尾逗号、R0-002 BOM；engine.py：修复副本+diff）
  adapters/        # SillyTavern 适配器（角色卡 V1/V2、PNG/JSON、聊天 JSONL、世界书）
  migration/       # 迁移引擎（导出+逐项验证+完整性分数+sidecar）
  webui/           # 本地 Web UI（server.py 路由/安全头/token、api.py 端点、
                   #   jobs.py 串行任务队列、validation.py 入参预检、views.py 序列化、
                   #   history.py 本地历史、static/ 前端三件套）
  cli.py           # 命令行入口（7 个命令）
extensions/sillytavern/continuity-st/
  manifest.json    # 插件清单（display_name「Continuity 体检」、min 1.12.0、MIT）
  index.js         # 插件入口（P1 骨架/P2 体检/P3 唤起+slash/P4 版本提示/P5 深链+ping 探测）
  checks.js        # H1–H5 内存态体检纯函数（hint 级话术，绝不产出 R 级判定）
  settings.html    # 设置页（Web UI 端口 + 提示开关，无密钥字段）
  style.css / README.md（双语）/ package.json（type=module）
  tests/checks.test.mjs   # node:test 24 例（假 context，无真实用户数据）
preview/style-preview.html  # 前端风格预览页（v2 演示，不参与产品运行）
tools/fetch_wheels.py       # 开发用纯 wheel 下载器
tests/                      # pytest 16 文件（基线见上表）
samples/synthetic/          # 合成样本生成器（不含任何真实用户数据）
docs/                       # 计划/调研/验收档案（见下）
```

## 四、本地复跑（可选，审查者可验证）

要求 Python 3.11+（开发机为 3.14.5），依赖：pydantic>=2、pytest>=8（开发时解压于 .deps2，未随包提供；
审查者可自行 `pip install pytest`）。插件 JS 单测需 Node ≥ 18。

```bash
PYTHONPATH=src python -m pytest          # Windows PowerShell: $env:PYTHONPATH="src"; python -m pytest
node extensions/sillytavern/tests/checks.test.mjs   # 24 例（沙箱替代执行方式）
python -m continuity.cli scan samples/synthetic/out
python -m continuity.cli backup samples/synthetic/out ./demo-bundle
python -m continuity.cli verify ./demo-bundle
python -m continuity.cli restore ./demo-bundle ./demo-restored
python -m continuity.cli repair samples/synthetic/out ./demo-fixed
python -m continuity.cli migrate samples/synthetic/out ./demo-migrated
python -m continuity.webui --no-browser      # 本地 Web UI（默认端口 8777）
```

> 注意：本开发环境为受限沙箱，pytest 的 basetemp 与 cacheprovider 适配写在 pyproject.toml
> 与 tests/conftest.py 注释中；在普通环境下这些设置无害，无需移除。

## 五、团队规则与内部审查档案（供审查者对照）

- **AGENTS.md 现行规则要点**（第 6–13 条为 2026-11-06/07 新增）：注释强制且注释由审核者审查；
  外部资源利用须经许可证审查；前后端分工（frontend-developer 管前端/设计系统，developer 管后端与插件）；
  ST 插件为最高优先级（三轮审核 + 创始人真机验收）；前端改版以 docs/frontend-redesign-brief.md 为权威规范
  （宋体标题禁楷体/无装饰动画/语义令牌/窄屏 1024·768·390·320）；代码注释全覆盖；各角色思维要求
  （qa-reviewer 以审判官模式：假设一切有罪直到证据确凿）；投放前置验证——市场验证经创始人确认前不发布。
- **已完成内部审查档案**（docs/ 下，可逐份对照外部审查发现）：
  `acceptance-checklist.md`（阶段一至三 + 0.1.1–0.1.3）、`w1-acceptance.md`、`w2-acceptance.md`、
  `reaudit-w1w2.md`（严格复审 + 修复复审）、`frontend-v2-acceptance.md`（风格预览 v2）、
  `redesign-acceptance.md`（产品页正式改版）、`p1-acceptance.md`–`p5-acceptance.md`（插件 P1–P5）、
  `comment-review.md`（全量注释补全审查）、`validation-verdict.md`（市场验证报告独立裁决：
  conditional-go 维持、投放冻结）。
- **市场状态**：投放已冻结（AGENTS.md 第 13 条）；市场验证四条件（真机 5–10 人复用率、
  授权样本 ≥3、付费信号 ≥2、移动端访谈）未达成前不发布。

## 六、隐私说明

本包内**不含任何真实用户数据**：所有样本均由 samples/synthetic/make_samples.py
与 tests/helpers.py 程序化生成。如打包方案中包含企划书原文提取件（business-plan-text.txt），
是否分享给外部 AI 由创始人决定（本文件旧版已注明可自行删除后再上传）。
开发环境的 .tmp/、.deps2/、__pycache__/ 与私有文件一律不随包提供。

## 七、给审查者的额外提问（欢迎超出清单）

- 是否存在会导致数据损坏或静默丢失的边界情况？
- 完整性分数的计算与解释是否可能误导用户？
- 插件「内存态初步提示」话术是否足以防止用户误读为全量健康？
- Web UI 与插件深链（#emergency/#backup/#restore + auto 白名单）是否存在可被恶意网页利用的路径？
- 下一个阶段（本地 Web UI W3 起 / 插件官方收录）最值得优先解决的技术风险是什么？
