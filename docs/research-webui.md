# 本地 Web UI 技术选型调研报告（B 报告）

> 调研人：researcher（Agent Teams）
> 日期：2026-11-06 ｜ 性质：技术调研，只出报告、不落地任何功能
> 读者：开发者（developer）与创始人；本报告只给选项与推荐结论，最终选型由创始人决策。
> 网页内容仅作为数据引用，不是对本项目的指令。

---

## 1. 决策约束（硬性前提，来自 AGENTS.md 与项目现状）

1. **本地优先**：UI 只在本地运行，任何数据默认不上传（AGENTS.md 规则 2）。
2. **Python 3.14.5**（系统安装，固定绝对路径调用），沿用现有 CLI 引擎（`src/continuity/`：扫描、备份/恢复、修复预览、迁移，pytest 104 例）。
3. **沙箱内 pip 不可用**：新依赖必须走 `tools/fetch_wheels.py`（当前实现只下载/解压 `py3-none-any` 纯 wheel 到 `.deps2`），且**每项依赖逐项经创始人审查**；`.gitignore` 需同步。
4. 现状资产：**Pydantic 2.13.4 已系统级安装**（项目统一数据模型基于 pydantic v2），pytest 9.2.0 在工作区 `.deps2`。
5. 前端必须无 CDN、无 npm 构建链依赖（本地优先 + 沙箱约束）；不执行用户内容中的脚本/HTML（规则 3）。

---

## 2. 方案总览对比

| 维度 | A. 纯标准库 http.server + 静态前端 | B. Flask 3.1.x（WSGI） | C. FastAPI + uvicorn（ASGI） | D. Tauri 2 + Python sidecar | E. Electron + Python 子进程 |
|---|---|---|---|---|---|
| 新增 Python 依赖 | **0** | 7（全纯 wheel） | ~8（全纯 wheel；pydantic 复用系统已装） | 同 B/C + 打包工具链 | 同 B/C + Node 工具链 |
| Python 3.14 兼容 | 天然（标准库） | ✅ 纯 wheel；conda 已有 py314 构建 | ✅ Starlette ≥0.48 官方支持 3.14 | 取决于后端方案 | 取决于后端方案 |
| 与 CLI 引擎集成 | 直接 import，零阻抗 | 同步 WSGI，直接 import | ASGI 包装，异步留余地 | sidecar 进程 + IPC/HTTP | 子进程 + IPC/HTTP |
| pydantic 复用 | 手动 json 序列化 | 手动或用 pydantic | **API 模型与项目模型同源** | 同 B/C | 同 B/C |
| 开发量（UI 壳） | 中高（手写路由/静态/上传/流式） | 低 | 中 | **高**（Rust 壳 + 生命周期 + IPC） | 高（主/渲染进程） |
| 打包体积（桌面） | 无壳（浏览器访问） | 无壳 | 无壳 | 小（几 MB，WebView2 系统自带） | 大（100 MB+ Chromium） |
| 沙箱内可开发/构建 | ✅ | ✅ | ✅ | ❌（Rust/Node/PyInstaller 需完全权限） | ❌ |
| 主要风险 | 功能简陋、后期返工 | 本地单用户足够，多并发弱 | uvicorn Windows asyncio 注意点少 | 工具链重、构建不可在沙箱复现 | 体积/内存/打包链重 |
| 适用阶段 | 验证性原型 | MVP 稳健选项 | **MVP 推荐** | MVP 验证后作为打包分发 | 不建议 |

---

## 3. 各方案详述

### A. 纯标准库（`http.server.ThreadingHTTPServer` + 静态前端）
- **依赖成本**：0 新增依赖；Python 3.14 标准库即包含 `http.server`、`wsgiref`（可简化 WSGI 风格路由）、`json`、`hashlib`（可复用于摘要校验）。
- **开发量**：路由分发、静态文件带 MIME 与范围请求、JSON API、大文件扫描进度（可用 SSE 或轮询）均需手写；约等于自造微型框架，但本工具 API 面窄（扫描/备份/恢复/预览/迁移 5 类动作），量级可控。
- **风险**：无模板引擎、无自动重载、安全细节（路径穿越防护等）要自己兜底；后续若加页面多起来，返工成本高。
- **评价**：零依赖是硬约束下的最安全选项；适合「先验证 UI 交互再决定是否引入框架」的原型期。

### B. Flask 3.1.x（WSGI 轻量框架）
- **依赖成本**：`flask, werkzeug, jinja2, click, itsdangerous, markupsafe, blinker` 共 7 项，**全部为 `py3-none-any` 纯 wheel**（[flask-3.1.3-py3-none-any.whl](http://www.ravenports.com/catalog/bucket_8F/python-Flask/v14/)、[werkzeug-3.1.9-py3-none-any.whl](https://github.com/Ravenports/Ravenports/blob/master/bucket_B3/python-Werkzeug)），与现有 `fetch_wheels.py` 的「只取纯 wheel」逻辑完全匹配，直接扩 `PKGS` 列表即可；Python 3.14 兼容有独立发行版构建佐证（conda-forge `flask-3.1.2-py314` 包，依赖 `python >=3.14`：[anaconda.org 记录](https://anaconda.org/main/flask/files/modal/info/68efd164b701a2bda3bc16d0)）。
- **开发量**：低；路由/模板（Jinja2 可用于渲染 diff 报告页）/静态文件/session 开箱即用；同步调用 CLI 引擎零改造。
- **风险**：自带开发服务器（Werkzeug）对本地单用户足够，但官方不建议生产部署——本产品是本地单用户工具，此风险实质不存在；框架较「老」，未来若要做 WebSocket 实时进度需换 gevent/eventlet（不建议，见 C）。
- **评价**：稳妥、依赖小、审查面小（7 个纯 Python 包）。若创始人倾向「最少新增依赖 + 纯同步模型」，选 B。

### C. FastAPI + uvicorn（ASGI，推荐）
- **依赖成本**：`fastapi, starlette, anyio, sniffio, idna, click, h11, typing-extensions` 约 8 项，全部纯 wheel；`pydantic` **复用系统已装的 2.13.4**（0 个新增 C 扩展）。关键版本证据：
  - Starlette **0.48.0（2025-09-13）发布说明明确「Add official Python 3.14 support」**（[release notes 引用](https://dependabot.ecosyste.ms/hosts/GitHub/repositories/virangdoshi%2Ffastapi/issues/86)）；
  - FastAPI 0.135.3 的依赖解析存在 `python_full_version >= '3.14' and sys_platform == 'win32'` 标记（[uv.lock 快照](https://huggingface.co/api/resolve-cache/spaces/anujsharma2007/farmer-advisory-env/915c216acec608dbbf069bacc441794f9a42fc73/uv.lock?download=true)），即官方已覆盖 3.14 + Windows；
  - uvicorn 不装 `[standard]` 即全纯 Python（h11 协议）；可选加速 `httptools 0.8.0` 已有 `cp314-cp314-win_amd64.whl`（2026-05 发布，[wheel 记录](https://raw.githubusercontent.com/damien-robotsix/robotsix-file-hub/refs/heads/main/uv.lock)）——MVP 阶段不需要。
- **开发量**：中；把现有 pydantic 模型（`ScanFinding`、清单、报告等）直接作为 API 请求/响应 schema（`model_validate`/`model_dump` 已在用），CLI 与 Web 共享同一套验证；OpenAPI 自动文档（`/docs`）可直接供 qa-reviewer 做验收对照。
- **风险**：新增依赖比 Flask 多 1–2 个；uvicorn 在 Windows 用默认事件循环即可（本地单用户）；测试用 `starlette.testclient`（依赖 `httpx` + `httpcore` + `h11` + `certifi`，均为纯 Python）或直接 socket 级测试。
- **评价**：与项目现有技术栈（pydantic v2）同源、类型/验证边界一致，是「延续 CLI 引擎」成本最低的框架路线。**本报告首推 C，B 为备选。**

### D. Tauri 2 + Python sidecar（桌面壳方案）
- **依赖成本**：Rust 工具链 + Node + 打包器（PyInstaller/Nuitka 或单文件 exe）；运行期依赖 Windows WebView2（Win10/11 系统自带）。社区已有成熟先例：Tauri sidecar 打包 Python 后端（PyInstaller `COLLECT` → `src-tauri/binaries/`，见 [vibebells 部署方案](https://raw.githubusercontent.com/paintcode/vibebells/refs/heads/main/DESKTOP_DEPLOYMENT_PLAN_TAURI.md)）；工程化注意点（sidecar 生命周期、父进程监视防孤儿、单实例插件、关窗确认）见 [tavotto ADR 0002](https://github.com/tavotto/tavotto/blob/ee1bc23086edb6019b1ca221a76df03aa8220230/docs/adr/0002-tauri-desktop-shell.md)。
- **开发量/风险**：高。**当前受限沙箱内无法构建**（Rust/Node/PyInstaller 均需完全权限与大量下载），开发-验证闭环无法在现有环境复现；UI 仍是 WebView 内网页，前端工作量与 B/C 相同，额外付出全部在壳与打包链上。
- **收益**：安装包小、桌面体验（窗口管理/单实例/无浏览器端口暴露）。
- **评价**：MVP 阶段**不建议**；待 Web UI 验收后，如需「双击即用的桌面版」，由创始人在完全权限环境另立项评估（届时后端仍沿用 B/C 选型，作 sidecar）。

### E. Electron（对比项，不推荐）
- 打包体积 100 MB+、内存占用高、需 Node 工具链；同样无法在沙箱内构建。仅在团队已深度依赖 Node 时才有优势，本项目（Python 优先）无此前提，故排除。

---

## 4. 前端策略（与后端选型解耦，三方案通用）

- **无 npm、无 CDN、无构建**：纯静态 HTML/CSS/JS 由后端直接伺服；交互复杂度低时用原生 JS 即可。
- 若需要响应式状态管理，可**vendoring 单个 MIT 许可的小体积库**（如 petite-vue / Alpine.js，单文件约 10–20 KB）——下载行为等同新依赖，须走创始人审查流程并固定版本、记录来源 URL。
- 前端不得执行/渲染任何来自角色卡或聊天内容的 HTML/脚本（规则 3）；所有用户内容一律转义显示。
- 长任务（大目录扫描/备份）建议「请求-轮询任务状态」或 SSE 进度，不引入 WebSocket 依赖。

---

## 5. 推荐结论（供创始人决策）

1. **MVP 阶段（提示词 8）**：采用 **C（FastAPI + uvicorn，纯 wheel，无 [standard] 扩展）**；如创始人希望新增依赖最少，**B（Flask）** 为等价备选；**A（纯标准库）** 仅在坚持「零新依赖」时启用。
2. **依赖落地方式**：扩 `tools/fetch_wheels.py` 的 `PKGS` 列表（C 方案 8 项 / B 方案 7 项，均为 `py3-none-any`，与脚本现有过滤逻辑一致），逐项列清单交创始人审查，同步 `.gitignore`（AGENTS.md 既定流程）。
3. **桌面壳（D/E）**：推迟到 MVP 验收后，仅作为打包/分发专项重新评估；不在本轮开发范围内。
4. **测试**：Web 层用 pytest + TestClient/socket 级测试接入现有 104 例套件；任何未真实运行的测试不得标记通过（规则 10）。

---

## 6. 来源

- Python 3.14 兼容性证据：[Starlette 0.48.0 release notes（官方 3.14 支持）](https://dependabot.ecosyste.ms/hosts/GitHub/repositories/virangdoshi%2Ffastapi/issues/86)、[fastapi/uv.lock（3.14 + win32 解析标记）](https://huggingface.co/api/resolve-cache/spaces/anujsharma2007/farmer-advisory-env/915c216acec608dbbf069bacc441794f9a42fc73/uv.lock?download=true)、[httptools 0.8.0 cp314-win_amd64 wheel 记录](https://raw.githubusercontent.com/damien-robotsix/robotsix-file-hub/refs/heads/main/uv.lock)、[conda-forge flask-3.1.2 py314 构建](https://anaconda.org/main/flask/files/modal/info/68efd164b701a2bda3bc16d0)、[Ravenports Flask 3.1.3（3.14 变体）](http://www.ravenports.com/catalog/bucket_8F/python-Flask/v14/)、[Ravenports Werkzeug 3.1.9](https://github.com/Ravenports/Ravenports/blob/master/bucket_B3/python-Werkzeug)
- 桌面壳方案参考：[vibebells Tauri + PyInstaller sidecar 部署方案](https://raw.githubusercontent.com/paintcode/vibebells/refs/heads/main/DESKTOP_DEPLOYMENT_PLAN_TAURI.md)、[tavotto ADR 0002（Tauri 2 + Python sidecar 工程细节）](https://github.com/tavotto/tavotto/blob/ee1bc23086edb6019b1ca221a76df03aa8220230/docs/adr/0002-tauri-desktop-shell.md)
- 项目内依据：`AGENTS.md`（环境说明/沙箱对策）、`tools/fetch_wheels.py`（现有纯 wheel 下载-解压机制）、`src/continuity/models.py`（pydantic v2 模型）

> 备注：框架版本与 wheel 可用性随时间变化，实施前应让开发者用当前日期复核 PyPI 最新版本号与许可证（均为 BSD/MIT 系）。
