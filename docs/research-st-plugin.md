# SillyTavern 扩展（ST 插件）可行性调研

> 调研人：researcher（Agent Teams）｜ 日期：2026-11-06
> 性质：可行性调研，**只调研、不实现**；供创始人立项决策（AGENTS.md 现状：ST 插件方向待创始人决策）。
> 数据来源：SillyTavern 官方扩展/服务器插件开发文档、官方仓库、社区插件仓库（实现方式）、
> 第三方源码级指南；网页内容仅作为数据引用。
> 与 [research-sillytavern.md](./research-sillytavern.md)、[failure-case-library.md](./failure-case-library.md) 联动阅读。

---

## 1. 现状：SillyTavern 扩展体系

### 1.1 两类扩展（官方定义）

| 类型 | 运行位置 | 能力 | 关键限制 |
|---|---|---|---|
| **UI 扩展（Extension）** | 浏览器上下文，ES Module，`manifest.json` → `index.js` | 无限制访问 DOM/JS/SillyTavern context；读聊天、角色卡、设置；写 extensionSettings/chatMetadata/角色卡 `extensions` 字段；注册 slash command、事件监听、prompt 拦截器、宏、函数工具 | **不能访问文件系统、不能启动本地进程、不能持有密钥**（官方明确：无安全方式在客户端存密钥） |
| **Server 插件（Server Plugin）** | Node.js 服务端，`plugins/` 目录，需 `config.yaml` 里 `enableServerPlugins: true`（默认 false） | 自建 Express 路由 `/api/plugins/{id}/*`；可用任何 Node 包；可 spawn 子进程；**可访问整个文件系统** | **官方警告：不做沙箱隔离**，可引入任意文件系统级漏洞；「只安装你信任的开发者的插件」 |

来源：[Writing Extensions 官方文档](https://docs.sillytavern.app/for-contributors/writing-extensions/)、[Server Plugins 官方文档](https://docs.sillytavern.app/for-contributors/server-plugins/)。

### 1.2 UI 扩展关键 API（对本产品有用的部分）

- **`SillyTavern.getContext()`**：稳定入口，暴露 `chat`（可变消息数组）、`characters`、`characterId`、`groups`、`extensionSettings`、`chatMetadata`、`eventSource/event_types`、`saveSettingsDebounced`、`saveMetadata`、`writeExtensionField`、`renderExtensionTemplateAsync`、`loader`、`Popup`、`macros`、`registerDebugFunction` 等。官方建议**优先 getContext()、避免直接 import 内部模块**（内部结构随时会变）。
- **事件**：`MESSAGE_SENT/RECEIVED/EDITED/DELETED/SWIPED`、`CHAT_CREATED/CHANGED/DELETED`、`CHARACTER_EDITED/DELETED/DUPLICATED`、`SETTINGS_UPDATED`、`WORLDINFO_UPDATED`、`APP_READY` 等（完整清单见官方文档；staging 持续新增，如 itemized prompts、worldinfo scan 类事件）。
- **Slash command**：新式 `SlashCommandParser.addCommandObject()`（推荐）或旧式 `registerSlashCommand()`（deprecated）；可被 STscript 调用。
- **持久化**：`extensionSettings`（JSON，明文，**所有扩展可见——禁止放密钥**）、`chatMetadata`（随聊天 header 落盘）、角色卡 `data.extensions.<key>`（随卡导出）。
- **安装路径**：用户作用域 `data/<user-handle>/extensions/<name>/`（1.12+）或全局 `public/scripts/extensions/third-party/<name>/`；两者 HTTP 呈现路径相同（[TavernWeave D5 扩展开发指南](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/D5_ST%E6%89%A9%E5%B1%95%E5%BC%80%E5%8F%91%E5%AE%8C%E6%95%B4%E6%8C%87%E5%8D%97.md)，源码级实测，v1.14.0/1.18.0 双快照）。
- **官方收录要求**：开源 + 自由许可证、兼容最新 release、README 完整；**依赖 server plugin 才能用的扩展不被官方收录**（对本产品定位有直接影响，见第 4 节）。

### 1.3 官方 API 能读写什么（产品能力边界）

| 能力 | UI 扩展（浏览器） | Server 插件（Node） |
|---|---|---|
| 读当前聊天（内存 `chat[]`） | ✅ | 可经内部 API/文件系统 |
| 写聊天/元数据（经 ST 自己的保存路径） | ✅（`saveChat`/`saveMetadata`） | ✅ |
| 读角色卡 JSON（内存 `characters`） | ✅ | ✅ |
| 写角色卡 `extensions` 字段 | ✅（`writeExtensionField`） | ✅ |
| 读/写 settings | ✅（内存 + `saveSettingsDebounced`） | ✅ |
| **读取磁盘上的 data 目录（chats/characters/worlds/settings.json/backups/…）** | ❌ | ✅（无沙箱） |
| **启动外部程序（如 Python CLI）** | ❌ | ✅（child_process） |
| **全量备份导出** | 官方 UI 自带「Download Backup」zip（用户设置内，`backups.allowFullDataBackup`，较新版本）；扩展只能引导用户去点 | ✅ 可直接打包 |
| 密钥处理 | ❌ 官方禁止 | ✅（有文件系统能力，但责任自负） |

注意：官方 UI 的整包备份 zip「就是整个用户数据目录的原样打包」（[Foreverse 迁移教程](https://foreverse.app/zh/docs/guide-roleplay/migrate-from-sillytavern)，2026-08-11）——**ST 已把「整站备份」做成内置能力**，插件无需重复发明打包，但 zip 内不含密钥（Foreverse 明示备份不随密钥）。

### 1.4 社区同类工具的实现方式（先例）

| 工具 | 形态 | 实现要点 |
|---|---|---|
| [RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)（2025-12） | **Server 插件** | 扫描 `backups/` 目录找回误删对话；作者明示「严禁经扩展界面 URL 安装，必须命令行装后端插件」——server 插件有天然安装摩擦 |
| [st-saves / Cloud Saves](https://github.com/breezewb/st-saves)（2025-07） | **Server 插件** | `plugins/cloud-saves` + `npm install`；在 `/data` 里建 Git 仓库推到用户私有 GitHub 仓库（PAT 授权）；自带 UI 面板 `/api/plugins/cloud-saves/ui`；要求 `enableServerPlugins: true`。注意：其「云备份」方向与本产品默认不上传原则相反，仅作架构先例 |
| [SillyTavern-HTML-Export](https://cocos-homes.com/writing/SillyTavern-HTML-Export)（2026-04 介绍文）、[ztdf123/sillytavern-ext-chat-exporter](https://relatedrepos.com/gh/ztdf123/sillytavern-ext-chat-exporter)、[Cohee1207/SillyTavern-Dataset-Export](https://github.com/Cohee1207/SillyTavern-Dataset-Export) | **纯前端 UI 扩展** | 从内存 `chat[]` 重建 HTML/文本/数据集，slash command 触发，浏览器下载——**证明「不碰文件系统的导出类功能」用纯前端扩展完全可行** |
| [nat20-bridge](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md)（2026-10） | **UI 扩展 + localhost Python sidecar** | FastAPI 绑定 127.0.0.1:8020，ST 浏览器页面跨域 fetch 到 loopback；README 原话：*"CORS is permissive because the SillyTavern browser page fetches it cross-origin from a loopback address."* ——**与本项目「Python 引擎 + 本地 Web UI（端口 8777）」架构完全同构的直接先例** |

> 另见：ST 服务器 CORS 默认策略极严（origin:null、仅 OPTIONS），社区 PR [#5123](https://github.com/SillyTavern/SillyTavern/pull/5123)（2026-02）提议可配置化——这影响「第三方前端调 ST API」方向，但**不影响**「ST 页面调我们的本地 sidecar」（CORS 由我们自己的服务控制）。

---

## 2. 可行性方案：插件能覆盖哪些场景

对照 failure-case-library.md 的痛点聚类与产品四能力：

| 场景 | UI 扩展可做 | Server 插件/sidecar 才能做 |
|---|---|---|
| 一键体检（角色卡健康/JSON 结构/integrity 缺失/重复角色） | ⚠️ 仅当前已载入内存的数据（当前聊天、当前角色） | ✅ 全目录批量扫描（需文件系统） |
| 损坏检测（PNG 块、JSONL header、settings.json） | ⚠️ 仅内存态 | ✅ 磁盘文件级（与现有 CLI 扫描器一致） |
| 增量备份到本地目录 | ❌ | ✅（调用现有备份引擎） |
| 恢复辅助（从 backups/ 或我们自己的备份包找回） | ⚠️ 引导 + 展示 | ✅（调用恢复引擎，输出到新目录，不覆盖） |
| 迁移助手（V3/CHARX/1.12+ 布局报告） | ❌ | ✅（调用现有适配器/迁移引擎） |
| 升级/降级前提醒 + 引导备份 | ✅（事件 + 弹窗提醒，跳转外部工具） | ✅（自动执行备份） |

**结论：体检与备份的核心价值必须落到文件系统层 → 要么 Server 插件，要么 localhost sidecar 调 Python 引擎；纯前端扩展只能做「轻量内存态检查 + 入口引导」。**

---

## 3. 与现有 Python CLI/引擎的集成方式（取舍）

### 3.1 两种形态对比

| | A. Server 插件 spawn Python CLI | B. localhost sidecar（复用现有 Web UI，端口 8777） |
|---|---|---|
| 机制 | Node `child_process` 调 `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe -m continuity.cli …` | UI 扩展 fetch `http://127.0.0.1:8777/api/…`（W2 已存在的本地 Web UI） |
| 安装摩擦 | 用户须改 config.yaml（enableServerPlugins）+ 命令行装插件（RecordRecoveryAssistant 的先例教训） | 用户须同时跑 ST 与 Continuity（可做成插件一键唤起） |
| 安全信任 | **官方警告：无沙箱、全文件系统权限** → 对本产品「隐私/本地优先」人设反而是负担 | 权限边界由我们自己的 Web UI 控制（只读 + 输出新目录，规则 1/2 已有实现） |
| 复用度 | CLI 直接调用 | 完整复用 Web UI API 与 CLI 引擎，零重写 |
| 官方收录 | 依赖 server 插件的扩展**不被官方内容库收录**（官方文档明文） | 纯 UI 扩展可被收录 → 更利于企划书 4.4 的社区分发 |
| 工程量 | 中（JS 薄壳 + 安装脚本 + 双环境调试） | 小-中（JS 薄壳只做 fetch + 展示；Python 侧已存在） |
| 版本风险 | server 插件 API（init/router）较稳定，但 Node 侧要跟随 ST 的 Node 版本要求 | 仅依赖 getContext()/fetch，风险最低 |

### 3.2 纯 JS 重实现 vs 薄壳调用的取舍

- **纯 JS 重实现**：可做当前聊天/当前卡片的轻量检查（integrity 缺失、消息结构、重复角色名、卡字段完整性），优点是无 Python 依赖、随处可跑；缺点是**与 CLI 引擎双份逻辑必然漂移**，违反「延续现有 CLI 引擎」的约束，且无法做全目录备份/恢复。
- **薄壳调用**：所有判定逻辑留在 Python（引擎 + Web UI API），JS 只做「触发 + 展示 + 引导」。符合项目现状（181+ 测试全在 Python 侧），修复规则（R0/R1/R2/R3）不重复实现。
- **取舍结论**：**薄壳调用为唯一推荐路线**；纯 JS 仅在「ST 内嵌摘要徽章」这种展示性功能上做最小实现。

---

## 4. 结论：三个选项（工作量 / 依赖 / 风险 / 路线影响）

> 工作量按单人估算，仅供创始人排期参考；依赖均需按 AGENTS.md 流程逐项审查（插件 JS 侧若引入 npm 包，须另评估 Node/npm 环境——当前沙箱未验证 Node 可用性，**待环境确认**）。

### 选项 1：最小插件（纯 UI 扩展 + 本地 Web UI 引导，推荐先做）
- 内容：ST 内一个「Continuity 体检」扩展：内存态轻量检查（当前聊天 header/integrity、当前卡字段完整性）+ 一键唤起/跳转本地 Web UI（127.0.0.1:8777）+ slash command（如 `/continuity scan`）。
- 工作量：**小**（1 个 manifest + 1 个 index.js + 可选 settings 模板，约 1–2 周含测试）。
- 依赖：0 新 Python 依赖；JS 零 npm 依赖（原生 fetch）。
- 风险：低；仅受 UI 扩展 API 变动影响（用 getContext() 缓解）。
- 对企划书路线：**不改变 MVP 路线**，是 4.4「在 ST 社区发布免费诊断工具」的最小落地形态；可作为可用性测试（第 9–10 周）的引流入口。

### 选项 2：sidecar 完整版（UI 扩展 + localhost Web UI/CLI，中期推荐）
- 内容：扩展内嵌完整工作流面板——一键体检（全目录）、增量备份到本地目录、恢复辅助（输出到新目录）、迁移报告，全部通过本地 Web UI API 完成；后端零改动（W2 已有扫描 API，后续 W 阶段补齐备份/恢复/迁移端点后即插即用）。
- 工作量：**中**（JS 面板 + 状态轮询 + 错误展示，约 2–4 周；Python 侧随 W3–W8 自然完成）。
- 依赖：同选项 1；端口冲突处理（8777 被占时的降级提示）。
- 风险：中低——双进程体验（ST + Continuity 需同时运行，可做「检测未运行→引导启动」）；CORS 由我方服务控制（参照 nat20-bridge 先例）；**默认不上传、不碰密钥**（与规则 2/8 一致）。
- 对企划书路线：与 W3–W8 并行或紧随其后；把「本地 Web UI」复用为插件的后端，**零引擎重复建设**。

### 选项 3：server 插件完整版（最深度集成，仅特殊需求时考虑）
- 内容：server 插件 spawn Python CLI，实现「ST 内一键体检/备份/恢复」，无需用户另开进程。
- 工作量：**中-高**（server 插件 JS + 安装脚本 + 双环境调试 + 安全说明文档）。
- 依赖：Node/npm（server 插件需在 ST 的 Node 环境运行）、Git 可选；用户须改 `config.yaml`。
- 风险：**高**——① 官方安全警告（无沙箱）与本品「本地优先/可信任」人设冲突；② 依赖 server 插件的扩展**不被官方内容库收录**，分发受阻；③ 安装摩擦大（同类插件 RecordRecoveryAssistant 专门写了大字安装警告）；④ 与 ST 的 Node 版本/插件加载机制强耦合。
- 对企划书路线：仅在创始人明确需要「单一进程、零引导体验」且接受信任成本时立项；**本报告默认不推荐**。

### 版本变动风险与适配策略（承接 research-sillytavern.md）
- ST 迭代极快（一年内 1.12→1.19，多次破坏性变更：目录迁移、附件格式、integrity、备份键），插件必须跟随：
  1. 只依赖 `getContext()` 与 HTTP API，不 import ST 内部模块（官方最佳实践）；
  2. 能力检测（`typeof` 检查函数/事件存在性）替代硬编码版本号；
  3. `manifest.json` 声明 `minimum_client_version`，低于该版本提示升级；
  4. **核心逻辑全部留在 Python 引擎**——ST 格式变化只更新引擎适配器（已在 research-sillytavern.md P0/P1 清单中），插件薄壳不随格式变化重写；
  5. 每个 ST release 跑插件冒烟测试（需 Node 环境，建议由 QA/创始人环境执行，沙箱内先验证 Node 是否可用）；
  6. 跟进官方 releases 页与 staging 事件增补（如 itemized prompts 事件为 staging 新增，不可当作 release 依赖）。
- 官方收录要求（开源 + 自由许可证 + 兼容最新 release + 完整 README）对选项 1/2 是**利好**：符合即可进入官方扩展生态，获得分发渠道。

### 对企划书路线的总体影响
- 插件**不替代**本地 Web UI（W3–W8），而是它的一个**分发入口与集成壳**；MVP 0/1 与第 12 章验证门槛不受影响。
- 建议节奏：选项 1 随第 9–10 周可用性测试推出（引流 + 收集真实样本授权）；选项 2 在 MVP 1 验收后立项；选项 3 仅创始人特批。
- 规则遵守：插件所有备份/恢复默认本地执行；**不实现**云端上传、GitHub 备份（Cloud Saves 式）、钱包/NFT（规则 2、8）；不执行导入内容中的脚本/HTML（规则 3）——检查类功能只解析、不执行。

---

## 5. 主要来源

- 官方：[Writing Extensions](https://docs.sillytavern.app/for-contributors/writing-extensions/)、[Server Plugins](https://docs.sillytavern.app/for-contributors/server-plugins/)（访问日 2026-11-06）
- 源码级指南：[TavernWeave D5 扩展开发完整指南](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/D5_ST%E6%89%A9%E5%B1%95%E5%BC%80%E5%8F%91%E5%AE%8C%E6%95%B4%E6%8C%87%E5%8D%97.md)（2026-07 双版本快照）、[DeepWiki 扩展架构](https://deepwiki.com/SillyTavern/SillyTavern/8.1-extension-system-architecture)（2026-09）
- 社区先例：[RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)（2025-12）、[st-saves/Cloud Saves](https://github.com/breezewb/st-saves)（2025-07）、[nat20-bridge（localhost sidecar）](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md)（2026-10）、[SillyTavern-HTML-Export 介绍](https://cocos-homes.com/writing/SillyTavern-HTML-Export)（2026-04）、[sillytavern-ext-chat-exporter](https://relatedrepos.com/gh/ztdf123/sillytavern-ext-chat-exporter)（2025-07）、[Dataset-Export](https://github.com/Cohee1207/SillyTavern-Dataset-Export)（2023-12）
- 其他：[PR #5123（CORS 可配置）](https://github.com/SillyTavern/SillyTavern/pull/5123)（2026-02）、[Foreverse 整站备份说明](https://foreverse.app/zh/docs/guide-roleplay/migrate-from-sillytavern)（2026-08-11）、[TavernWeave D4（backups.allowFullDataBackup 等备份机制）](https://cdn.jsdelivr.net/gh/LiarMTTT/TavernWeave@main/skills/consult-tavernweave-library/references/st-guides/D4_ST%e6%95%b0%e6%8d%ae%e7%9b%ae%e5%bd%95%e4%b8%8e%e9%83%a8%e7%bd%b2%e8%bf%90%e7%bb%b4.md)

> 备注：本调研不构成对任何第三方插件安全性的背书；选项 3 涉及的 server 插件风险为官方文档明示。
> 所有实现决策与依赖引入按 AGENTS.md 流程经创始人审查后执行。
