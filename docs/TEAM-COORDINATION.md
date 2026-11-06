# TEAM-COORDINATION.md — 多会话协作板（仅协调用，非规则文件）

> 更新时间：2026-11-06
> 最高规则仍是 AGENTS.md；本文件只记录参与角色与写作用域，避免多会话写冲突。

## 参与者

- **创始人（人工）**：唯一验收人、唯一 Git commit 执行人。
- **外部开发者 AI 会话**：负责阶段一至三 + 0.1.1/0.1.2 审查整改（已完成，待创始人验收）。
- **Agent Teams 团队（lead 总控）**：
  - `lead`：总控/总策划——共享任务板、写作用域、与创始人对接验收。
  - `developer`：产品开发者——负责「本地 Web UI（提示词 8）」线。
  - `qa-reviewer`：测试与审核者——验收支持、每轮真实测试与规则审核。
  - `researcher`：调研者——SillyTavern 兼容性 / Web UI 技术选型 / 商业调研，只出报告。

## 写作用域约定（第一轮）

| 成员 | 本轮写作用域 |
|------|-------------|
| developer | 仅 `docs/webui-plan.md`；下一轮经创始人确认后：`src/continuity/webui/` 新目录 |
| qa-reviewer | 仅 `docs/acceptance-checklist.md` |
| researcher | `docs/research-sillytavern.md`、`docs/research-webui.md`、`docs/research-business.md` |
| lead | 本文件 `docs/TEAM-COORDINATION.md` |
| 外部开发者会话 | AGENTS.md 与核心模块（src/tests 现有代码） |

任何成员如需改动**他人写作用域内**的文件（尤其是现有核心模块），必须先在其计划中标注「需创始人协调」，经创始人裁决后方可执行。

## 通用约定

1. 每次开工前重读 AGENTS.md（可能被其他会话更新）。
2. 不执行 Git commit（由创始人执行）；不删除或降低测试；未真实运行的测试不得标记通过。
3. 每个阶段完成后停止，等待创始人验收。
4. 冲突无法自行解决时，以创始人裁决为准。
