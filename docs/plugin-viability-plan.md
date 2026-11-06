# 插件自身可行性方案 + 插件↔网页关系重构（plugin-viability-plan）

> 编制：researcher（Agent Teams，哲学家/产品经理视角）｜ 日期：2026-11-07
> 触发：创始人指令「先不管网页端，把插件本身做成可行的产品；插件与网页的关系批判得不够清楚，需要重构清楚」。
> 本计划只出方案与接口契约建议、不写代码；backend 变更由 developer 按写作用域执行。
> 依据：[st-plugin-plan.md](./st-plugin-plan.md)（§6.3 token 模型）、[research-st-plugin.md](./research-st-plugin.md)（三选项）、
> [product-useless-diagnosis.md](./product-useless-diagnosis.md)（MVP-loop）、[failure-case-library.md](./failure-case-library.md)。

---

## 1. 关系批判（诚实，不绕）

- **现状**：插件 = 六项内存提示 + 「打开本地 Web UI」按钮 → 用户落在一个**只会扫描的首页**。
  于是出现「两张皮，两边都不可行」：插件皮——只有提示没有结果；网页皮——只有扫描没有救治。
  用户从插件到网页完成了一次「空转」。
- **对「薄壳=只给链接」的批判**：薄壳原则（逻辑留在引擎）本身没错，错在把薄壳做成了「链接分发器」。
  **薄壳的正确形态是「一键启动一个有结果的救数据动作」，而不是「给出一个网址」**。链接是死的，
  动作是活的；用户要的是结果（备份包生成、聊天找回），不是导航。
- **关系重构后的定义（一句话）**：
  - 插件 = **遥控器**：在酒馆内识别「该救数据了」的时刻（出事/升级前），一键**启动**对应工作流；
  - 网页版 = **执行与结果**：工作流页面自动开始、展示进度与结果（备份包、恢复报告）；
  - 一体 = 用户感知为**一次动作**：插件按下 → 网页自动跑完 → 结果呈现。中间没有「探索」环节。
- 与创始人「先不管网页端」的关系：网页首页的「装修」继续搁置，但网页的**工作流页**（急救备份/恢复）
  是插件可行性的必要条件——**「先不管网页端」= 不管首页美观，不是不做工作流页**。本计划把网页端
  工作流页定义为实现插件的后端能力载体（W3'/W4' 的 API 化，见第 4 节）。

---

## 2. 三条价值路径对比（证据与取舍）

### 路径 A：深链引导式（推荐）
- 机制：插件按钮 → `window.open("http://127.0.0.1:8777/#w=emergency&auto=1")` → 网页端工作流页
  加载后**自动开始**（页面从服务器注入的 meta token 自认证，插件不接触 token）→ 10 分钟内出结果。
- 证据/优点：
  - token 安全模型**完全不变**（st-plugin-plan §6.3 原设计：token 由服务器注入首页 meta，页面自取自用）；
  - 深链参数只带路由与 auto 标记，**不携带任何密钥**——恶意网页即使打开深链也拿不到数据
    （跨域无法读响应、无 CORS、无 token）；
  - 改动最小：插件 P3 唤起逻辑改路由即可；后端新增 ping + 三个工作流 API（见第 4 节）；
  - 绕开「只会扫描的首页」，直达 W3'/W4' 工作流——直接修复 product-useless-diagnosis 的闭环断裂。
- 取舍：插件面板内不显示进度（进度在网页端）；依赖浏览器允许弹窗（用户需允许 popup 或插件提示点击）。

### 路径 B：面板内嵌 API
- 机制：插件面板直接 fetch `127.0.0.1:8777` 的 API，在酒馆内展示进度与结果。
- 证据/缺点：
  - 需要 `/api/ping` 免 token + CORS 白名单（ST 页面源）+ token 方案重设计（token 如何安全交到插件：
    插件无安全存储，extensionSettings 明文对所有扩展可见——官方明令禁存密钥）；
  - 安全面扩大（跨域 API + 密钥流转），与「插件零密钥」原则冲突；
  - nat20-bridge 先例证明可行（CORS permissive loopback），但其 bridge 无敏感数据；我们的 API 是
    **数据操作接口**（备份/恢复），风险等级不同。
- 取舍：体验最深（面板内看进度），但安全复杂度最高；**作为选项 2 阶段再评估**（research-st-plugin 原结论一致）。

### 路径 C：Server 插件（真·独立备份）
- 机制：server 插件碰文件系统，可在无网页端时独立备份。
- 证据/缺点：官方**无沙箱警告**、官方内容库**不收录**依赖 server 插件的扩展、安装摩擦大
  （st-saves 需改 config.yaml + npm install 的教训）、与「本地优先可信人设」冲突；
  且创始人指令「先不管网页端」≠「网页端消失」——A 路径已经让插件在网页端缺位时也能引导启动。
- 取舍：仅在「要求插件完全脱离网页端独立完成备份」时成立；**本计划不推荐、默认不做**，列待决策。

### 推荐：路径 A
理由：以最小安全面改动（免 token ping + 三个复用引擎的 API）实现「插件一键 → 有结果的救数据动作」，
闭环修复彻底；B/C 的增量体验不值得其安全与安装成本（在 MVP-loop 未验证前）。

---

## 3. 插件自身可行性功能清单（P5，原 P3 唤起模块的升级版）

| # | 功能 | 插件侧实现 | 依赖的后端端点 | 用户结果 |
|---|---|---|---|---|
| P5-1 | **出事急救入口**（误删/白屏/升级后异常，对应案例 CASE-10/14/02） | 面板主按钮「立即抢救数据」→ 深链 `#w=emergency&auto=1` | `POST /api/jobs/emergency-backup`（自动探测 data 目录）+ 引导至恢复 | 10 分钟内生成急救备份包或完成找回引导 |
| P5-2 | **升级前备份提醒 + 一键备份**（对应 CASE-13/16） | 检测到聊天异常线索（H1/H2）或用户主动点击 → 深链 `#w=backup&auto=1` | `POST /api/jobs/backup` | 升级前拿到完整备份 + 可恢复性自检报告 |
| P5-3 | **服务未运行检测**（零 CORS 技巧） | `new Image().src = "http://127.0.0.1:8777/api/ping"`（onload/onerror 判断）；未运行则展示启动指引（复制 `python -m continuity.webui`） | `GET /api/ping`（免 token，仅 `{"status":"ok"}`） | 不再出现「点了没反应」；未启动也能自助 |
| P5-4 | **进度与结果展示** | 插件仅 toast「已在网页版打开【急救备份】，自动开始中」；进度/结果全部在网页工作流页 | 工作流页轮询 `GET /api/jobs/{id}` | 用户看到任务完成 + 结果路径（不出酒馆也能感知状态） |
| P5-5 | 内存态提示（保留 H1–H6） | 不变 | 无 | 触发「该救数据了」的时刻识别 |

- P5 相对原 P3 的差异：唤起目标从「首页」改为「工作流深链 + auto 启动」；新增 ping 检测；
  「打开」升级为「启动一个动作」。其余薄壳原则不变（不碰文件、零密钥、零外部 URL——深链仅 127.0.0.1）。

---

## 4. 后端 API 最小集合（供 developer 实现；引擎函数已存在）

| 端点 | 方法 | 鉴权 | 说明 |
|---|---|---|---|
| `/api/ping` | GET | **免 token**（待创始人批准） | 仅返回 `{"status":"ok"}`；无数据、无副作用；用于插件存活探测 |
| `/api/jobs/emergency-backup` | POST | 现有 token 校验 | 自动探测 ST data 目录（依据 USER_DIRECTORY_TEMPLATE，含多用户句柄）→ 调引擎备份函数 → 返回 job id |
| `/api/jobs/backup` | POST | 现有 token 校验 | 显式目标目录备份（W3' 形态）→ job id |
| `/api/jobs/restore` | POST | 现有 token 校验 | 从本产品备份包/指定目录恢复 → **输出新目录**（规则 1）→ job id + 校验报告 |
| `/api/jobs/{id}` | GET | 现有 token 校验 | 任务进度/结果轮询（沿用 W2 scan 任务模式） |

- 纪律：全部复用引擎函数（backup/restore/scan 已有实现）；token 校验与现有端点一致；
  restore 绝不覆盖源（写作用域纪律 = 现有引擎约定）；API 化由 developer 在 W3'/W4' 中实施，
  属 backend 写作用域，本计划只提供契约。
- 深链安全模型（重申）：`#w=...&auto=1` 不含 token；工作流页自服务器 meta 取 token 后自动开始；
  无 token 页面拒绝自动开始并提示刷新。

---

## 5. 风险与待创始人批准清单

| # | 事项 | 评估 | 状态 |
|---|---|---|---|
| 1 | `/api/ping` 免 token | 无数据无副作用；任何网页可用 img 标签探测本地服务存活（无信息泄漏，但属「本地服务存在性探测」面扩大）——建议加 **Host 白名单校验**（仅 127.0.0.1:8777/localhost:8777）后批准 | **待创始人批准** |
| 2 | 深链被恶意网页滥用 | 深链无密钥；恶意页可「骚扰性打开」用户本地 Web UI 工作流页（自动开始仍需 meta token，恶意页无法跨域获得）——风险=UI 打扰而非数据泄漏；可选加固：服务器对 `auto=1` 深链校验 Referer/Origin 白名单 | **待创始人批准加固级别** |
| 3 | 路径 C（Server 插件）是否再评估 | 建议**维持不推荐**（无沙箱警告+不收录+安装摩擦）；仅当创始人要求「插件脱离网页端独立备份」才重新评估 | **待创始人裁决** |
| 4 | W3'/W4' 后端 API 化与 P5 的排期 | 插件可行性依赖工作流 API 存在；建议 P5 与 W3'/W4' 并行立项，插件在「API 就绪日」联调 | **待创始人排期确认** |
| 5 | 弹窗拦截 | `window.open` 可能被浏览器拦截；插件按钮为直接用户手势触发（安全），README 注明允许弹窗 | 实现细节，无需批准 |

---

## 6. 给创始人的三句话结论

1. **插件可行的最小形态** = 路径 A（深链引导）：一键启动「有结果的救数据动作」，token 模型不变、安全面最小。
2. **网页端的工作流页（急救备份/恢复）是插件可行性的后端载体**——「先不管网页端」指首页装修搁置，不是不做工作流页；两者以 W3'/W4' API 化衔接。
3. **需要批准的只有三件事**：`/api/ping` 免 token（建议附 Host 白名单）、深链加固级别、路径 C 是否彻底关闭。

---

## 7. 来源与联动

- [st-plugin-plan.md](./st-plugin-plan.md)（§6.3 token 模型、§4 阶段拆分）、[research-st-plugin.md](./research-st-plugin.md)（三选项与先例）
- [product-useless-diagnosis.md](./product-useless-diagnosis.md)（MVP-loop：急救备份→恢复→场景入口）、[failure-case-library.md](./failure-case-library.md)（CASE-10/13/14/16/02）
- 官方：[Writing Extensions](https://docs.sillytavern.app/for-contributors/writing-extensions/)、[Server Plugins](https://docs.sillytavern.app/for-contributors/server-plugins/)（路径 C 排除依据）
- 先例：[nat20-bridge](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md)（B 路径先例）、[st-saves](https://github.com/breezewb/st-saves)（C 路径安装摩擦证据）
