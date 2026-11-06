# 产品页正式改版验收清单（frontend-developer 交付三轮独立审核，创始人严格模式）

> 审核方：qa-reviewer（与 developer/frontend-developer 严格分离，独立判定）
> 审核时间：2026-11-07 01:35–02:05
> 审核范围：`src/continuity/webui/static/{index.html,style.css,app.js}` 改版 + `tests/test_webui_frontend_static.py`（71→126 例）+ `docs/frontend-redesign-brief.md`（权威规范）+ `docs/frontend-redesign-delivery.md` + `.tmp/backup-redesign/` 快照
> 依据：AGENTS.md 第 10 条（brief 为权威）、docs/frontend-redesign-brief.md 全文、docs/frontend-redesign-delivery.md
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 规范符合 + 注释审查」

### 1.1 全套 pytest 真实运行（AGENTS.md 固化命令）

| 运行 | 结果 | 说明 |
|------|------|------|
| 第 1、2 次全套 | 355 passed + **1 failed** + 1 skipped（357 collected） | 失败 = `test_webui_api_scan.py::test_scan_oversized_body_400`（Connection 类错误） |
| 单测重跑 / 仅该文件 / server+api_scan / api_scan+frontend 组合 | 全部通过（16/38/142 例） | 隔离与组合均过 |
| 第 3 次全套 | **356 passed + 1 skipped，22.94s，退出码 0** | 全过 |

**失败归因（如实记录）**：`test_webui_api_scan.py` 与 `server.py` 本轮**均未改动**（git 零 diff）；失败只在高负载全套下间歇出现、隔离/组合/重跑全套均过——为**既有 webui 测试 fixture 的时序脆弱**（服务器线程无就绪等待，见观察项 O1），**与本轮前端改版无因果**。不构成退回项，但列入观察项建议 developer 加固。

**结论：357 collected = 356 passed + 1 skipped 达成（第 3 次全套证实），基线 302 不降。**

### 1.2 业务逻辑零变化核对（app.js 快照逐函数比对 + 全文通读）

- 函数清单比对（vs `.tmp/backup-redesign/app.js`）：旧 11 个函数（api/loadOverview/showPage/clearChildren/makeLi/makeLiTagged/pollJob/renderScan/setScanError/setScanRunning/setText）**全部保留、零丢失**；新增仅 `applyTheme`（主题切换）✓
- 全文逐行通读：`api()` 的 token 封装、扫描表单提交（`/api/jobs/scan` + `X-Continuity-Token`）、`pollJob` 300ms 轮询、`renderScan` 渲染、错误/加载/禁用分支**与旧版逻辑一致**，仅文案「扫描」→「检查」（brief §五允许）✓
- index.html：`<meta name="continuity-token" content="__CONTINUITY_TOKEN__">` 注入结构保留 ✓（`test_webui_server.py` 对首页令牌/CSP/「概览」/style.css 首字节的用例全部真实通过为证）；`scan-form/scan-source/scan-run/scan-state/scan-error/scan-result/scan-summary/scan-kinds/scan-findings/scan-duplicates/scan-symlinks` 等业务 id **全部保留** ✓
- 无新增网络调用（app.js 仅既有 4 个 fetch 端点）✓

### 1.3 brief 逐条核对（docs/frontend-redesign-brief.md 权威）

| brief 条款 | 实测 | 结论 |
|-----------|------|------|
| §四 中文标题宋体系（优先 Noto Serif SC，回退 Songti SC/STSong/SimSun） | `--font-serif: "Noto Serif SC", "Songti SC", "STSong", "SimSun", serif` 精确匹配 | ✓ |
| §四 正文黑体系（Noto Sans SC/PingFang SC/Microsoft YaHei） | `--font-sans` 精确匹配 | ✓ |
| §四 禁楷体/霞鹜文楷/手写/斜体/负字距 | 实际 font-family 值零禁体（测试只查真实声明值，注释提及不误报）；`font-style: italic` 0 命中；负 `letter-spacing` 0 命中 | ✓ |
| §七 不新增粒子/光斑/装饰动画 | `css-particle/blob/noise/drift/float-up/shimmer/stagger` 全 0 命中；`@keyframes` 集合 ⊆ {spin}（唯一状态动画）；`backdrop-filter` 0 命中 | ✓ |
| §七 阴影玻璃从简 | 无 backdrop-filter/模糊玻璃，仅轻阴影 | ✓ |
| §三 双栏 Hero（左价值说明+右目录操作） | `.hero-copy`/`.hero-work` 双栏 + 断点折叠单列 | ✓ |
| §六 R0–R3 浅表面统一对齐（非厚重卡片） | `.level-list` 统一对齐 + 细分隔 + 浅表面；文字+图标（SVG，aria-hidden 装饰）+颜色三通道 | ✓ |
| §七 语义令牌集中维护、两主题角色稳定 | **15 个语义令牌**（bg/surface/surface-muted/text/text-secondary/placeholder/border/primary/primary-text/primary-hover/focus/success/warning/suggest/danger）在 light/dark 两块**各自齐全**（测试逐块断言） | ✓ |
| §七 对比度 ≥4.5:1（正文/次要/占位） | **QA 独立复算 10 组**（WCAG 相对亮度公式）与交付声称**逐位一致**：text/bg 9.75、secondary 4.59、placeholder 4.83、primary 5.00、hover 4.53（下限，交付已说明）、R0–R3 4.74–4.92、深色 13.95/4.78——**全部达标**，计算方法可信 | ✓ |
| §三 窄屏 1024/768/390/320 | 断点 1024/768/480（覆盖 390/320）+ 触控 ≥44px | ✓ |
| §八 无障碍 | role=alert/status、aria-live、aria-pressed、aria-label、aria-hidden、label[for]、焦点环、键盘操作保留 | ✓ |

### 1.4 注释审查（新代码注释与实现一致）

- app.js 头部改版说明（保留业务逻辑/新增主题与接线）与实现一致 ✓；L49「初始主题：本地记忆 > 系统深色偏好 > 默认浅色」与代码顺序一致 ✓；L159「.loading 类由 CSS 渲染转圈动画（唯一状态反馈动效，尊重 reduced-motion）」与 style.css 的 `@keyframes spin` + reduced-motion 停动画规则一致 ✓
- index.html L11「服务端 CSP 禁止内联样式与内联脚本」与实现（零内联）一致 ✓；L26「扫描已并入首页操作区」与实际结构一致 ✓
- style.css 头部规范摘要（宋体系/禁楷/不加负字距/不斜体）与实现一致 ✓
- **无错误/过时/误导注释。**

### 1.5 与上一轮（风格预览 v2 审核）比较

- 上轮发现「study 字体规范过时（Fraunces）」「preview 装饰动画」等问题——本轮 brief 明确废弃旧笔记（禁楷体/霞鹜文楷/装饰动画），产品页实现与 brief 完全一致；preview 页本轮未动（delivery §7.3 声明待创始人指示，属范围外）✓
- 新增发现：flaky 失败（O1，非本轮引入）。

**第 1 轮结论：功能与真实测试通过（357=356+1，flaky 已归因）；业务逻辑零变化；brief 逐条全符合；注释一致。**

---

## 第 2 轮「安全与十规则审计 — 真实执行 + 投毒反证」

| # | 检查项 | 真实执行结果 | 判定 |
|---|--------|--------------|------|
| B1 | 剥注释后无 eval/innerHTML/document.write | 契约测试对剥注释后 app.js 断言全过；**反证 P4**：代码中 `eval(x)` 检出、注释提及不误报 | ✓ |
| B2 | 零内联样式/脚本/事件属性（CSP 契约） | 契约测试 7 项断言全过；**反证 P1**：注入 `style=`/`onclick=` 均检出 | ✓ |
| B3 | 无外部 URL（data: 除外） | 契约测试全过；**反证 P2**：注入 `https://evil.example` 检出 | ✓ |
| B4 | localStorage 无密钥 | 仅 `cs-ui-theme` 键（主题偏好）；密钥字样 0 命中 | ✓ |
| B5 | 无新增网络调用 | app.js 全文通读：仅既有 4 个 fetch（/api/version、/api/health、/api/jobs/scan、/api/jobs/<id>），无外部域名 | ✓ |
| B6 | 无装饰动画（投毒反证） | **反证 P3**：注入 `@keyframes drift` → keyframes 集合 ⊄ {spin} 检出 | ✓ |
| B7 | 键盘焦点样式存在 | `:focus-visible` 2px 焦点环规则存在（delivery §4 声明 + style.css 实现） | ✓ |
| B8 | 图标按钮 aria-label | 主题按钮有文字 + aria-pressed；SVG 装饰图标 `aria-hidden="true"` 不重复朗读；导航 `aria-label` | ✓ |
| B9 | reduced-motion 降级真实存在 | `@media (prefers-reduced-motion: reduce)` 显式规则（停过渡与 spin，不用 !important——grep `!important` 0 命中） | ✓ |

### 十条规则逐条

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓ | 页面承诺文案真实（与引擎行为一致，无夸大） |
| 2 默认不上传 | ✓ | 零外部 URL（B3）、零新网络（B5）、页脚双语承诺 |
| 3 不执行导入内容 | ✓ | 剥注释零 eval/innerHTML/document.write（B1）、全 textContent |
| 4 R0–R3 如实分级 | ✓ | R0–R3 说明文案与引擎语义一致（brief §六「不得重新定义等级」） |
| 5 动作日志与差异 | ✓（N/A） | 页面无业务动作 |
| 6 不删测试/注释强制 | ✓ | 302 基线保持 + 126 例真实契约；注释一致（1.4） |
| 7 先计划阶段停等 | ✓ | brief→快照→改版→交付说明；停等审核 |
| 8 无 NFT/代币/钱包/云端 | ✓ | 全文 grep 0 命中 |
| 9 格式不确定不猜测 | ✓（N/A） | 无数据解析逻辑 |
| 10 未运行不标通过 | ✓ | 357 例真实运行；浏览器视觉检查如实声明受限（delivery §4/§7），未伪造 |

### 与第 1 轮结论比较

- 第 1 轮静态结论经 4 组投毒反证全部确认有效；无新增安全漏洞；O1 延续为观察项。

**第 2 轮结论：安全与十规则审计通过（CSP 契约可拦截、零外部资源、无执行导入内容、降级真实）。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归核对

- 357 collected = 356 passed + 1 skipped（第 3 次全套真实通过）；302 基线不降（前端 126 例全过，含既有预览页 71 例语义保留或增强）✓
- 测试增删理由（delivery §6）核对：删除「data-page=scan」断言因扫描并入首页（brief §三/§五，业务 id 保留于 overview 页，无功能删除）——合理；新增 55 例全部为规范硬化（零内联/字体/禁装饰/令牌/触控/断点/剥注释安全/业务保留），**无一项弱化** ✓

### 3.2 git 写作用域核对（只读命令）

- frontend 名下：`M static/{app.js,index.html,style.css}`、`M tests/test_webui_frontend_static.py`、`?? docs/frontend-redesign-brief.md`、`?? docs/frontend-redesign-delivery.md`；快照 `.tmp/backup-redesign/`（4 文件，gitignored 但存在）——**未越界**（server/api/jobs/validation/views/history、extensions/、其他 tests 零改动）✓
- 无 commit（等三轮结论，符合约定）✓

### 3.3 brief 第十节交付说明清单齐备核对

| 要求 | delivery 对应 | 结论 |
|------|---------------|------|
| 实际修改文件及职责 | §1（6 项表） | ✓ |
| 中文标题字体保证策略与回退 | §2（三道防线） | ✓ |
| 两主题语义色彩对应 | §3（15 令牌对照表 + 对比度） | ✓ |
| 窄屏与交互状态检查结果 | §4 | ✓ |
| 验证方式 | §5（node --check + 126 例 + 全套 357 + 对比度脚本，全部真实运行） | ✓ |
| 已知限制 | §7（无浏览器/无新字体/预览页未同步/主题无实时跟随） | ✓ |
| 需后续审批的字体/资源 | §8（Noto Serif SC/Sans SC vendoring 待审查 + CSP font-src 同步） | ✓ |

### 3.4 差距清单

| # | 差距 | 属性 |
|---|------|------|
| G1 | 浏览器视觉验证（1024/768/390/320 真实渲染、两主题观感、控制台）**待创始人**——沙箱无浏览器，已如实声明 | 预期（brief §十.6） |
| G2 | preview/style-preview.html 未同步（仍含旧演示注释） | 范围外（delivery §7.3 待创始人指示） |
| G3 | 字体 vendoring（Noto Serif/Sans SC）待创始人审批流程 | 预期（brief §四） |
| O1 | `test_scan_oversized_body_400` 全套下间歇 flaky（连接类；单测/组合均过，api_scan/server 未改动） | 观察项：建议 developer 为 webui 测试 fixture 加服务器就绪等待（如轮询 port connect），与前端无关 |

### 3.5 发布准备核查

- 页脚双语承诺 ✓；无夸大文案（「只读取文件信息与结构」与引擎行为一致）✓；CSP 契约（style-src/script-src 'self'）与服务端 CSP 兼容 ✓

### 与第 2 轮结论比较

- 第 3 轮新增：交付清单齐备核对（7/7）、G1–G3 差距、O1 flaky 归因结论；无新增退回项。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 规范符合 + 注释审查 | 通过（357=356+1；业务零变化；brief 全符合；注释一致） |
| 第 2 轮 安全与十规则审计（真实执行 + 投毒反证 4 组） | 通过（CSP 契约可拦截、零外部、无执行、降级真实） |
| 第 3 轮 回归与发布审查 | 通过（基线不降、写作用域合规、交付清单 7/7 齐备） |

### 退回项：**无**

### 观察/建议（非阻塞）

- O1：webui 测试 fixture 无服务器就绪等待（间歇 flaky，建议 developer 加固，与本次改版无关）；
- G1：浏览器视觉复核请创始人按 brief §十.6 执行（1024/768/390/320 + 两主题 + 控制台）；
- G2：预览页是否同步修订待创始人指示。

**一句话验收建议**：产品页正式改版三轮全部通过、无退回项——brief 逐条符合（宋体标题/黑体正文/禁装饰动画/语义令牌 15×2 稳定/对比度独立复算达标）、业务逻辑零变化、安全契约可拦截；建议交创始人验收（附创始人浏览器视觉复核 G1），通过后 commit；O1 flaky 建议随下轮 developer 加固一并处理。
