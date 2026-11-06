# ST 插件上市投放计划（st-launch-plan）

> 编制：researcher（Agent Teams，常驻资源与智慧中枢）｜ 日期：2026-11-07
> 对象：docs/st-plugin-plan.md（developer 计划稿，选项 1 最小插件）的上市/投放/验收配套；
> 依据：[research-st-plugin.md](./research-st-plugin.md)、[marketing-copy.md](./marketing-copy.md)（模板 A–D）、
> [failure-case-library.md](./failure-case-library.md)（验收样本）、官方 [Writing Extensions](https://docs.sillytavern.app/for-contributors/writing-extensions/) 文档。
> 纪律：只出计划与文案、不写代码；规则 2/8；社区只读、不刷屏（企划书 4.4）。

---

## 1. 官方扩展收录要求细节（P4 验收与收录门槛）

来源：[Writing Extensions 官方文档](https://docs.sillytavern.app/for-contributors/writing-extensions/)（访问日 2026-11-06）。

| 官方要求 | 本项目落实点（对照 st-plugin-plan.md） |
|---|---|
| 开源 + 自由许可证（不确定用 AGPLv3 亦可） | 插件许可证待创始人定（st-plugin-plan 6.4-4）；**建议 MIT**（与「薄壳引导」定位一致、吸收面最大），README 与 manifest 双写 |
| 必须兼容最新 release 版本 | P4 承诺 + `minimum_client_version` 门槛 + 每 release 冒烟测试（research-st-plugin 第 4 节策略） |
| README 必须完整：安装说明、使用示例、功能列表 | st-plugin-plan 已排双语 README（~150 行）；本计划第 4 节给出大纲 |
| **依赖 server plugin 的扩展不被收录** | 选项 1 纯 UI 扩展天然满足（已明确不做 server 插件） |
| 提交渠道：联系官方团队进官方内容库 | 收录是「申请制」而非自动；上线顺序见第 3 节 |
| manifest 字段规范：display_name/author/js/css/version/auto_update/minimum_client_version 等 | P1 静态契约测试已覆盖 manifest schema |
| 官方最佳实践：只用 `getContext()`、禁存密钥于 extensionSettings、DOMPurify 转义 | st-plugin-plan 已逐条落实（薄壳原则、textContent 渲染、零密钥） |

> 补充风险：官方内容库收录存在**审核等待期与不确定性**（提交制、无 SLA），因此投放不能押注收录成功——
> 主渠道应是「内置安装器 URL 分发 + 社区帖 + GitHub Release」三线并行（见第 3 节）。

---

## 2. 分发渠道清单

| 渠道 | 方式 | 时机 | 备注 |
|---|---|---|---|
| GitHub Releases（主仓库或独立扩展仓库） | 发布 zip/文件夹 + 双语 README；ST 内置「Install from URL」直接贴 GitHub raw/zip URL | P4 验收后立即 | 零等待、可迭代；版本号与 release notes 双语 |
| ST 官方内容库（扩展商城） | 按官方要求申请收录 | GitHub 上线 + 社区反馈一轮后申请 | 审核期不可控；收录成功后是最大自然流量入口 |
| Discord（酒馆相关服务器） | 在允许的频道发布 + 求助帖价值回复（marketing-copy 模板 B） | 需创始人提供凭据（环境变量、只读） | 先读版规；不刷屏 |
| Reddit r/SillyTavernAI | 检查清单价值帖（模板 A，附插件与 Web UI 链接） | 需登录凭据或经创始人授权 | 版规自查；只发一次主帖 |
| 百度贴吧 / NGA | 中文案例科普帖（模板 C：「白屏也能救数据」角度） | 与中文社区调研节奏同步 | 遵守吧规 |
| 教程/博客类（GitCode、Foreverse 式教程生态） | 后续可产出「酒馆体检入门」教程文（外链回 GitHub） | 第 2 批投放（上线 1–2 周后） | 内容先行、链接在后 |

---

## 3. 发布节奏与文案（复用 marketing-copy.md 模板）

| 阶段 | 动作 | 复用模板 | 验收信号 |
|---|---|---|---|
| T0 上线前 | README 双语定稿（安装/使用/功能/隐私声明/能力边界「插件是入口不是引擎」） | README 首屏结构 | QA 三轮审核 P4 通过 |
| T1 上线日 | GitHub Release + 双语 release notes（What's new→谁需要→已知限制→反馈渠道） | 模板 D | 可安装、可启用 |
| T2 上线后 3–7 天 | Reddit/贴吧价值帖（「升级 ST 前 5 分钟自查清单」+ 插件入口） | 模板 A/C | 不刷屏、先贡献清单内容 |
| T3 上线后 1–2 周 | Discord 求助回应式推广 + 教程文 | 模板 B | 凭据渠道才做；无硬广 |
| T4 持续 | 官方内容库申请 + 每 ST release 兼容性复验与更新公告 | 模板 D | 收录结果或明确拒绝原因 |

**核心文案（插件面板/README 首句，双语）**：
- CN：「Continuity 体检：酒馆内的一键内存体检。深度检查、备份、恢复与迁移请打开本地 Web UI——数据不出你的电脑。」
- EN："Continuity Checkup: a one-click, read-only health peek inside the tavern. For deep scans, backups and migration open the local Web UI — your data never leaves your machine."

---

## 4. 创始人真机验收清单（对照 st-plugin-plan §6.2 补充细节）

> 五步验收：安装 → 启用 → 体检 → 唤起 → slash。以下在原 7 条基础上补充**通过标准、证据记录与边界用例**。

### 4.1 前置准备
1. 本机 ST ≥ `minimum_client_version`（待定值）；`python -m continuity.webui` 已运行（默认 8777）。
2. 准备三个验收样本（用**合成数据**，不用真实聊天，规则 9/2）：
   - 样本①：仅 header + 开场白的「疑似重置」聊天（对应 H2/CASE-01）；
   - 样本②：无 `integrity` 字段的旧格式聊天（对应 H1/CASE-13）；
   - 样本③：两张同名不同内容的角色卡（对应 H3/CASE-07）。

### 4.2 五步验收表（每步记录证据）

| 步骤 | 操作 | 通过标准 | 证据 |
|---|---|---|---|
| 1 安装 | 放入 `data/<user-handle>/extensions/continuity-st/`，扩展管理页出现「Continuity 体检」 | 列表可见、版本徽标正确 | 截图 |
| 2 启用 | 勾选启用；打开设置页改端口（如 8777）再改回 | 启用无报错；设置持久化（刷新仍在） | 截图 + 刷新复验 |
| 3 体检 | 分别打开样本①②③，点「一键体检」 | ①H2「疑似重置」②H1「旧格式提示（不误伤）」③H3「同名卡提示」；全部含「内存态初步提示，深度检查请打开本地 Web UI」字样 | 三次截图 |
| 4 唤起 | 点「打开本地 Web UI」；随后停掉服务再点一次 | 服务运行时新标签打开 8777 首页（无需输密钥）；停服时友好提示 | 截图 ×2 |
| 5 slash | 输入 `/continuity`；另在低版本/不支持环境看降级 | 命令触发面板；降级提示存在 | 截图 + 控制台 |

### 4.3 安全与边界审计（必须逐项过）
1. DevTools Network：**零外部出站请求**（仅本页与 127.0.0.1）；无 `localStorage`/密钥写入。
2. 控制台零报错、零警告刷屏。
3. **无写路径**：验收前后对 `data/` 目录取文件清单+mtime 快照对比，确认插件未改动任何文件。
4. 边界用例：无选中角色/群聊打开时面板给出安全提示不报错；窄窗口（390px）面板可读；ST 中英界面下文案正常。

### 4.4 验收产出
- 五步 + 审计的截图包（含时间戳）；创始人签字确认 → commit + GitHub 推送（凭据仅环境变量）。

---

## 5. 合规红线（投放与文案）

1. 不夸大：面板与所有文案保留「内存态初步提示」定位，R 级结论只由 Python 引擎给出（st-plugin-plan 1.2/2 已约束）。
2. 不承诺数据恢复魔法；H2「疑似重置」话术用「疑似/建议」措辞（R4 风险已列）。
3. 零外部请求、零密钥、零上传（规则 2）；插件代码内无任何云端 URL。
4. 无 NFT/代币/钱包/加密支付（规则 8）；插件免费、无广告、无遥测。
5. 社区礼仪：先读版规、先贡献价值（清单内容）再给链接；不私信轰炸；Reddit/Discord 等渠道待创始人凭据。
6. 隐私声明（README 双语）：本扩展不收集、不存储、不上传任何数据；只在本地内存中做只读检查。

---

## 6. 给创始人的 5 条投放决策建议

1. **许可证选 MIT**：官方收录要求自由许可证即可；MIT 与「薄壳引导、深度能力在 Web UI」的定位最匹配，且便于社区二次集成；如创始人倾向 AGPL-3.0（官方建议的稳妥项）亦无碍收录。
2. **先 GitHub Release、后官方收录**：收录有审核等待期，不押注；内置安装器 URL 分发先行，收录作为第二波自然流量。
3. **确认 `minimum_client_version` 取值**（建议 1.12.0 起，与数据目录迁移线一致），并在 README 写清「低于该版本请先升级」的引导文案。
4. **真机验收按本计划 4.2/4.3 执行**：五步 + 零出站审计 + 无写路径快照对比 + 合成三样本；验收证据留档（QA 三轮审核可复用）。
5. **社区首发节奏按 T1→T2→T3 逐步展开**，Reddit/Discord 渠道待创始人凭据授权；每渠道首帖先发「升级前自查清单」价值内容再附链接（模板 A/B/C）。

---

## 7. 来源与联动

- 官方：[Writing Extensions（收录要求/最佳实践）](https://docs.sillytavern.app/for-contributors/writing-extensions/)、[Server Plugins（排除依据）](https://docs.sillytavern.app/for-contributors/server-plugins/)
- 项目内：[st-plugin-plan.md](./st-plugin-plan.md)（§6.2/6.4 对照）、[research-st-plugin.md](./research-st-plugin.md)、[marketing-copy.md](./marketing-copy.md)、[failure-case-library.md](./failure-case-library.md)（验收样本来源）
- 投放合规：[TEAM-COORDINATION.md](./TEAM-COORDINATION.md)（凭据规则）、AGENTS.md（规则 2/8/10）
