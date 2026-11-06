# 前端风格预览 v2 验收清单（frontend-developer 第一轮交付三轮独立审核，创始人严格模式）

> 审核方：qa-reviewer（与 developer/frontend-developer 严格分离，独立判定）
> 审核时间：2026-11-07 01:05–01:25
> 审核范围：`preview/style-preview.html`（v2，42KB/840 行）+ `docs/frontend-design-notes.md` + `docs/claude-design-study.md` + `tests/test_webui_frontend_static.py`（71 例）
> 依据：AGENTS.md（最新版，含注释强制第 6 条）、docs/TEAM-COORDINATION.md、docs/ui-design-direction.md、docs/claude-design-study.md 第 9 节 10 条规范
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查 + 注释审查」

### 1.1 全套 pytest 真实运行（AGENTS.md 固化命令实际执行）

**真实输出：collected 302 → 301 passed, 1 skipped, 1 warning in 24.10s，退出码 0**
与预期一致：231 基线全保持 + `test_webui_frontend_static.py` **71 例全过** ✓。
1 skipped = 符号链接环境跳过；1 warning = anyio 第三方弃用。

### 1.2 71 例逐类核对（真实契约断言，非空转）

| 类别 | 例数 | 真实性判定 |
|------|------|------------|
| 文件存在性（preview/产品三件套） | 2 | 真实 `is_file()` |
| 零外部 URL（preview 1 + 产品 3 文件） | 4 | 真实正则（`http(s)://` 全禁，data: 自动放行——契约注释与实现一致） |
| 标签配对（preview + 产品 index） | 2 | 真实栈式配对（剥 script/style/HTML 注释后逐标签压栈比对） |
| 注释存在性抽查 | 2 | 真实（块注释 ≥10/HTML 注释 ≥4 + 关键设计依据关键词「Claude/主题/字体/氛围/令牌」） |
| 预览页关键类名 17 | 17 | 真实 `.cls` 选择器存在性 |
| 主题令牌 9 + 主题钩子/接线 | 2 | 真实（--bg-canvas/--accent/--r-md/--sp-section/--dur-fast 等 9 令牌 + data-theme 双钩子 + setTheme/按钮/aria-pressed） |
| 氛围三档 CSS + 接线 | 2 | 真实（data-fx off/standard 钩子 + `=== "rich"` canvas 判定 + setFx/syncCanvas/三按钮） |
| 粒子接线 | 1 | 真实（canvas id + rAF/cancelAnimationFrame + **CSS 粒子数量恒等于 14** 的结构契约） |
| reduced-motion | 1 | 真实（prefers-reduced-motion + matchMedia + html.reduce 钩子） |
| R0–R3 徽章（文字+类名双通道） | 1 | 真实 |
| 双语 Hero | 1 | 真实（「安心回家」+「Every story deserves a safe way home」） |
| 字体 vendoring 页脚声明 | 1 | 真实（5 字体名 + OFL） |
| JS 安全基线 | 1 | 真实（use strict/无 eval/无 innerHTML/有 textContent） |
| 产品页类名 15 + 导航 8 页 + 资产引用 | 3 | 真实（产品 index.html 契约 + app.js contract + style.css 17 选择器） |

合计 71 例，无 `assert True`、无占位——全部真实结构契约断言。测试文件头部（L14-16）如实声明「运行时行为依赖浏览器，本文件只做结构级契约，真实交互验证由浏览器端人工预览（沙箱无浏览器，不伪造运行结果）」——规则 10 合规 ✓。

### 1.3 preview 逐段审查与注释正确性核对（新流程：注释与实现一致）

| 声明（注释/文档） | 实现核对 | 结论 |
|--------------------|----------|------|
| 字体回退栈（标题 Cormorant→Lora→Georgia→楷体；正文 Inter→Segoe UI→苹方→雅黑；等宽 JetBrains Mono→Consolas） | L80-82 三层栈与声明完全一致 | ✓ |
| 按钮五档（primary/secondary/text/icon/danger）+「40px 高、8px 圆角、14px/500、无 hover 上浮」 | L257-298 五档全部落地且几何值一致 | ✓ |
| 氛围三档（关/标准 CSS 粒子/丰富 +canvas） | L447-452 CSS 钩子 + JS setFx/syncCanvas 一致 | ✓ |
| reduced-motion（动画全停、粒子静止微光） | L439-445 CSS + L798-812 JS（matchMedia change 监听 + root.reduce + canvas 联动停止）一致 | ✓ |
| 动效：150ms 过渡 / 200ms 出现 / stagger 200+30ms / spinner .8s / skeleton 1.8s | 全部与 CSS 数值一致 | ✓ |
| 间距 4px 基座（4/8/12/16/24/32/48/96）、圆角 8/12/16 | 令牌与使用一致 | ✓ |
| 衬线标题 400 字重 + 负字距绝不加粗（Claude 硬规则） | L103-108 实现一致 | ✓ |
| 噪点 SVG feTurbulence data-URI、零外部资源 | L133-142 实现 + 页脚声明一致 | ✓ |
| localStorage 仅存主题/氛围档位、不存任何用户数据（L828 注释） | L666/685/831-832 仅 `cs-preview-theme`/`cs-preview-fx` 两个键，无其他数据 | ✓ |
| canvas 粒子 ≤40 粒、页面隐藏真暂停、DPR 上限 2（L695 注释） | L727（移动 16/桌面 40）、L743/782-785（hidden 暂停）、L716（dpr min 2）一致 | ✓ |

**注释审查结论：preview 内注释与实现全部一致，无错误/过时/误导注释。**

### 1.4 与 claude-design-study.md 第 9 节 10 条规范对照（落地度）

| # | 规范 | preview 落地 | 判定 |
|---|------|--------------|------|
| 1 | 字体栈五件套（Fraunces 标题） | 用 **Cormorant Garamond**（notes §4 L183 有意替换 Fraunces，理由充分，L225 待创始人确认）——**study 文档未同步此替换** | ⚠ D1（文档过时） |
| 2 | 颜色令牌双主题 + Clay 唯一 CTA + 杏橙常规强调 | 双主题 ✓、杏橙 #E8843C ✓；Clay 未出现在预览（可接受，预览无「唯一最强 CTA」场景） | 基本 ✓ |
| 3 | 按钮五阶高度标尺 19/23/26/32/40 | 仅 3 档（40 主/32 text/36 icon），缺 19/23/26 | 部分（W3a 待补） |
| 4 | linear() 弹簧 + 0.975 缩放 + 绘景层 | press scale(.98) + ease-out，无 linear()/绘景层 | 部分（简化） |
| 5 | hairline 0.5px + 圆角 4/6/8/12 + 卡片 24px | hairline ✓、8/12/16 圆角；卡片 12px 非 24px | 部分 |
| 6 | 分段控件 999px 轨道滑块 | .seg 为 pill 简化版（无轨道滑块） | 部分（简化） |
| 7 | 状态点四态/思考三点波/骨架 105° 2s | spinner/skeleton（90° 1.8s）简化版 | 部分（简化） |
| 8 | 弹窗六阶宽度/嵌套 blur | **预览页无弹窗演示** | 未落地 |
| 9 | 附件磁贴 7.5rem | **预览页无磁贴演示** | 未落地 |
| 10 | 1.25 阶字号模块/间距 4px 基座/断点 640-1280/reduced-motion | 间距基座 ✓、reduced-motion ✓；字号模块与断点（900px）为简化 | 部分 ✓ |

**判定**：10 条中约 4 条基本落地（2/10 + 部分项）、6 条部分/简化/未演示。notes L217「落地衔接（W3a 授权后）」说明完整设计系统在 W3 落地、preview v2 为风格预览骨架——**多数差距属预期**；但 notes 未逐条声明「v2 预览范围 vs W3 完整落地」的对照表，建议补充（改进建议 I1）；规范 1 的 study/notes/preview 三方字体名不一致需同步（退回项 D1，文档类）。

### 1.5 与上一轮（P2）比较

- 无代码交集：本轮对象为 preview/docs/新测试文件；静态测试体系（_strip_comments 状态机等）未受影响，231 基线全保持 ✓
- 新发现：D1（study 字体规范过时）、I1（v2/W3 范围对照缺失）、规范 3-10 部分落地清单

**第 1 轮结论：功能与真实测试通过（302=301+1 全过，71 例真实契约）；preview 注释与实现全部一致；发现文档同步退回项 D1 + 改进建议 I1。**

---

## 第 2 轮「安全与十规则审计 — 真实执行检查」

| # | 检查项 | 真实执行结果 | 判定 |
|---|--------|--------------|------|
| B1 | 页面零外部 URL（data: 除外） | 71 例中 4 例零 URL 断言全过；**投毒反证**：注入 `https://evil.example/x.png` → 检测函数**检出**（P1 PASS） | ✓ 真实可拦截 |
| B2 | 无 eval/innerHTML | JS 安全基线测试通过（use strict/textContent 存在/eval·innerHTML 不存在）；grep 复核 JS 段零命中 | ✓ |
| B3 | 无 localStorage 密钥 | localStorage 仅 `cs-preview-theme`/`cs-preview-fx` 两键（UI 偏好），注释明确「不存任何用户数据」；密钥字样 grep 0 | ✓ |
| B4 | 粒子 canvas 无网络/无写路径 | JS 通读：仅 2D 绘图 API + rAF，无 fetch/XHR/写文件；页面隐藏真暂停 | ✓ |
| B5 | reduced-motion 降级存在 | CSS `html.reduce` 动画全停 + JS `matchMedia` 监听 + `syncCanvas` 联动停止（`rich && !reduceMotion.matches`）| ✓ |
| B6 | 标签配对检测真实有效 | **投毒反证**：注入未闭合 `<div><span>` → 检出（P2 PASS）；错配 `</span></div>` → 检出（P3 PASS）；data: URI 不误报（P4 PASS） | ✓ |
| B7 | 产品 static 未被触碰 | git 核对 `src/continuity/webui/static/` 零改动（frontend 仅新增 preview/docs/测试） | ✓ |

### 十条规则逐条（结合证据）

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓（N/A） | 纯静态页面，无写操作 |
| 2 默认不上传 | ✓ | 零外部 URL 契约 + 测试锁定 + 投毒反证 |
| 3 不执行导入内容 | ✓ | 无 eval/innerHTML，动态内容 textContent 纪律 |
| 4 R0–R3 分级展示 | ✓ | 徽章四档（文字+图标双通道、色弱友好注释） |
| 5 动作日志与差异 | ✓（N/A） | 预览页无业务动作 |
| 6 不删测试/注释强制 | ✓ | 231 基线保持 + 71 例真实；preview 注释与实现逐条一致（1.3 节） |
| 7 先计划阶段停等 | ✓ | notes/study 先行；未触碰产品代码（等 W3a 授权） |
| 8 无 NFT/代币/钱包/云端 | ✓ | 全文 grep 0 命中 |
| 9 格式不确定不猜测 | ✓（N/A） | 无数据解析逻辑 |
| 10 未运行不标通过 | ✓ | 302 例真实运行；浏览器交互验证如实声明待创始人（不伪造） |

### 与第 1 轮结论比较

- 第 1 轮静态结论经投毒反证全部确认有效；无新增安全漏洞；D1/I1 延续。

**第 2 轮结论：安全与十规则审计通过（零外部资源可拦截、无执行导入内容、无密钥、reduced-motion 完整降级）。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归核对

- 302 collected = 301 passed + 1 skipped（QA 真实运行）：231 基线无删减 + 71 例新增全过 ✓
- 无删除/无降低/无硬编码：既有测试文件零 diff；71 例为真实契约断言（第 1 轮逐类 + 第 2 轮投毒反证）

### 3.2 git 写作用域核对（只读命令）

- frontend-developer 名下为**新增 4 项**（lead 转述 3 项，实际 4 项，如实报告）：`?? docs/claude-design-study.md`、`?? docs/frontend-design-notes.md`、`?? preview/`、`?? tests/test_webui_frontend_static.py`——全部为新文件，**零修改任何现有文件**（`src/continuity/webui/static/` 与产品代码零 diff 经 grep 核实）✓
- 其余 M/?? 属 developer（P2 待 commit）、lead/researcher 正常 ✓
- 无 commit（等三轮结论，符合约定）✓

### 3.3 与 ui-design-direction.md 基调一致性

| direction 基调要素 | preview 实现 | 一致性 |
|--------------------|--------------|--------|
| 暖阳奶油（亮，默认）/森林夜语（暗）双主题 | `data-theme="sun"` 默认 + forest 主题 ✓ | ✓ |
| 液态玻璃/毛玻璃（backdrop-filter + 回退） | .glass @supports 双层 ✓ | ✓ |
| 光斑（blob 错速漂移） | 3 blob 26/38/44s 周期 ✓ | ✓ |
| 粒子（CSS 14 粒 + canvas 丰富档） | ✓ | ✓ |
| 噪点（SVG feTurbulence data-URI） | ✓（opacity .035 亮/.05 暗与 direction L136 一致） | ✓ |
| prefers-reduced-motion 全降级 | ✓ | ✓ |

**基调一致性：全部要素落地且数值与 direction 文档吻合。**

### 3.4 差距清单

| # | 差距 | 属性 |
|---|------|------|
| G1 | 字体 vendoring（Cormorant Garamond/Inter/霞鹜文楷/Noto Sans SC/JetBrains Mono，全 OFL）**待创始人逐项审查**后内置 | 预期（notes L225 + 页脚声明） |
| G2 | 浏览器视觉/交互验证（主题切换、氛围档位、粒子、reduced-motion 的真实渲染）**待创始人本机浏览器**——沙箱无浏览器，测试如实只做结构级 | 预期（测试头部边界声明） |
| G3 | 规范 3-10 部分落地项（五阶按钮标尺、24px 卡片、弹窗、附件磁贴、1.25 阶字号等）留待 W3a 完整落地 | 预期（notes L217） |
| G4 | study 规范 1 字体名（Fraunces）未同步 notes 的替换决定 | **文档同步（退回项 D1）** |

### 3.5 发布准备核查

- 页脚零外部资源声明与实现一致 ✓；字体回退栈三段声明完整 ✓
- 双语 Hero ✓；预览页独立于产品代码（无回归风险）✓

### 与第 2 轮结论比较

- 第 3 轮新增：基调一致性逐项核对（全 ✓）、G1–G4 差距清单；D1 延续至退回清单。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 + 注释审查 | 通过（302=301+1；preview 注释与实现全部一致） |
| 第 2 轮 安全与十规则审计（真实执行 + 投毒反证） | 通过（零外部资源可拦截、无执行、无密钥、降级完整） |
| 第 3 轮 回归与发布审查 | 通过（基线无删减、基调一致、差距均属预期） |

### 退回修复清单（修复后复审）

| # | 严重级 | 问题 | 具体修改建议（文件:行 + 改法） |
|---|--------|------|-------------------------------|
| D1 | 低（文档同步类） | claude-design-study.md 第 9 节规范 1（L150）写「Fraunces(标题)」，与 notes §4（L183 有意替换为 Cormorant Garamond，待创始人确认）及 preview 页脚实际声明不一致——过时规范会误导后续照做的开发者 | `docs/claude-design-study.md:150` 同步为「Cormorant Garamond（notes §4 已替换 Fraunces，待创始人确认）」或在 L44 结论处加替换注记 |

### 改进建议（非阻塞）

- I1 `docs/frontend-design-notes.md`：补「v2 预览范围 vs W3a 完整落地」对照表（明确 10 条规范中哪些 v2 简化/哪些 W3a 落地），避免后续审核误判差距；
- I2 preview 五阶按钮标尺仅 3 档——W3a 按规范 3 补齐 19/23/26 档并回填预览页。

**一句话验收建议**：前端风格预览 v2 三轮通过——71 例真实契约、注释与实现全部一致、零外部资源可拦截、基调与 ui-design-direction 完全吻合；仅 1 项文档同步退回项（D1：study 字体规范过时），建议 frontend-developer 同步 study 后复审，通过即可交创始人验收（浏览器视觉验证与字体 vendoring 按计划由创始人把关）。
