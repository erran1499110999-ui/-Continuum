# 本地 Web UI 开发计划（提示词 8）

> 作者：developer（产品开发者，Agent Teams）
> 日期：2026-11-06
> 状态：**计划稿，等待创始人确认后开工**（AGENTS.md 规则 7：先计划，再修改；阶段完成后停止等待验收）
> 依据：AGENTS.md（最新版，2026-11-06）、TEAM-COORDINATION.md（写作用域）、README.md、
> pyproject.toml、CHANGELOG.md（0.1.0–0.1.3）、docs/format-compatibility.md、docs/review-guide.md（0.1.3 基线），
> 以及对 src/continuity/ 全部引擎与 tests/ 的只读通读。

## 0. 本轮结论摘要

1. 本计划**只规划、不写任何产品代码**；本轮唯一交付物就是本文件 `docs/webui-plan.md`。
2. 技术路线自评结论：**Python 标准库 HTTP 服务器 + 无构建原生 JS 单页应用**（零新增运行时依赖）。
   `docs/research-webui.md`（调研者产物）截至 2026-11-06 **尚不存在**，因此本路线为自评，
   **待创始人确认**；若调研者随后产出该文档，将与本计划对照修订。
3. 新代码全部集中在独立新目录 `src/continuity/webui/`，不修改任何现有核心源码；
   新增 pytest 测试文件位于 `tests/` 目录（**新文件、不改旧文件**），该目录现属外部开发者写作用域，
   属**「需创始人协调」**事项。
4. 分 8 个阶段（W1–W8），每阶段一个模块，逐阶段停止等待验收。

---

## 1. 现状盘点（通读结论，供 UI 一一对应）

### 1.1 引擎能力面（Web UI 唯一依赖的公开函数，签名已定型于 0.1.3）

| 能力 | 引擎入口（`src/continuity/`） | 输出 | 关键约束（UI 必须继承） |
|---|---|---|---|
| 扫描 | `scanners/scan.py::scan_directory(root, limits)` → `ScanReport` | 文件清单（类型/SHA-256）、`findings`（严重级+修复等级+建议）、重复组、跳过符号链接 | 源目录**只读**；超资源上限抛 `ScanError`，绝不输出貌似完整的结果 |
| 备份 | `backup/engine.py::create_backup(source, bundle, *, options, source_client, source_client_version)` → `BundleManifest` | `manifest.json` + `files/`；warnings | bundle **必须不存在**且不得位于 source 之内；备份中源变化即中止 |
| 校验 | `backup/engine.py::verify_bundle(bundle)` → `VerifyReport` | ok/checked/mismatches/missing/extra_files | 清单外文件 = 完整性失败（0.1.2） |
| 恢复 | `backup/engine.py::restore_backup(bundle, dest, *, options)` → `RestoreReport` | restored/errors/warnings/extra_files | dest **必须不存在**；预校验 + 临时目录 + 原子发布 |
| 修复预览 | `repair/engine.py::apply_repairs(source, output)` → `RepairReport` | `repair-report.json` + `diffs/*.diff`；R0 自动修复 / R2 建议 / R3 隔离清单 | output **必须不存在**；修复副本写新目录，源只读 |
| 迁移 | `migration/engine.py::migrate_sillytavern(source, output, *, limits)` → `MigrationReport` | `migration-report.json` + 导出目录；逐项验证 items、匹配率+分母解释、needs_review、damaged/unprocessed 警示 | output **必须不存在**；报告脱敏（无绝对路径、无原始字段值） |
| 版本 | `continuity.__version__`（0.1.0） | — | — |

- 所有错误类型（`BackupError`/`RepairError`/`MigrationError`/`ScanError`/`OSError`）信息均面向用户，UI 直接透传展示。
- 报告对象：`ScanReport`/`VerifyReport`/`RestoreReport`/`RepairReport`/`MigrationReport` 为 dataclass，
  `BundleManifest`/`ScanFinding` 为 Pydantic；Web UI 在自有的序列化层统一转 JSON（`asdict`/`model_dump`）。
- **尚未实现**：R1 可推断修复规则（需真实样本）、HTML 报告（`reports/` 目前为空壳）、
  引擎级进度回调（长任务只有开始/结束状态）。

### 1.2 CLI 命令面（Web UI 功能一一对应）

`scan` / `backup` / `restore` / `verify` / `repair` / `migrate` / `version`（`src/continuity/cli.py`）。
Web UI 的每个页面即一个 CLI 命令的可视化 + 结果展示，见第 4 节功能清单。

---

## 2. 技术选型与理由（自评，待创始人确认）

### 2.1 硬约束（来自 AGENTS.md 环境说明与沙箱现状）

- Python 必须用绝对路径 `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe`（PATH 的是 WindowsApps 存根）。
- pip 不可用；新依赖须经**创始人逐项审查**，并用 `tools/fetch_wheels.py` 下载**纯 wheel**（`py3-none-any`）
  解压到 `.deps2`，同步 `.gitignore`。Python 3.14 很新，**带编译组件的 wheel 风险高**。
- 沙箱无 Node 工具链 → 任何需要前端构建（npm/webpack/vite）的方案**不可行**。
- 沙箱文件系统受限（0o700 目录上锁、中文叶子目录名受限、缓存原子写入被拒）→ 服务器与测试必须在
  现有 `pyproject.toml`/`conftest.py` 固化的工作方式内运行（这些固化配置**勿删勿改**）。
- 本地优先：默认不上传、不联网（产品运行期零出站请求）。

### 2.2 推荐方案 A（主推）：Python 标准库服务器 + 无构建原生 JS 单页应用

| 层次 | 选择 | 理由 |
|---|---|---|
| 后端 | `http.server.ThreadingHTTPServer`（标准库） | Python 3.11+/3.14 内置，**零新增运行时依赖**：免创始人逐项审查、免 fetch_wheels、沙箱内必然可用；同步阻塞引擎调用与线程模型天然匹配 |
| 路由/API | 自研薄路由层（约 100 行） | 端点极少（见 4.2），不值得引入框架；后续想换 Flask/FastAPI 时 API 层已隔离 |
| 前端 | 原生 HTML/CSS/JS 单页（无构建），静态资源由服务端从包内 `static/` 目录提供 | 沙箱无 Node；无构建 = 无工具链风险；资源量小（一个工作台） |
| 通信 | JSON POST API + 轮询 job 状态 | POST 体传 UTF-8 路径，**避开中文路径出现在 URL query 的编码问题**（本项目大量中文路径）；无需 WebSocket |
| 长任务 | `jobs.py` 单工作线程串行队列 | 引擎无进度回调，长任务只有粗粒度状态（queued/running/succeeded/failed + 日志缓冲）；本地单用户工具串行执行最稳 |
| 安全 | 仅绑定 127.0.0.1；启动随机 token；Host 头白名单；CSP；前端全部 textContent 转义 | 见第 5 节 |
| 启动 | `python -m continuity.webui`（`__main__.py`），默认端口 8777（2026-11-06 创始人裁决：原默认 8765 被百度输入法常驻占用） | **不修改 cli.py**，避开外部开发者核心文件；浏览器自动打开为可选参数（沙箱内打不开则忽略） |

### 2.3 备选方案对比

| 方案 | 新增依赖 | Python 3.14 兼容 | 沙箱可真实运行 | 前端 | 复杂度/风险 | 结论 |
|---|---|---|---|---|---|---|
| **A 标准库 + 原生 JS** | 0 | 内置，必然 | 是 | 无构建 | 低 | **推荐** |
| B Flask + Jinja2 模板 | ~6 个纯 wheel（flask/werkzeug/jinja2/click/itsdangerous/markupsafe 等） | 纯 wheel 可用 | 需 fetch_wheels + 创始人逐项审查 | 无构建（服务端模板） | 中 | 备选（想要成熟路由/模板时） |
| C FastAPI + uvicorn/starlette | ~12 个纯 wheel（fastapi/starlette/anyio/h11/sniffio 等） | 纯 wheel 可用 | 同上；async 事件循环在受限沙箱未验证 | 无构建 SPA | 中高 | 备选（未来需要 WebSocket 流式进度时再评估） |
| D Gradio / Streamlit | 多且重、常带编译组件 | 3.14 wheel 风险高 | 大概率不可用 | 框架自带 | 高 | 不采用 |
| E React/Vue + Node 构建 | 需 Node 工具链 | — | 沙箱无 Node，不可构建 | 构建产物需预生成入库 | 高 | 不采用 |
| F 纯静态 HTML（无服务器，双击打开） | 0 | — | 浏览器无文件系统能力，无法调用引擎 | — | — | 不可行（必须跑引擎） |

**推荐 A，理由**：满足全部硬约束（零依赖、3.14 兼容、沙箱必可运行、本地优先），且开发量最小；
`api.py` 隔离层保证未来如创始人裁定改用 B/C，迁移成本可控。**本选择待创始人确认。**

### 2.4 与调研者结论的衔接

`docs/research-webui.md` 尚不存在。若研究员随后产出技术选型结论：
- 结论与 A 一致 → 直接执行；
- 结论为 B/C → 按创始人裁决，改写本计划第 2 节与阶段 W1 的实现细节，其余阶段结构不变；
- 结论含新依赖 → 一律走「创始人逐项审查 + fetch_wheels + .gitignore 同步」流程。

---

## 3. 架构设计（全部位于 `src/continuity/webui/`）

```
src/continuity/webui/
  __init__.py        模块说明
  __main__.py        python -m continuity.webui 入口（--port/--no-browser，host 硬编码 127.0.0.1）
  server.py          ThreadingHTTPServer、路由、静态文件（仅包内 static/）、安全头、Host 白名单、token 校验
  api.py             端点处理器：health / version / jobs / history（仅调用引擎与 jobs，不含业务逻辑）
  jobs.py            job 队列（单工作线程串行）：状态机 queued→running→succeeded/failed、日志缓冲、结果暂存
  views.py           引擎 dataclass/Pydantic 报告 → JSON（asdict/model_dump 适配；迁移报告已脱敏，原样透传）
  validation.py      入参校验：路径必填、输出目录不得已存在、输出不得位于源目录之内、拒绝 NUL 等非法字符
  history.py         本地操作历史（JSONL 追加，单进程单写者）：job 类型/时间/路径/结果摘要——不含任何文件内容
  static/
    index.html       单页外壳（token 通过 <meta name="continuity-token"> 注入，避开 CSP 禁内联脚本）
    app.js           路由与页面渲染（fetch + textContent，禁用 innerHTML/eval）
    style.css        工作台样式（暗色可选，无外部字体/CDN 资源——保证完全离线）
```

关键设计点：
- **API 隔离**：`server.py` 只做 HTTP 事务；`api.py` 只做参数校验 + 调引擎；引擎绝不 import webui。
- **无「读任意文件」端点**：diff、报告 JSON 全部随 job 结果返回（`RepairReport.fixes[].diff` 已在结果内）；
  静态服务只允许读取包内 `static/` 目录（resolve 后 `is_relative_to` 校验），从根上杜绝路径穿越读用户磁盘。
- **隐私**：前端渲染一律 `textContent`/转义（角色卡与聊天内容绝不按 HTML 解析——规则 3）；CSP 默认 `self`；
  历史记录只存路径与统计摘要，不存文件内容。
- **单 job 串行**：避免多任务争用输出目录与资源上限；用户提交第二个任务时返回 409 提示排队/等待
  （实现：同一时刻至多 1 个待处理/运行任务，忙碌时 `JobQueueFullError` → HTTP 409 `JobsBusy`；
  已完成任务内存保留上限 64，防字典无限增长——W2 严格复审修复后与本设计一致）。
- **历史存储位置**：优先 `.tmp/webui-history.jsonl`（开发沙箱，已被 .gitignore）；正式运行时回退
  `%LOCALAPPDATA%\ContinuityStudio\history.jsonl`（本机环境变量路径，不写入源码）。

### 3.1 多语言支持 i18n（W3a 必做）

**要求**：中英双语界面为 W3 必做项；所有静态文本一律走语言资源表，HTML/JS 内**禁止硬编码用户可见字符串**。

- **资源文件结构**（`src/continuity/webui/static/locales/`）：
  ```
  locales/
    zh-CN.json      # 中文（默认/回退语言）
    en.json         # 英文
    registry.json   # 语言注册表：{"default":"zh-CN","languages":[{"id":"zh-CN","label":"简体中文"},{"id":"en","label":"English"}]}
  ```
- **资源表形态**：扁平 key（如 `"scan.title"`、`"scan.btnRun"`），值为纯字符串；占位符用 `{name}`，
  渲染时经统一 `t(key, params)` 函数替换；**绝不允许在资源值中嵌入 HTML**（规则 3）。
- **切换机制**：`t()` 依据 `localStorage["continuity-lang"]`（默认跟随浏览器语言 → 回退 zh-CN）；
  导航栏语言切换器即时重渲染；服务端仅提供资源文件静态下载，不做服务端渲染。
- **扩展更多语言的框架**：新增语言 = 新增 `xx.json` + 在 `registry.json` 登记，零代码改动；
  缺失 key 自动回退默认语言并可在控制台 debug 级提示（资源完整性由测试锁定，见第 8 节）。
- **测试保证**：`tests/test_webui_i18n.py`（W3a 新增）断言：registry 与文件一致；每个语言的 key 集合
  与默认语言**完全一致**（无缺译）；所有 HTML/JS 源码无硬编码中文字面量（grep 级扫描 + 白名单例外表）。

### 3.2 UI 设计系统与外壳重构（W3a）

**背景**：创始人要求 UI 现代化重设计——交互性强、时尚前沿，参照 **Linear / Vercel / Stripe** 等现代
科技产品的视觉语言。技术栈约束不变（方案 A：无构建原生 JS/CSS），设计系统全部以 **CSS 自定义属性 +
组件类 + 少量原生 JS 工具函数**实现，不引入前端框架/构建。

- **美学基调**：精密、克制、速度感——深色默认 + 高对比中性色阶；克制的强调色（单主色 + 语义色
  ok/warn/err）；大留白、清晰层级、8px 网格间距；微交互（hover/聚焦态、150–250ms 缓动）；
  数据面板优先的信息架构（扫描/报告天然是「仪表盘」形态）。
- **设计系统组成**：
  - `theme.css`：设计令牌（色彩/间距/字号/圆角/阴影/动效时长）CSS 变量定义 + **暗色/亮色主题**
    双套变量（`data-theme` 切换 + `prefers-color-scheme` 跟随 + 用户手动覆盖，本地持久化）；
  - 组件库化：按钮/输入/徽标/标签/卡片/表格/空态/错误态/进度态统一为组件类（`ui-*`）与
    `ui.js` 工具函数（创建节点/主题切换/Toast），页面不再自造样式；
  - 动效：微过渡（`transition` 令牌）+ 尊重 `prefers-reduced-motion`（可访问性）；
  - 响应式：桌面优先，≥1024px 完整布局、窄窗口单列堆叠（本地工具，不承诺移动端全功能）。
- **范围边界**：设计系统只覆盖「产品外壳与通用组件」；复杂图表（diff 查看器等）仍按组件规范
  在对应阶段实现（W5）；不引入图标字体/CDN，图标用内联 SVG（离线可用，CSP 兼容）。
- **与调研衔接**：调研者即将产出 `docs/ui-design-direction.md`（UI 设计方向调研）。
  该文档产出后，本小节以其中结论为准修订（色彩/组件/交互的具体取向）；
  如调研结论与本小节冲突，按创始人裁决调整。**当前标注：待 docs/ui-design-direction.md 产出后修订。**

---

## 4. 页面/功能清单（与 CLI 一一对应）

### 4.1 页面清单

| 页面 | 对应 CLI 命令 | 功能与展示内容 | 规则合规要点 |
|---|---|---|---|
| 首页/概览 | version（并入） | 工具版本、本地优先承诺、当前是否有运行中 job、六个功能入口 | 明示「不上传任何数据」 |
| 扫描页 | scan | 按类型统计文件数；findings 列表（严重级 info/warning/error、修复等级、建议、证据）；重复文件组；跳过符号链接列表；**只读操作标识** | 规则 1/9：只展示引擎结论，UI 不做二次推断 |
| 备份页 | backup | 源目录 + 备份包目录 + 可选来源客户端名/版本 → manifest 摘要（条目数、warnings、bundle_id） | 预检「备份目标必须不存在、不得在源目录内」 |
| 校验页 | verify | ok / checked / mismatches / missing / extra_files；未通过时红色警示（0.1.2：清单外文件=失败） | 结果如实，不粉饰 |
| 恢复页 | restore | restored / errors / warnings / extra_files；目标目录必须不存在 | 原子发布语义在提示文案中说明 |
| 修复预览页 | repair | **R0**：自动修复列表（rule_id/前后 SHA-256/理由）+ 逐条 **diff 查看器**（纯文本转义、并排/统一视图）；**R2**：仅建议列表；**R3**：隔离清单（绝不执行）；**R1**：明示「尚未实现，待真实样本设计」 | 规则 4：四级如实区分；规则 5：每动作有 diff |
| 迁移页 | migrate | items 状态表（ok/mismatch/excluded/unsupported/needs_review）；「已检查支持项匹配率」+ 分母解释；unprocessed_files/damaged_files 警示；needs_review 清单；warnings | 规则 4/5；覆盖率不完整时显著警示（与 0.1.3 起 CLI 非零退出码语义对齐，UI 标红） |
| 历史/日志页 | —（新增，规则 5 的可视化） | 本地操作历史列表；每次操作的运行日志 tail；报告文件位置提示（目录名展示，绝对路径默认折叠） | 规则 2：历史仅存本地；规则 5：日志与差异可查 |

### 4.2 API 端点清单（初版，随阶段增量实现）

```
GET  /api/health                  服务健康
GET  /api/version                 {tool, version}
POST /api/jobs/scan               {source}
POST /api/jobs/backup             {source, bundle, source_client?, source_client_version?}
POST /api/jobs/restore            {bundle, dest}
POST /api/jobs/verify             {bundle}
POST /api/jobs/repair             {source, output}
POST /api/jobs/migrate            {source, output}
GET  /api/jobs/<id>               {state, log_tail, result?, error?}
GET  /api/history                 {items: [...]}（本地历史）
GET  /                            首页（注入 token 的 meta）
GET  /static/*                    包内静态资源
```
- 所有请求带 `X-Continuity-Token` 头（启动时生成的随机值）；静态资源除外。
- 错误统一为 `{error: "<面向用户文案>", kind: "<BackupError|ScanError|...>"}` + 恰当 HTTP 码；
  引擎异常直接透传其文案（已面向用户）。
- 输出目录「已存在」等冲突：validation 层预检 + 引擎自身双重把关，错误文案一致。
- 已有任务正在排队或运行时提交新任务 → 409（`JobsBusy`，单任务串行，提示等待完成）。

---

## 5. 安全与十项规则合规设计（对照 AGENTS.md）

| 规则 | Web UI 落实方式 |
|---|---|
| 1 原始只读，修复出新品目录 | 无任何「写源目录」功能；输出目录必须不存在 + 不得嵌套源目录，前端预检 + 引擎强制 |
| 2 默认不上传 | 无上传端点、产品运行期零出站请求；历史仅存本地；页面明示承诺 |
| 3 不执行导入内容 | 前端禁用 innerHTML/eval；所有数据 textContent 转义；CSP `default-src 'self'`；静态资源仅包内 |
| 4 修复分级不伪造 | R0/R2/R3 如实展示；R1 明示未实现；无「一键全修复」这类越级按钮 |
| 5 动作有日志与差异 | 历史页 + 运行日志 + diff 查看器；报告 JSON 随结果返回 |
| 6 不删测试 | 测试只增不改；全量 105 例基线保持（104 passed + 1 skipped，见第 7 节） |
| 7 先计划、阶段停止 | 本计划即第 2 步；W1–W8 每阶段停等验收 |
| 8 无 NFT/云端 | 明确不在范围，UI 不出现相关功能 |
| 9 格式不确定不猜测 | UI 只展示引擎结论；「未知类型」原样标记，不自行推断 |
| 10 未运行不标通过 | 每阶段在受限环境真实运行全套 pytest 后才报验收 |

服务器层附加安全：仅绑定 127.0.0.1（无监听全网卡选项）；**Host 头白名单**（127.0.0.1/localhost，防 DNS rebinding）；
启动随机 token 防恶意网页对本机接口的跨站调用；无 auth 体系（本地单用户工具，MVP 明确不引入账户）；
连接空闲/慢读超时 30 秒（slowloris 防护，W2 复审修复）；客户端粗暴断连的网络级错误静默为 debug 日志，
不打印 traceback（日志刷屏防护，W2 复审修复）。

---

## 6. 分阶段拆分（每阶段一个模块；顺序与依赖；逐阶段停等验收）

> 遵守「只开发一个阶段任务」：任一时刻只开工一个阶段，该阶段验收通过后（创始人确认）才进入下一阶段。
> 每阶段验收标准均含：**受限环境真实运行**（AGENTS.md 固化的 pytest 命令，见第 8 节）全量 pytest
> （核心引擎 105 例基线 + Web UI 新增用例；W1+W2 复审修复后当前真实全量 187 collected = 186 passed + 1 skipped，2026-11-06）
> 通过，且不修改任何现有测试。

| 阶段 | 模块 | 依赖 | 内容 | 阶段验收要点（新增测试聚焦） |
|---|---|---|---|---|
| **W1** | WebUI 骨架与基础设施 | 无 | `webui` 包、`__main__`、`server.py`（路由/静态/安全头/token/Host 白名单）、`jobs.py`、`history.py`、`validation.py`、`views.py` 骨架、静态外壳（首页/导航/空页面）、`/api/health`、`/api/version` | **沙箱内 127.0.0.1 真实监听成功**（本计划最大环境风险，W1 就必须实测）；health 200；无 token 403；静态路径穿越 404；服务器可正常关闭 |
| **W2** | 扫描模块 | W1 | 扫描页 + `POST /api/jobs/scan` + 结果展示（类型统计/findings/重复/符号链接） | 对合成样本目录真实扫描；响应与直接调用 `scan_directory` 结果一致；源目录零写入 |
| **W3a** | UI 设计系统与外壳重构 + i18n（W3 子阶段） | W1、W2 | **外壳先行**：按 3.2 设计系统重构全部外壳（theme.css 双主题、组件库、动效、响应式）；W2 扫描页迁移到新设计系统；按 3.1 完成 i18n（zh-CN/en 资源表、切换器、全站静态文本走 `t()`，无硬编码字符串）；接入调研者 docs/ui-design-direction.md 结论 | 双语切换真实可用；资源表完整（key 集合一致）；亮暗主题切换；无硬编码中文残留（测试锁定）；现有 187 例全量保持 |
| **W3b** | 备份 + 校验模块（W3 功能子阶段） | W3a | 备份页 + 校验页 + 两个端点 + manifest 摘要展示；**功能页一律按新设计系统 + 双语资源表实现** | 真实创建备份包；verify 通过/篡改失败两条路径；输出目录已存在等错误路径；新页面双语与新设计系统一致 |
| **W4** | 恢复模块 | W3b（需备份包） | 恢复页 + 端点 + 恢复报告展示（新设计系统 + 双语） | 真实恢复 + 逐文件校验；目标已存在报错；错误时不残留部分目录 |
| **W5** | 修复预览模块 | W3a（复用扫描展示组件） | 修复页 + 端点 + R0 列表 + **diff 查看器** + R2/R3/R1 展示（新设计系统 + 双语） | 尾逗号样本 R0 真实修复；diff 内容正确且按纯文本转义；R2/R3 如实展示 |
| **W6** | 迁移模块 | W3a | 迁移页 + 端点 + items 状态表 + 匹配率与分母解释 + damaged/unprocessed 警示（新设计系统 + 双语） | 合成 ST 样本真实迁移；items 与 `migrate_sillytavern` 报告一致；覆盖率不完整时前端显著警示 |
| **W7** | 历史/日志与打磨 | W3b–W6 | 历史页（JSONL）、运行日志 tail、统一错误文案（双语资源表）、安全头与 token 复核、可访问性小修、更多语言扩展演练 | 历史可追查既往操作；日志含关键事件；无回归 |
| **W8** | 端到端验收支持 | W7 | 配合 qa-reviewer 的验收清单走查；可用性测试（第 9–10 周）配合修正 | 全功能链路（扫描→备份→校验→恢复→修复→迁移）真实跑通；验收清单全部达成 |

> **W3 拆分说明（外壳先行）**：W3a 是纯外壳/基建阶段，不含业务功能；W3b 起的每个功能页
> 都必须按 W3a 确立的设计系统与 i18n 资源表实现（禁止再造样式或硬编码文案）。
> W3a/W3b 各自停等验收；创始人可先行体验 W3a 的新外壳再批准 W3b 开工。

每阶段完成后：输出变更清单、真实测试结果、已知风险与下一步，**停止等待创始人验收**；通过后由创始人执行 Git commit。

---

## 7. 拟新增/修改文件清单与写作用域

### 7.1 新增文件（developer 本轮及后续写作用域：全部位于 `src/continuity/webui/`，独立新目录，零冲突）

```
src/continuity/webui/__init__.py
src/continuity/webui/__main__.py
src/continuity/webui/server.py
src/continuity/webui/api.py
src/continuity/webui/jobs.py
src/continuity/webui/history.py
src/continuity/webui/views.py
src/continuity/webui/validation.py
src/continuity/webui/static/index.html
src/continuity/webui/static/app.js
src/continuity/webui/static/style.css
```

W3a 新增（UI 设计系统与 i18n，见 3.1/3.2）：

```
src/continuity/webui/static/theme.css        # 设计令牌 + 暗色/亮色双主题
src/continuity/webui/static/ui.js            # 组件工具/t() 函数/主题切换/Toast
src/continuity/webui/static/locales/zh-CN.json   # 默认语言资源表
src/continuity/webui/static/locales/en.json      # 英文资源表
src/continuity/webui/static/locales/registry.json # 语言注册表
tests/test_webui_i18n.py                     # 资源表完整性/无硬编码文案（方案甲，届时确认）
```

### 7.2 新增测试文件（⚠ 需创始人协调：`tests/` 目录当前属外部开发者写作用域）

- 以下为**全新文件、绝不修改任何现有测试文件**；因 TEAM-COORDINATION.md 写作用域表未覆盖
  `tests/` 下的新文件，放置位置需创始人裁决（方案甲：`tests/` 下新增；方案乙：若裁决不放
  `tests/`，则改为 `src/continuity/webui/tests/` 并同步调整 pyproject 的 testpaths——后者同样动核心文件，也需协调）：

```
tests/test_webui_server.py       W1：启动/关闭、health、token、Host 白名单、静态路径穿越
tests/test_webui_jobs.py         W1：job 状态机、串行队列、错误透传
tests/test_webui_validation.py   W1：入参校验矩阵
tests/test_webui_api_scan.py     W2：扫描端点
tests/test_webui_api_backup.py   W3/W4：备份、校验、恢复端点（含篡改反例）
tests/test_webui_api_repair.py   W5：修复端点（R0 diff、R2/R3 展示数据）
tests/test_webui_api_migration.py W6：迁移端点（items、匹配率、警示）
```

### 7.3 需修改的现有文件（**全部标注「需创始人协调」，本计划默认不触碰**）

| 文件 | 拟议改动 | 说明 |
|---|---|---|
| `src/continuity/cli.py` | 可选：新增 `webui` 子命令 | 属外部开发者核心文件；**W1–W8 均不需要**（用 `python -m continuity.webui`），建议延后或不做 |
| `pyproject.toml` | 可选：`[project.scripts]` 加 `continuity-webui` 入口；若创始人改选方案 B/C 才需加依赖 | 依赖新增须创始人逐项审查 + `tools/fetch_wheels.py` 增列包名 + `.gitignore` 同步 |
| `README.md` / `CHANGELOG.md` | 各阶段验收后记录 Web UI 进度 | 由创始人或协调后更新 |
| `AGENTS.md` | 「当前状态」节更新 | 属外部开发者/创始人范畴 |
| `src/continuity/reports/` | — | **不触碰**（独立 HTML 报告为另一条线，Web UI 展示层与之解耦） |
| 现有 `tests/`、`src/continuity/` 其余文件 | — | **一律不修改** |

---

## 8. 测试策略（沿用现有 pytest 体系，真实运行，不降低 105 例基线）

1. **同一套运行方式**：所有 Web UI 测试沿用 AGENTS.md 固化命令
   （绝对路径 Python + `$env:PYTHONPATH='D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'` +
   `$env:TMP/TEMP='D:\项目1agent角色平台\.tmp'` + `& $py -m pytest`）；
   `pyproject.toml` 的 `--basetemp` 与 `no:cacheprovider` 固化配置**原样保留**。
2. **零新测试依赖**：服务器 fixture 在**随机端口（port=0）**以线程启动 `ThreadingHTTPServer`，
   teardown 时 shutdown+join；客户端用标准库 `urllib.request` 发 JSON（POST 体 UTF-8 传中文路径，
   规避 URL 编码问题）。不需要 httpx/requests。
3. **复用合成样本**：只读引用 `tests/helpers.py` 的 `make_st_sample_tree` / `make_card_png` 等
   （不改动 helpers），与现有测试共享同源样本；真实用户数据一概不用。
4. **引擎级断言**：每个端点测试断言「HTTP 响应 == 直接调用引擎函数的结果」（JSON 化后逐字段比对），
   并断言输出产物真实存在（`manifest.json`、`repair-report.json`、`migration-report.json`、`diffs/`）。
5. **错误与安全反例**：输出目录已存在 / 源不存在 / 备份期间文件变化 / verify 篡改失败 /
   无 token 403 / 静态路径穿越 404——逐条真实执行断言，禁止 mock 引擎函数装成功。
6. **回归基线**：每阶段全量运行 `pytest`（105 例基线 = 104 passed + 1 skipped，`docs/review-guide.md`
   的 10 文件清单为比对基线）；W1 落地后当前真实全量为 **163 passed + 1 skipped（164 collected）**；
   **不删除、不降低、不跳过任何现有测试**；新增用例只增不减。
7. **沙箱专项**（W1 必须实测）：127.0.0.1 监听是否被沙箱拦截、端口释放是否干净；
   若沙箱拦截监听，立即上报创始人协调运行环境，不绕过。
8. **前端层测试的现实边界**：无 Node 工具链 → 不做 DOM 级前端测试；JS 转义逻辑以纯函数形式
   保持极简，由 Python 端测试通过「响应内容不含未转义标记」类断言兜底（例如 diff 文本中的
   `<script>` 必须按纯文本传输且前端约定只走 textContent）。若创始人要求更强前端保障，
   需另行评估引入无构建测试方案（属后续协调项）。

---

## 9. 风险与待创始人确认事项

### 9.1 风险

| # | 风险 | 影响 | 对策 |
|---|---|---|---|
| R1 | 沙箱是否允许 127.0.0.1 监听端口（本计划最大环境未知数） | W1 即卡住 | W1 阶段第一件事做最小监听验证；被拦截则上报创始人协调，不绕过 |
| R2 | `tests/` 新测试文件的写作用域未覆盖 | 测试无法落地 | 已标注「需创始人协调」，见 7.2；裁决前不动手 |
| R3 | 引擎无进度回调，长任务体验粗粒度 | 大目录扫描/备份时页面只能显示「运行中」 | MVP 接受串行+状态+日志缓冲；细粒度进度需给核心引擎加回调（**需创始人协调**），列入后续候选 |
| R4 | 外部开发者后续可能调整核心引擎签名 | Web UI 依赖的 6 个公开函数变化导致测试失败 | 依赖面已收敛到 1.1 节清单；webui 测试会第一时间暴露签名漂移，报 lead 协调 |
| R5 | 修复报告含绝对路径（引擎现状，0.1.1 只对迁移报告脱敏） | 本地历史中路径可见 | UI 默认折叠展示、历史只存目录名摘要；改引擎脱敏属核心改动（**需创始人协调**），不在本轮 |
| R6 | 中文路径/中文文件名在 HTTP 层的编码坑 | 扫描含中文目录失败 | 全部走 POST JSON（UTF-8）而非 query；W2 测试专门覆盖中文路径样本 |
| R7 | 若创始人改选方案 B/C，纯 wheel 在 Python 3.14 的可获得性 | 依赖环节延误 | 选型前用 fetch_wheels 试取一次并列出清单给创始人审查；方案 A 无此风险 |

### 9.2 待创始人确认清单

1. **技术栈**：确认方案 A（推荐）或改选 B/C（此时需逐项审查新增依赖清单）。
2. **tests/ 新文件**：授权在 `tests/` 下新增 Web UI 测试文件（不改旧文件）。
3. **入口方式**：`python -m continuity.webui` 是否可接受；是否要求同时改 `cli.py` 加 `webui` 子命令（需协调）。
4. **默认端口**：已裁决为 **8777**（原 8765 被百度输入法等常驻程序占用，2026-11-06 创始人裁决；如遇占用仍可用 `--port` 指定其它端口）。
5. **历史记录位置**：开发沙箱用 `.tmp/webui-history.jsonl`、正式运行回退 `%LOCALAPPDATA%` 的方案是否可接受。
6. **与调研者衔接**：`docs/research-webui.md` 产出后，以创始人裁决为准对照修订本计划第 2 节。

---

## 10. 与外部开发者的潜在写冲突点（写给 lead 的协调清单）

1. **`tests/` 目录**：Web UI 测试文件为新增，但目录属外部开发者写作用域 → 需创始人裁决（见 7.2）。
2. **`src/continuity/cli.py` 与 `pyproject.toml`**：Web UI 入口集成（可选）会触碰核心文件 → 本计划默认
   不触碰，如需做必须创始人协调。
3. **`README.md` / `CHANGELOG.md` / `AGENTS.md`**：各阶段进度记录需协调谁写、何时写。
4. **引擎公开函数签名**：Web UI 依赖 1.1 节 6 个函数的现行签名；若外部开发者后续改动，
   需提前在协作板通报（建议 lead 把该依赖面记入共享任务板）。
5. **`src/continuity/reports/`（HTML 报告线）**：Web UI 展示层与之解耦，不占用该目录，
   但两个产出物最终面向同一批报告数据，建议 lead 在协作板标注各自的报告格式职责。

---

## 11. 下一步

1. 本计划提交创始人确认（重点：第 9.2 节清单）。
2. 创始人确认后，下一轮仅开工 **阶段 W1**（WebUI 骨架与基础设施），W1 验收后再议 W2，依此类推。
3. W1 开工首件事：受限环境真实监听 127.0.0.1 的最小验证（风险 R1），结果第一时间上报 lead。
