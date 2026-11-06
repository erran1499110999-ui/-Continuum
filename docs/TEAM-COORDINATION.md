# TEAM-COORDINATION.md — 多会话协作板（仅协调用，非规则文件）

> 更新时间：2026-11-06
> 最高规则仍是 AGENTS.md；本文件只记录参与角色与写作用域，避免多会话写冲突。

## 参与者

- **创始人（人工）**：唯一验收人、唯一 Git commit 执行人。
- **外部开发者 AI 会话**：负责阶段一至三 + 0.1.1/0.1.2 审查整改（已完成，待创始人验收）。
- **Agent Teams 团队（lead 总控）**：
  - `lead`：总控/总策划——共享任务板、写作用域、与创始人对接验收。
  - `developer`：产品开发者——后端（server/api/jobs/validation/views/history）与 **ST 插件（当前最高优先级）**。
  - `frontend-developer`：前端开发者——Web UI 前端（static/、i18n/双语、设计系统、风格预览页）；字体/按键/交互严格参照 Claude 网页端。
  - `qa-reviewer`：测试与审核者——验收支持、每轮真实测试与规则审核、**注释正确性审查**。
  - `researcher`：调研者兼【产品经理/商业策划/推广文案】——技术+商业+社区调研、产品可行性与商业性规划、宣传推广与文案设计、资源地图与设计案例（Claude 等）；只出报告与方案，不落地代码。

## 写作用域约定（第一轮）

| 成员 | 本轮写作用域 |
|------|-------------|
| developer | 仅 `docs/webui-plan.md`；下一轮经创始人确认后：`src/continuity/webui/` 新目录 |
| qa-reviewer | 仅 `docs/acceptance-checklist.md` |
| researcher | `docs/research-sillytavern.md`、`docs/research-webui.md`、`docs/research-business.md` |
| lead | 本文件 `docs/TEAM-COORDINATION.md` |
| 外部开发者会话 | AGENTS.md 与核心模块（src/tests 现有代码） |

任何成员如需改动**他人写作用域内**的文件（尤其是现有核心模块），必须先在其计划中标注「需创始人协调」，经创始人裁决后方可执行。

## 写作用域约定（第二轮，创始人 2026-11-06 已裁决）

| 成员 | 本轮写作用域 |
|------|-------------|
| developer | `src/continuity/webui/`（全新目录）+ `tests/test_webui_server.py`、`tests/test_webui_jobs.py`、`tests/test_webui_validation.py`（全新文件，创始人已批准「方案甲」：tests/ 下新增、绝不改旧文件） |
| qa-reviewer | `docs/acceptance-checklist.md`（0.1.3 增量复核修订） |
| researcher | 本轮待命 |
| 外部开发者会话 | 创始人裁决：由其负责 SillyTavern V3/CHARX/1.12+ 布局兼容性更新（`src/continuity/adapters/` 等核心代码），输入文档 `docs/research-sillytavern.md` 第 9 节 P0 清单 |

已裁决的技术决策：Web UI 技术栈 = **方案 A（纯标准库 ThreadingHTTPServer + 无构建原生 JS，零新增依赖）**；入口 `python -m continuity.webui`；默认端口 8765；历史记录 `.tmp/webui-history.jsonl`（正式回退 %LOCALAPPDATA%）。

## 写作用域约定（第三轮，W2：创始人已验收 W1 并授权）

| 成员 | 本轮写作用域 |
|------|-------------|
| developer | `src/continuity/webui/`（继续，新增扫描页 + `POST /api/jobs/scan` 端点）+ `tests/test_webui_api_scan.py`（全新文件，方案甲） |
| qa-reviewer | `docs/w2-acceptance.md`（W2 独立审核） |
| researcher | 待命（可按需深挖 SillyTavern 样本验证，不写代码） |
| 外部开发者会话 | 继续 V3/CHARX/1.12+ 兼容性更新（核心代码），与本团队 webui 无重叠 |

## 创始人新指令（2026-11-06 22:48，自 W2 起生效）

1. **三轮审核制（严格模式，创始人 2026-11-06 强化）**：developer 每完成一次大任务（一个 W 阶段）→ qa-reviewer 三轮独立审核：
   - 第 1 轮「功能与真实测试」：真实运行全套 pytest；**逐行审查代码正确性**；
   - 第 2 轮「安全与十规则审计」：攻击者视角**真实执行攻击路径**验证可行性（不能只看代码推断），对照提示词 9；
   - 第 3 轮「回归与发布审查」：全量回归、**与阶段目标差距清单**、发布准备核查，对照提示词 10。
   **每一轮必须与上一轮结果比较、指明具体修改建议**；问题退回 developer 修复后复审；三轮全过才提交创始人验收。
2. **GitHub 按阶段上传**：每阶段创始人验收通过后，按阶段推送到 `https://github.com/erran1499110999-ui/-Continuum.git`（origin 已配置）。推送凭据仅存环境变量/凭据管理器，绝不写入源码或日志。
3. **仓库产品描述中英文双语**：README.md 等对外产品描述需中英双语。README 更新涉及外部开发者写作用域，须创始人协调排期。
4. **企划书变更跟踪**：基线 = `docs/plan-docx-text.txt`（提取自创始人 docx 原件，与 `_docx_text.txt` 内容一致）。创始人更新企划书后，lead 重新提取并与基线 diff，把变更同步到任务与本文档。
5. **调研者社区调研**：可对 X（Twitter）、Reddit、百度贴吧等社区做真实产品调研；优先公开渠道（无需登录的公开页面/帖子，只读、不发言、不刷屏）；如需登录凭据由创始人提供，仅存环境变量，只读使用。

## 创始人新指令（2026-11-07 凌晨）

1. **透明度**：lead 维护 `docs/PROGRESS.md`（通俗进度看板，中英双语），每轮更新；创始人可随时查阅。所有对外汇报用通俗语言解释关键信息与步骤。
2. **调研者升级**：兼产品经理/商业策划/推广文案——把调研与产品可行性、商业性、系统性规划结合；产出推广、广告词、文案设计（中英双语）；拓展消息来源（学术论文 arXiv、开源项目、成熟产品、行业媒体、多语言社区等）。
3. **UI 现代化重设计 + 多语言**：Web UI 需交互性强、时尚、前沿，参考国外主流科技网站（Linear/Vercel/Stripe 等）的现代主义设计风格，建立明确美学基调与设计系统；多语言支持（先中英）并入 W3 完成。
4. **ST 插件战略定位**：插件与网站是一个整体——插件是获客入口（敲门砖），在酒馆内做轻量体检提示并引导到本地 Web UI；深度功能与付费路径都在 Web UI/引擎侧。
5. **资源整合（不闭门造车）**：结合一切可用资源——开源代码、成熟产品、学术成果，建立资源地图与借鉴清单（遵守许可证与依赖审查流程；不得引入与规则 8 冲突的内容）。

## 通用约定

1. 每次开工前重读 AGENTS.md（可能被其他会话更新）。
2. 不执行 Git commit（由创始人执行）；不删除或降低测试；未真实运行的测试不得标记通过。
3. 每个阶段完成后停止，等待创始人验收。
4. 冲突无法自行解决时，以创始人裁决为准。
