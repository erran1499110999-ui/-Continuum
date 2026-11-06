# ST 插件开发计划（选项 1：最小插件，纯 UI 扩展）

> 作者：developer（Agent Teams）
> 日期：2026-11-06
> 状态：**计划稿，等待创始人确认后开工**（AGENTS.md 规则 7；本轮只计划、不写任何插件代码）
> 依据：docs/research-st-plugin.md（调研者三选项，选项 1 已获创始人立项）、docs/failure-case-library.md（P0 案例体检素材）、
> docs/TEAM-COORDINATION.md（写作用域）、AGENTS.md（最新版，含严格三轮审核规则）、docs/webui-plan.md（本地 Web UI 现状）。

## 0. 一句话定位

SillyTavern 内的一个**纯浏览器 UI 扩展（薄壳）**：内存态一键体检（只读、无副作用）+ 一键唤起本地 Web UI
（127.0.0.1:8777）+ slash command 入口。**所有判定逻辑与深度操作继续留在 Python 引擎**，插件不重复实现、
不碰文件系统、不碰密钥、不做云端（规则 1/2/3/8/9）。

---

## 0.1 市场定位：敲门砖与网站一体（创始人指令，2026-11-07）

- **插件 = 免费分发的获客敲门砖**：在 ST 官方内容库/社区免费分发（MIT 许可证 + 双语 README 达标后），
  以「酒馆内一键体检」制造轻量价值瞬间——用户无需离开酒馆就能得到内存态健康提示（H1–H6）。
- **转化漏斗（一体产品）**：
  ```
  酒馆内轻量体检提示（免费插件）──「打开本地 Web UI」── 深度体检/备份/恢复/迁移（本地 Web UI，W3–W8 引擎能力）
      ── 未来付费路径（企划书 4.4 的进阶能力沉淀，仅本地实现，不涉云端/NFT，规则 8）
  ```
  插件只做「提示 + 引导」，绝不收费、不放广告、不收集数据；**所有深度价值沉淀在本地 Web UI（= 产品的
  「网站/工作台」一体形态）**，插件与 Web UI 共用同一品牌（Continuity Studio / Continuity 体检）与双语文案。
- **为什么是敲门砖**：ST 社区是精准用户聚集地（案例库 20 条 ST 案例证明痛点高频）；插件是企划书 4.4
  「在 ST 社区发布免费诊断工具」的最小落地形态，也是第 9–10 周可用性测试的引流入口。
- **与资源地图的衔接**：调研者即将产出 `docs/resource-map.md`（分发与内容渠道资源地图）。
  本插件将作为资源地图中「ST 社区分发」条目的落地载体；可借鉴项（官方内容库收录规范、社区发布渠道
  清单、内容引流策略、案例库故事化文案）待该文档产出后补充进本计划与 P4 验收清单。
  **当前标注：待 docs/resource-map.md 产出后修订本节。**

---

## 1. 范围（做什么 / 明确不做什么）

### 1.1 功能范围（选项 1 最小插件）

| 功能 | 实现方式 | 数据来源 |
|---|---|---|
| 一键体检（内存态，只读） | `getContext()` 读当前聊天/角色卡内存，纯函数判定，结果面板展示 | 仅 ST 内存，不写任何文件 |
| 一键唤起本地 Web UI | 按钮 `window.open("http://127.0.0.1:<port>/")` 新标签页；端口来自 extensionSettings（默认 8777） | 服务器首页自携带 token（meta 注入），插件不接触 token |
| slash command 入口 | `SlashCommandParser.addCommandObject()`（旧 API 能力检测回退）注册 `/continuity` | — |
| 设置页 | extensionSettings：Web UI 端口、提示开关 | 持久化仅 settings（明文、无密钥） |

### 1.2 明确不做（与调研结论一致）

- **不做文件系统访问**：UI 扩展官方禁止；全目录体检/备份/恢复/迁移一律引导到本地 Web UI（Python 引擎）。
- **不做密钥**：插件不读、不存、不传任何 API Key（官方明示客户端无安全存钥方式）。
- **不做云端**：代码内零外部 URL（Python 静态测试强制）；不上传任何角色数据（规则 2/8）。
- **不重复实现 Python 逻辑**：R0/R1/R2/R3 判定、扫描、备份等全部留在引擎；JS 侧只有「结构事实提示」。
- **不做 server 插件**（选项 3）：官方无沙箱警告与本产品本地优先人设冲突、官方内容库不收录、安装摩擦大。

### 1.3 与 Python 引擎 / 本地 Web UI 的关系（薄壳原则）

```
ST 页面（扩展薄壳）─── 内存态轻量检查（仅提示） ──→ 面板/弹窗
        │
        └── 一键唤起 → 新标签页 http://127.0.0.1:8777/（本地 Web UI，W1–W2 已运行）
                              └── 深度扫描/备份/恢复/修复/迁移 = Python 引擎（已实现/按 W3–W8 开放）
```

- 深度操作结论（R0/R2/R3、完整性分数、差异报告）只由 Python 引擎产出；插件绝不给出 R 级判定。
- 插件内存态检查的每条结论必须标注「内存态初步提示，深度检查请打开本地 Web UI」。
- 插件随 W3–W8 自然升级为选项 2 形态（面板内嵌 API 调用），本期不依赖任何未实现的 W 端点。

---

## 2. 体检项设计（内存态，只读，无副作用）

> 依据 failure-case-library.md 第 5 节的检测规则候选；**只选可在内存态做且可验证的项**；
> 每项均为「结构事实 + 保守话术」，不猜测根因（规则 9）。

| # | 检查项 | 依据案例 | 判定逻辑（纯函数） | 话术级别 |
|---|---|---|---|---|
| H1 | 当前聊天 `chat_metadata.integrity` 缺失 | CASE-02/13/16 | `!chat_metadata?.integrity` | **提示**：旧格式或异常，勿当损坏（CASE-13 教训：旧格式告警不误伤） |
| H2 | 疑似被重置的聊天 | CASE-01/03 | 当前聊天消息数 ≤ 2 且末条为角色 `first_mes` | **提示**：疑似只剩 header+开场白，建议用 Web UI 深度体检并从备份核对 |
| H3 | 同名角色卡（不同内容） | CASE-07 | 内存 `characters` 按 `data.name` 分组，组内卡 JSON 规范化串长度或 SHA-256（`crypto.subtle`）不同 | **提示**：同名卡导入覆盖风险，建议导入前先备份（引导 Web UI） |
| H4 | 当前卡字段完整性 | CASE-18/21 | `data.name`/`first_mes` 等关键字段缺失 | **提示**：字段缺失清单（只列字段名，不列内容） |
| H5 | 当前聊天消息结构异常 | CASE-11 | 消息缺 `mes` 或 `is_user` 非布尔 | **提示**：消息结构异常条数 |
| H6 | 服务器可唤起性（可选，P3 定） | — | 仅 `window.open`；如需「检测未运行」须新增 `/api/ping`+CORS → 见 6.3 待确认 | — |

- 全部检查**只读内存、不调用 saveChat/saveSettings/任何写路径**；面板渲染用 textContent/模板转义（规则 3）。
- 合成样本单元测试构造假 `context` 对象覆盖上述判定（见第 4 节测试策略）。

---

## 3. 结构与代码量预估

```
extensions/sillytavern/continuity-st/     # 插件根（新顶层目录，与 src/tests 零冲突）
  manifest.json         # id/name/version/minimum_client_version/license（~20 行）
  index.js              # 入口：事件与 slash 注册、面板、体检编排（~450 行）
  checks.js             # 纯函数体检逻辑（可独立单测，~200 行）
  settings.html         # 设置页（端口等，~60 行）
  style.css             # 面板样式（~80 行）
  README.md             # 中英双语安装/使用说明（官方收录要求，~150 行）
tests/
  test_st_plugin_static.py    # Python 静态契约/安全 lint 测试（~200 行，落点需创始人协调）
extensions/sillytavern/tests/
  checks.test.mjs             # JS 纯函数单测（node:test，零 npm 依赖，~150 行）
```

**代码量预估**：JS ~650 行 + HTML/CSS ~140 行 + 测试 ~350 行 + 文档 ~150 行；单人 **1–2 周**（与调研一致）。

- `minimum_client_version`：调研建议按 1.12 目录迁移后的版本线（具体取值待创始人确认，见 6.4）。
- 只依赖 `getContext()` 与浏览器原生 API；不 import ST 内部模块；全部 API 用法带能力检测（`typeof`）与降级提示。

---

## 4. 分阶段拆分（每阶段一个模块；逐阶段停等验收；每阶段过 QA 严格三轮审核）

| 阶段 | 模块 | 依赖 | 内容 | 阶段验收要点 |
|---|---|---|---|---|
| **P1** | 骨架与静态契约 | 无 | `manifest.json`、最小 `index.js`（APP_READY 注册、空面板、版本徽标）、`tests/test_st_plugin_static.py`（manifest schema 校验、禁外部 URL、禁 eval/innerHTML、禁 localStorage/密钥字样、双语 README 占位检查） | pytest 真实运行；manifest 全字段校验通过；静态 lint 全过 |
| **P2** | 内存态体检模块 | P1 | `checks.js` 纯函数 + 面板结果渲染（全 textContent）+ `checks.test.mjs`（node:test，假 context 覆盖 H1–H5 与话术保守性断言）；Python 侧静态测试扩展 | **沙箱内 Node 可用性实测**（前置门，见 5.1）；JS 单测真实运行全过；静态测试全过；无任何写路径 |
| **P3** | 唤起与入口模块 | P2 | 「打开本地 Web UI」按钮（端口读 extensionSettings，默认 8777；未运行服务的友好文案）、slash command `/continuity`（新式 API + 能力检测回退）、设置页 | 静态测试（slash 注册代码存在、只 127.0.0.1 域名）；创始人本机 ST 实测：按钮开新标签、slash 触发体检、控制台零报错 |
| **P4** | 打磨与收录准备 | P3 | 中英双语 README（安装/使用/隐私声明）、版本门槛提示 UX、staging 防御（不依赖 staging 事件）、docs 指引更新（主 README 插件一节需创始人协调）、QA 严格三轮审核 | 三轮审核全过；创始人真实验收步骤（见 6.2）全过；GitHub 按阶段推送 |

- 每阶段完成后：变更清单 + 真实测试结果 + 风险与下一步，**停止等待验收**（规则 7）。
- P 路线与 W3–W8 路线并行、互不阻塞；P 路线不修改任何核心引擎文件。

---

## 5. 环境与验证

### 5.1 开发环境与沙箱可用性（风险标注）

| 需求 | 沙箱现状 | 风险与备选 |
|---|---|---|
| Node（JS 单测 node:test） | **未验证**（调研第 4 节已标注「沙箱未验证 Node 可用性，待环境确认」） | P2 开工前置门：`node --version` 实测。可用 → 沙箱内真跑单测；不可用 → ① JS 单测由创始人/QA 环境执行并**如实记录运行证据**（规则 10：绝不把未运行的标为通过）；② Python 静态契约测试仍在沙箱真跑，作为兜底；③ 或创始人裁决安装 Node（走 AGENTS.md 依赖审查流程） |
| 浏览器（真实 ST 页面） | 沙箱不可用 | 真实验收必须在创始人本机 ST 实例进行（见 6.2）；沙箱内只测纯逻辑/静态契约 |
| Python 引擎 | 可用（现有体系） | 无 |
| npm 依赖 | 不需要（node:test 内置；零 npm 包） | 无 |

### 5.2 沙箱内可真实运行的测试（规则 10）

1. **Python 静态契约测试**（`tests/test_st_plugin_static.py`，pytest 真跑）：
   - manifest.json：必填字段、`minimum_client_version` 语义版本、license 字段存在；
   - JS 源码 lint：无 `eval(`、无 `innerHTML=`、无 `http://`（127.0.0.1 除外）、无外部域名、
     无 `localStorage`、无密钥字样（`api_key`/`token=` 写入）；
   - checks.js 导出函数签名存在且为纯函数（源码级正则 + 简单 AST 启发，不执行 JS）。
2. **JS 单元测试**（`checks.test.mjs`，`node --test`，零依赖）：以假 context 覆盖 H1–H5
   判定分支与保守话术（含边界：旧格式无 integrity、消息数=2 但末条非 first_mes 不误报等）。
   执行方式：Node 可用 → 沙箱内真跑，并在 pytest 中以子进程桥接复核（可选）；Node 不可用 → 按 5.1 备选执行并记录证据。
3. 现有 pytest 全套（187 collected 基线）回归不降。

### 5.3 创始人真实验收步骤（ST 实例，见 6.2 完整清单）

核心：安装插件 → 启用 → 设置页 → `/continuity` 触发 → 三类样本聊天上体检 → 唤起 Web UI → 控制台/网络面板审计。

---

## 6. 拟新增/修改文件清单、写作用域与待确认

### 6.1 写作用域（本轮及后续 P 阶段）

- **新目录 `extensions/sillytavern/continuity-st/`**（全新，与 src/tests/docs 零冲突；目录形态待创始人确认，见 6.4）。
- **新增 `tests/test_st_plugin_static.py`**：tests/ 落点沿用「方案甲」（创始人已批准先例），仍请创始人确认（⚠）。
- **不修改任何现有文件**；主 README/docs 增加插件一节的更新需创始人协调排期（外部开发者/创始人写作用域）。

### 6.2 创始人真实验收步骤（真机 SillyTavern）

1. 环境：创始人本机 ST（≥ `minimum_client_version`）+ 已运行 `python -m continuity.webui`（默认 8777）。
2. 安装：把 `continuity-st` 文件夹放入 `data/<user-handle>/extensions/`（或 `public/scripts/extensions/third-party/`），扩展管理页启用。
3. 体检：在 ①疑似重置聊天（header+开场白）②无 integrity 的旧格式聊天 ③两张同名不同内容卡 上执行一键体检 → 面板分别给出 H2/H1/H3 提示，且**确认无任何文件被写**（对比 data 目录 mtime）。
4. 唤起：点击「打开本地 Web UI」→ 新标签打开 http://127.0.0.1:8777/（首页正常显示，无需输入任何密钥）；停掉服务后按钮给出友好提示。
5. slash：输入 `/continuity` → 触发体检面板；不支持的 ST 版本给出升级提示。
6. 审计：DevTools Network 面板确认**零外部出站请求**（仅 127.0.0.1 或本页）；控制台零报错。
7. 创始人验收通过 → commit + GitHub 按阶段推送（凭据仅环境变量）。

### 6.3 token 与跨域处理说明（设计决策，待确认）

- **MVP（P3）**：插件**只打开新标签页**，不做任何跨域 API 调用。token 由服务器注入其首页
  `<meta name="continuity-token">`，新标签页自取自用——**插件全程不接触、不存储 token**，
  也无需给服务器加 CORS（零安全面变化）。
- **备选（选项 2 阶段再做，需创始人确认）**：服务器新增免 token 的 `GET /api/ping`（返回仅
  `{"status":"ok"}`）+ `Access-Control-Allow-Origin` 白名单（默认 ST 常见源），供插件「检测服务
  未运行 → 引导启动」。此改动触及 `src/continuity/webui/server.py`（developer 范围，但属安全变更，须创始人批准）。

### 6.4 待创始人确认清单

1. 插件目录与命名：`extensions/sillytavern/continuity-st/`（备选 `st-plugin/`）；插件显示名「Continuity 体检」。
2. slash 命令名：`/continuity`（备选 `/continuity-scan`）。
3. `minimum_client_version` 取值（建议 1.12.0 或更高，按目录迁移版本线）。
4. 插件许可证（官方内容库要求自由许可证：AGPL-3.0 或 MIT，待定）。
5. Node 环境：沙箱内是否可用/是否允许安装；不可用时的 JS 单测执行与证据记录方案。
6. MVP 唤起方式：确认「仅 window.open 新标签」方案（零 token/零 CORS）；是否现在就做 `/api/ping`+CORS 白名单备选。
7. tests 落点：`tests/test_st_plugin_static.py`（方案甲）确认。
8. 主 README/docs 增加插件章节的更新排期（需创始人协调）。

---

## 7. 风险清单

| # | 风险 | 影响 | 对策 |
|---|---|---|---|
| R1 | 沙箱无 Node → JS 单测无法在沙箱真跑 | P2 验收受阻 | P2 前置门实测；备选：创始人/QA 环境执行并记录证据 + Python 静态测试兜底；绝不虚标（规则 10） |
| R2 | ST 版本迭代破坏 API（1.12→1.19 多次破坏性变更） | 插件失效/报错 | 只用 getContext()；能力检测替代版本硬编码；minimum_client_version 门槛；staging 事件不依赖 |
| R3 | 8777 端口被占用/服务未运行 | 唤起失败体验差 | 端口可配置（extensionSettings）；友好文案「请先运行 python -m continuity.webui」；README 双语说明 |
| R4 | 内存态检查的启发式误报（同名卡/疑似重置） | 误导用户 | 全部标注「内存态初步提示」；话术保守（「疑似」「建议」）；结论性判定只由 Python 引擎给出 |
| R5 | 官方收录要求不达标（README/license/兼容性） | 无法进入官方内容库 | P4 专门准备：双语 README、自由许可证（待创始人定）、兼容最新 release 承诺 |
| R6 | 插件被误当作「可深度体检/备份」工具（能力边界误解） | 期望落差 | 面板与 README 明示：深度检查与备份/恢复/迁移 → 本地 Web UI；插件是入口不是引擎 |
| R7 | 与外部会话核心代码重叠 | 写冲突 | 插件全程不 import 内部模块、不改任何核心文件；P 路线新增文件全部在新目录 |

---

## 8. 下一步

1. 本计划提交创始人确认（重点：第 6.4 节清单）。
2. 创始人确认后，下一轮仅开工 **P1（骨架与静态契约）**；P2 前置门先实测沙箱 Node 可用性。
3. 每阶段完成：变更清单 + 真实测试结果 + 风险与下一步，停等验收与 QA 严格三轮审核。
