# 前端改版交付说明（frontend-redesign-delivery）

> 编制：frontend-developer（Agent Teams）｜ 日期：2026-11-07
> 依据：docs/frontend-redesign-brief.md（创始人 2026-11-07 权威规范）+ AGENTS.md 第 10 条。
> 状态：已按规范直接修改产品前端，真实运行全部测试；停等 qa-reviewer 严格三轮审核。
> 快照：改版前原文件已备份至 `.tmp/backup-redesign/`（index.html / style.css / app.js / style-preview.html，
> 均不含任何密钥/凭据）。

---

## 1. 实际修改文件及职责

| 文件 | 职责 | 主要改动 |
|---|---|---|
| `src/continuity/webui/static/index.html` | 产品首页（HTML 结构） | 「骨架展示页」→ 产品首页：Hero 双栏（左中文主标题+说明+按钮组；右真实目录操作区）、R0–R3 状态区（统一对齐/细分隔/浅表面，非厚重卡片）、服务信息块；导航保留 7 入口（扫描并入首页操作区）；零内联样式/脚本/事件属性（服务端 CSP 契约） |
| `src/continuity/webui/static/style.css` | 设计系统（全部样式集中） | 两主题语义令牌（浅=暖阳奶油·陶土 / 深=森林夜语）；宋体标题/黑体正文字体栈；按钮/输入/状态/等级区语义类；触控 ≥44px；断点 1024/768/480（覆盖 390/320）；reduced-motion 降级（不用 !important）；唯一动画 = 加载转圈（状态反馈） |
| `src/continuity/webui/static/app.js` | 交互逻辑 | **扫描业务流程原样保留**（token/API/轮询/渲染函数未重写，文案「扫描」→「检查」）；新增主题切换（localStorage 记忆 + 系统深色偏好取初始值）；新增 Hero 按钮接线（已填路径→直接提交检查；未填→聚焦输入框；「了解修复等级」→平滑滚动）；加载态加 `.loading` 类渲染转圈 |
| `tests/test_webui_frontend_static.py` | 前端静态契约测试 | 适配新结构 + 新增断言（见 §6 增删理由） |
| `docs/frontend-redesign-delivery.md` | 本交付说明 | — |
| `.tmp/backup-redesign/` | 改版前快照 | 4 个原文件备份（不可恢复点） |

未改动：后端（server/api/jobs/validation/views/history）、extensions/（ST 插件）、preview/style-preview.html（预览页本轮不在改版范围，仅做快照）、其余 tests。

## 2. 中文标题字体保证策略与回退

- 标题统一走 `--font-serif: "Noto Serif SC", "Songti SC", "STSong", "SimSun", serif`（宋体系，与规范原文一致）；
  正文/导航/按钮/标签走 `--font-sans: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif`（黑体系）。
- **防楷体三道防线**：① 栈内不含任何楷体/霞鹜文楷/手写字体；② 不斜体化（无 `font-style: italic`）、
  无负字距（无负 `letter-spacing`）、无字体合成；③ 契约测试 `test_static_font_stacks` 只读实际
  `font-family` 声明并断言禁体名单（楷/KaiTi/STKaiti/霞鹜文楷/LXGW/WenKai）不出现——注释中
  「禁楷体」属合规文档说明，测试不误报（见测试 docstring）。
- 回退路径：Windows 有 Songti SC/STSong/SimSun 覆盖中文；macOS 有 Songti SC；其余环境落到系统 serif
  ——不下载任何新字体（本轮零外部资源，CSP 亦禁止外源字体）。

## 3. 两主题语义色彩对照（含对比度）

同一套语义角色（15 个令牌）在两主题下各自定义，状态含义不随主题改变（R0 始终成功、R1 始终需确认）：

| 语义角色 | 浅色「暖阳奶油」 | 深色「森林夜语」 |
|---|---|---|
| 背景 --bg | `#FAF3E8` | `#16251F` |
| 主要表面 --surface | `#FFF9F0` | `#223A30` |
| 浅表面 --surface-muted | `#F2E7D4` | `#1B2E26` |
| 正文 --text | `#4A3B2C`（9.75:1） | `#EAF2EA`（13.95:1） |
| 次要文字 --text-secondary | `#7E6C52`（对 bg 4.59:1 / 对 surface 4.83:1） | `#A8C0B2`（8.23:1） |
| 占位符 --placeholder | `#7E6C52`（4.83:1） | `#8FA896`（4.78:1） |
| 边框 --border | `#A08A68`（对 surface 3.17:1） | `#6E927F`（3.54:1） |
| 主操作 --primary / 文字 | `#E8843C` / `#3D2B1A`（5.00:1） | `#7FBF9A` / `#12241B`（7.59:1） |
| 主操作悬停 --primary-hover | `#DB7E3A`（文字仍 4.53:1） | `#68A882`（5.81:1） |
| 焦点环 --focus | `#B95F1F`（≥4:1 可见） | `#9AD8B4`（7.49:1） |
| 成功 R0 --success | `#43703B`（对浅表面 4.74:1） | `#8CC9A8`（8.37:1） |
| 警告 R1 --warning | `#8A5908`（4.88:1） | `#E3C06B`（9.11:1） |
| 建议 R2 --suggest | `#6C5A3F`（5.41:1） | `#A8C0B2`（8.23:1） |
| 危险 R3 --danger | `#A6442C`（4.92:1） | `#E08E7E`（6.33:1） |

**对比度检查方式（可复现）**：WCAG 2.1 相对亮度公式 `L=0.2126R+0.7152G+0.0722B`（sRGB 分段线性化）
+ 比值 `(L1+0.05)/(L2+0.05)`；正文/次要文字/占位符/状态文字 ≥ 4.5:1，边框/焦点环 ≥ 3:1（非文本）。
计算脚本已真实运行：`.tmp/contrast-check*.py`（三轮，全部色值经实测后定稿，未凭目测）。
浅色主题状态色针对 R0–R3 行底 `#F2E7D4` 额外压深一档（如 R0 由 `#6E9A5B`→`#43703B`），
因为旧值在浅表面上仅 4.11:1 未达标；「主按钮悬停变深」受限：再深则按钮文字跌破 4.5:1，
故 hover 用 `#DB7E3A`（4.53:1 下限）且按下态以 `scale(.97)` 反馈，不引入更低对比度的底色。

## 4. 窄屏与交互状态检查结果

- 结构级（静态检查 + 契约测试，真实运行）：断点 `@media` 1024/768/480（覆盖 390/320）；
  480 以下按钮/表单动作纵向排列 `width:100%` 不挤压；输入框 `width:100%` + `min-height:44px`
  不横向滚动；长内容 `overflow-wrap: anywhere`；无任何固定大宽度（仅 1120px 上限与图标/图标微尺寸）。
- 交互状态（真实支持才实现）：默认/悬停（主按钮变深 `--primary-hover`、次按钮/导航浅表面）、
  按下（scale(.97)，无上浮）、键盘聚焦（`:focus-visible` 2px `--focus` 环 + 2px 偏移）、
  禁用（按钮/输入降透明 + not-allowed）、加载（`.state.loading` 转圈 + 「正在检查…」）、
  成功（「检查完成：N 个文件」摘要）、错误（role=alert 错误框）。
- 无障碍：扫描状态 `role="status"`、错误 `role="alert"`、结果区 `aria-live="polite"`、
  主题按钮 `aria-pressed` 且文字随状态变化、导航 `aria-label`、装饰图标 `aria-hidden="true"`、
  触控目标 ≥44px；reduced-motion 下全部过渡与转圈动画关闭（显式规则，不用 !important）。
- **人工浏览器检查受限说明**：受限沙箱无浏览器/截图工具，1024/768/390/320 的真实渲染与
  两主题观感、控制台报错等需创始人/QA 在浏览器人工复核（已提供结构级保证与断点规则，
  未伪造运行结果，符合 AGENTS.md 规则 10）。

## 5. 验证方式（全部真实运行）

1. `node --check app.js` → 语法通过（真实执行）；
2. `tests/test_webui_frontend_static.py` → **126 passed**（真实运行）：标签配对、零外部 URL、
   零内联样式/脚本、中文注释抽查、关键类名/id 契约、宋体/黑体栈与禁楷断言、无装饰动画、
   双主题语义令牌齐全、44px 触控、断点与 reduced-motion、扫描业务函数保留、安全断言
   （剥注释后禁 eval/innerHTML/document.write）；
3. 全套 pytest → **356 passed + 1 skipped（357 collected）**，基线 302（301+1）不降、零失败；
   其中 `test_webui_server.py` 对改版后首页的令牌注入、CSP、「概览」标签、style.css 首字节
   校验均真实通过，证明改版未破坏服务端契约；
4. 对比度三轮计算脚本真实运行（见 §3）。

## 6. 静态契约测试的增删理由（对应 brief）

- 删除「产品页含 `data-page="scan"`」：扫描已并入首页右侧目录操作区（brief §三/§五），
  业务 id 与事件绑定原样保留于 overview 页，不新增功能。
- 新增（全部为规范硬化，无一项弱化）：零内联样式/脚本/事件属性（§九 CSP 契约）；
  字体栈与禁楷/禁斜体/禁负字距（§四）；无粒子/光斑/装饰动画、仅允许 `spin` 状态动画、
  无预览演示文案 composer/focus-within（§五/§七）；两主题 15 个语义令牌逐块齐全（§七）；
  44px 触控 + 1024/768/480 断点 + reduced-motion（§三/§八）；app.js 剥注释后禁
  eval/innerHTML/document.write（安全断言增强）；扫描业务函数与端点契约保留（§二/§八）。
- 既有安全断言（零外部 URL、use strict、textContent、标签配对、注释存在、预览页全部断言）
  原样保留或增强。

## 7. 已知限制

1. 无浏览器环境：真实渲染、控制台错误、两主题观感、窄屏人工核对待浏览器复核（见 §4）。
2. 本轮未引入任何新字体（规范 §四：不下载未经批准字体），宋体/黑体均为系统回退栈，
   效果依赖操作系统预装字体。
3. 预览页 `preview/style-preview.html` 未改动（不在本轮改版范围），其中仍含旧「composer/
   焦点环/36px」演示注释——按规范 §五 该内容只允许留在预览页独立演示区，未混入产品页，
   是否同步修订预览页待创始人指示。
4. 主题初始值为「localStorage 记忆 > 系统深色偏好 > 浅色」，无系统主题实时跟随（切换按钮手动）。

## 8. 待后续审批的字体/资源事项

- 如需品牌级中文字体观感，建议后续审批 vendoring：**Noto Serif SC**（标题，SIL OFL 1.1）与
  **Noto Sans SC**（正文，SIL OFL 1.1），放入 `src/continuity/webui/static/fonts/` 并走
  AGENTS.md 依赖审查流程（逐项经创始人审查）；CSP 需同步放行 `font-src 'self'`。
- 本轮零新依赖、零新资源、零网络请求——无其他待审批项。

---

## 9. 深链引导流程（创始人路径 A）交付补充（2026-11-07）

### 9.1 修改文件及职责

| 文件 | 职责 |
|---|---|
| `src/continuity/webui/static/index.html` | 新增 `#page-emergency`（急救备份）、把 `#page-backup`/`#page-restore` 占位页升级为真实引导页；三页默认隐藏，hash 路由切换显示；全部复用既有组件类（form/field/input/btn/state/error/tip/kv），新增仅 `.guide/.steps/.guide-desc` 三处结构样式（步骤序号为静态 CSS 计数器，无任何动效） |
| `src/continuity/webui/static/app.js` | 新增深链路由（`#emergency/#backup/#restore`，兼容 `#w=xxx&auto=1` 写法）、`wireGuide` 三流程接线、`renderGuideResult` 通用安全结果渲染；把扫描轮询重构为通用 `pollJob(jobId, opts)`（扫描行为不变） |
| `tests/test_webui_frontend_static.py` | 新增 15 项深链契约断言（见 9.5），既有断言一项未弱化 |
| `docs/frontend-redesign-delivery.md` | 本补充章节 |

### 9.2 API 契约（以 src/continuity/webui/server.py 实际实现为准）

| 深链 | 端点 | 载荷 | 结果要点 |
|---|---|---|---|
| `#emergency` | POST /api/jobs/emergency-backup | `{source, output}` | `bundle` + `manifest` + `verify` 可恢复性自检 |
| `#backup` | POST /api/jobs/backup | `{source, bundle}` | `bundle` + `manifest` |
| `#restore` | POST /api/jobs/restore | `{bundle, dest}` | `restored/ok/errors/warnings/extra_files` 校验报告 |

> **与早期规划文档的差异（已按「以代码为准」对齐）**：docs/plugin-viability-plan.md 曾写
> emergency-backup「自动探测 data 目录、无入参」；后端实际实现要求显式 `{source, output}`。
> 前端据此增加两个输入字段，文案不宣称「自动探测」（测试 `test_static_guide_copy_honest` 固化）。
> 自动探测能力如后续上线，由 developer 改端点，前端再删输入。

### 9.3 Q12 安全细化（restore 永不自动开始）

- `#restore` 深链**只切换页面，绝不自动执行**：进入后必须由用户人工确认「备份包 + 目标目录」并手动点击「开始恢复」；页面明示「恢复输出到新目录，绝不覆盖任何现有数据」「本页不会自动执行任何恢复操作」。
- `auto=1` 白名单仅 `#emergency` / `#backup`，且**仅在全部必填目录均已填写时**才自动提交；存在空白字段时只聚焦第一个空白字段引导填写，绝不带空值自动提交（`tryAutoStart`）。
- 代码注释与测试断言双固化：`name !== "restore"` 排除 + 「任何情况下都不自动执行恢复」注释 + `"restore-form"` 字面引用禁用断言。

### 9.4 结果渲染（安全 + 可读）

- 全部 textContent/节点 API 构建，无 innerHTML/eval（延续规则 3 纪律）；
- 输出路径优先入摘要；后端未带路径时回退展示用户填写的目标目录；
- 标量字段 → 中文标签键值行（`已恢复文件数/校验通过/自检·不一致文件数` 等，未知字段回退原名）；
- 布尔 → 「是/否」；`verify` 自检对象扁平一层；字符串数组（errors/warnings 等）→ 标题 + 列表；
- 错误全程透传（400 校验文案、409 忙碌、任务 failed 文案原样显示于 role=alert 错误框）。

### 9.5 测试结果（真实运行）

- 新增断言：三页默认隐藏与 DOM id 完整（含 emergency-source/output）；端点与令牌头；路由/接线函数；
  Q12 restore 永不自动执行（4 项）；auto=1 白名单；文案真实性（含「不得宣称自动探测」）；
  **页面 id 唯一性**（防重复区块回归，修复过程实际抓到并消除了两处重复的旧恢复占位页）。
- `node --check app.js` 通过；`tests/test_webui_frontend_static.py` 141 passed；
  全套 pytest **400 passed + 1 skipped（401 collected）**，零失败（developer 后端 P5 测试已同步全过）。

### 9.6 已知限制

1. 沙箱无浏览器：hash 路由/深链直达/auto=1 聚焦与提交属运行时行为，结构级契约已测，
   真实交互需浏览器或 ST 插件真机验证（QA 三轮审核范围）。
2. emergency/backup 的 auto=1 在目录为空时只聚焦不提交——安全优先的刻意行为，插件侧如需
   「完全自动」须先获得目录参数（深链传参契约待定，本前端不猜测字段格式，规则 9）。
3. 结果渲染对后端新增字段自适应（未知标量/字符串数组均能展示），但嵌套对象仅展开 verify 一层。
