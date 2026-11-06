# 各 Agent 能力提升计划（team-capability-plan）

> 编制：researcher（Agent Teams，常驻资源与智慧中枢）｜ 日期：2026-11-07
> 目的：按创始人「常驻中枢」指令，逐成员给出可落地的能力增强建议。
> 每条标注：收益 / 成本 / 前置（**需创始人批准的事项单列**）。全部只建议、不实施；
> 引入工具/依赖一律走 AGENTS.md 审查流程；不引入与规则 8 冲突内容。
> 环境约束提醒：沙箱内 pip 不可用（纯 wheel 走 tools/fetch_wheels.py）、Node 可用性未验证、
> 浏览器仅创始人/QA 环境可用。

---

## 1. qa-reviewer（测试与审核者）

| 建议 | 收益 | 成本 | 前置 |
|---|---|---|---|
| **攻击样本库**（samples/attack/）：把提示词 9 的清单落成固定夹具——恶意 PNG（块长度越界/CRC 错/超大 tEXt/炸弹尺寸）、恶意 JSONL（截断/BOM/超深嵌套/超长行）、zip slip 包、符号链接、Unicode/空格路径、超大文件 | 三轮审核第 2 轮「真实执行攻击路径」有现成弹药，审核可复现、可回归 | 低（一次性编写 + 随案例库增补） | 写作用域：samples/ 目录落点需创始人确认 |
| **投毒脚本集**（tools/gen_malicious.py 类）：一键生成上述攻击样本 + 预期断言描述 | 审核不再手搓样本；与 failure-case-library 第 5 节联动 | 低-中 | 同上；属 developer/qa 写作用域协调 |
| Playwright MCP 接入（已列 resource-map Top 5） | 第 2 轮「攻击者视角」可在真实浏览器执行路径验证（不再是代码推断） | 中（配置一次） | **创始人批准 MCP 配置** |
| 审核清单模板化（每轮产出固定五段：执行证据/发现/与上轮比较/具体修改建议/结论） | 三轮审核一致性、创始人可读性 | 低 | 无 |
| 学习 resource-map §5 的 Sequential Thinking MCP | 复杂攻击链推理结构化 | 低 | **创始人批准** |

## 2. developer（后端/引擎/ST 插件）

| 建议 | 收益 | 成本 | 前置 |
|---|---|---|---|
| **mypy 类型检查**（纯 wheel，py3-none-any，fetch_wheels 可落地） | 引擎 200+ 行级别的类型安全；配合注释全覆盖（规则 6/11） | 低（配置一次，增量标注） | **创始人审查后入 .deps2** |
| **ruff**（纯 wheel）做复杂度/lint 门禁（per-file 复杂度上限、不可达代码检测） | 控制引擎复杂度、防「硬编码伪装」（规则 6） | 低 | **创始人审查** |
| **coverage.py**（纯 wheel）真实覆盖率门槛（如关键模块 ≥85%） | 三轮审核第 1 轮「真实测试」有量化依据 | 低 | **创始人审查** |
| hypothesis 属性测试（纯 wheel）用于扫描/修复引擎的输入空间测试 | 边界输入自动发现（截断 JSON、极端长度） | 中（学习成本） | **创始人审查** |
| ST 插件 JS 侧：Node 可用性实测（P2 前置门，st-plugin-plan 5.1）+ node:test 真跑 | 规则 10 的真实运行证据 | 低 | Node 实测结果报创始人 |
| 沙箱 ACL skill（diagnose-windows-sandbox-acl）遇到访问拒绝先跑 | 减少环境类排障时间 | 低 | 无 |

## 3. frontend-developer（Web UI 前端/i18n/设计系统）

| 建议 | 收益 | 成本 | 前置 |
|---|---|---|---|
| **浏览器截图工作流**（Playwright MCP 或创始人/QA 环境手动截图流）：每个组件变更产出 1024/768/390/320 四档截图对照（规则 10 窄屏要求） | 视觉回归有证据；与 frontend-redesign-brief 一致 | 中 | **MCP 批准**或 QA 环境协作 |
| 语义令牌集中维护脚本（单一 tokens.css 生成器，规则 10「语义令牌集中维护」） | 改一处全站生效；防令牌漂移 | 低 | 无 |
| open-claude-ui 的 tokens.css/pure.css 参考（resource-map §5.2） | Claude 设计规格快速对齐（claude-design-study 10 条） | 低 | **许可证核实后**方可引入 |
| i18n 词典完整性检查（Python 小脚本对比 zh/en JSON 键集合） | 双语不落键（创始人双语要求） | 低 | 无 |
| axe-core / 手动 WCAG 清单（对比度、焦点环、reduced-motion） | 无障碍验收可量化 | 低-中 | Node 可用性待定；手动清单可先行 |
| extract-design-system skill（resource-map §5.2） | 从 claude.ai 等站点抽令牌做参照（产出仅参考，勿商用专有资产） | 低 | **创始人批准 skill 安装** |

## 4. lead（总控/编排）

| 建议 | 收益 | 成本 | 前置 |
|---|---|---|---|
| GitHub MCP（resource-map Top 5-1）只读监控仓库/PR/Issue + Release 草稿 | 每阶段推送与问题跟踪自动化 | 中 | **创始人批准 + 只读令牌** |
| PROGRESS.md 半自动生成（从共享任务板导出表格骨架，lead 人工润色） | 看板更新频率提升（创始人指令：每轮更新） | 低 | 无（纯流程） |
| 看板任务模板化（每任务含：目标/验收标准/写作用域/依赖） | 减少派单歧义、减少写冲突 | 低 | 无 |
| 批次节奏固定化（沿用本次持续队列模式：每批简报+下批计划） | 团队吞吐可预期 | 低 | 无 |

## 5. 全体成员（通用）

| 建议 | 收益 | 成本 | 前置 |
|---|---|---|---|
| **代码注释标准**（规则 6/11）：每模块 docstring + 关键分支注释；注释与代码一致性由 qa 第 1 轮核查 | 后续 AI/人类接手成本大降 | 低（习惯养成） | 无（创始人已授权注释全覆盖） |
| 引用规范：所有调研/文档标注来源 URL + 日期 + 置信度（沿用 researcher 现有格式） | 可追溯、可复核 | 低 | 无 |
| MCP/技能清单（resource-map §5）：GitHub/Playwright/Filesystem/Fetch/Sequential Thinking | 按需取用 | 低-中 | **创始人批准后逐项配置** |
| 每批工作「先读 AGENTS.md 最新版 + 写作用域」双检查（文件可能被其他会话更新） | 防规则漂移与写冲突 | 低 | 无 |

---

## 6. 需创始人批准的事项清单（单列）

1. MCP 配置 Top 5（GitHub/Playwright/Filesystem/Fetch/Sequential Thinking）——只读优先、凭据仅环境变量。
2. 纯 wheel 工具入 .deps2：mypy、ruff、coverage.py（建议第一批）；hypothesis（第二批）。
3. samples/attack/ 攻击样本库目录落点（建议 samples/synthetic/ 下分 attack/ 子目录）。
4. Node 环境：沙箱内可用性实测结果上报；不可用则批准「JS 单测在创始人/QA 环境执行 + 证据留档」方案。
5. open-claude-ui 许可证核实与 vendoring 许可（核实后单独报批）。
6. extract-design-system skill 安装许可。

---

## 7. 来源与联动

- [resource-map.md](./resource-map.md)（§5 MCP/工具清单）、[st-plugin-plan.md](./st-plugin-plan.md)（§5.1/5.2 环境与验证）、
  [failure-case-library.md](./failure-case-library.md)（§5 样本设计输入）、[claude-design-study.md](./claude-design-study.md)、
  [frontend-redesign-brief.md](./frontend-redesign-brief.md)（规则 10）、AGENTS.md（规则 6/11、环境说明）
