# 前端设计笔记：Claude 网页端设计提取 × 暖色基调融合（frontend-design-notes）

> 编制：frontend-developer（Agent Teams）｜ 日期：2026-11-07（第一轮）
> 定位：创始人指令「字体设计、按键排布、交互方式严格参照 Claude 网页端（Claude.ai）」的
> 提取依据 + 与已确认美学基调「有生命力的温暖朦胧」（docs/ui-design-direction.md）的融合方案。
> 约束：零构建原生 JS + 纯 CSS（方案 A）；所有资源可 vendoring、无 npm/CDN；引入需许可证登记。
> 说明：Claude 未公开官方设计系统文档，以下要点提取自第三方对 claude.com / claude.ai 的公开
> 逆向/整理资料（来源逐条标注）；Copernicus / Tiempos / Styrene 为商业授权字体，只作参照不引入。

---

## 1. Claude 网页端设计要点提取（逐条标注来源）

### 1.1 字体系统（衬线标题 + 无衬线正文）

| 角色 | Claude 使用 | 关键参数 | 来源 |
|---|---|---|---|
| 大标题（display） | Copernicus / Tiempos Headline（衬线，商业字体） | 字重 **400（从不加粗）**；负字距 -0.3 ~ -1.5px；行高 1.05–1.2；字阶 28/36/48/64 | [claude-design-card/DESIGN.md](https://github.com/geekjourneyx/claude-design-card/blob/main/DESIGN.md) |
| 小标题（title） | StyreneB（无衬线） | 字重 500；字阶 16/18/22；行高 1.3–1.4 | 同上 |
| 正文 | StyreneB → 近似替代 **Inter** | 400；16px（body-md，行高 1.55）/ 14px（body-sm） | 同上 |
| 标注/按钮/导航 | StyreneB | 12px/500/字距 1.5px（大写标签）；13px/500；14px/500（按钮、导航） | 同上 |
| 代码 | JetBrains Mono | 14px/400，行高 1.6 | 同上 |
| 回退栈 | display：Tiempos Headline → Garamond → Times New Roman；正文：Inter → -apple-system → Segoe UI → Roboto | — | 同上 |

- 硬规则：**衬线标题用 400 字重 + 负字距，绝不加粗**；正文与 UI 全用无衬线；正文西文禁用几何感太强的 Helvetica/Arial 系。
- **官方近似替代（OFL，可 vendoring）**：衬线标题 = **Cormorant Garamond**（weight 500 + -0.02em 字距最接近），备选 EB Garamond / Lora；正文 = **Inter**（与 StyreneB 同为屏幕阅读优化的人文无衬线）。来源：同上「Note on Font Substitutes」。
- 已知缺口：Copernicus/Styrene 无公开网络字体，OFL 替代为社区共识方案。来源同上「Known Gaps」。

### 1.2 色彩与表面（我们主题恰好同构）

| 令牌 | Claude 值 | 说明 | 来源 |
|---|---|---|---|
| canvas | `#faf9f5` | **暖奶油画布**（刻意非冷白，与本项目暖阳奶油同方向） | claude-design-card/DESIGN.md |
| ink / body / muted | `#141413` / `#3d3d3a` / `#6c6a64` | 暖墨正文、弱化层级 | 同上 |
| primary（珊瑚） | `#cc785c`；press 态 `#a9583e`；禁用 `#e6dfd8` | 唯一强调色，**克制使用**：主 CTA 与大色块，不铺满 | 同上 |
| hairline | `#e6dfd8` | 1px 边框基调（「边框是一级高度差，不是墨线」） | 同上 |
| surface-card | `#efe9de` | 比画布深一档的卡片底 | 同上 |
| 表面节奏 | 奶油画布 / 奶油卡 / 深色产品表面交替 | 色块分层优先，阴影极少 | 同上 |
| 产品端（claude.ai） | 白底卡 + **0.5px** 边框；禁渐变、禁装饰阴影（仅功能焦点环） | 更克制的对话界面 | [agent 仓库 claude-guidelines/ui_components.md](https://github.com/dwsy/agent/blob/291e371f7dc7a7957f0141d2a5558285231eaa9a/extensions/generative-ui/claude-guidelines/sections/ui_components.md) |

- 结论：**Claude 的奶油画布 + 暖珊瑚强调与我们已确认的「暖阳奶油」基调高度同构**——融合成本低，
  只需把按钮/输入/间距骨架换成 Claude 规格，颜色继续用我们已通过的对比度达标令牌。

### 1.3 按钮样式与层级

| 档位 | 几何 | 颜色与状态 | 来源 |
|---|---|---|---|
| primary | **高 40px、圆角 8px、padding 12×20、14px/500** | 实底 primary；**hover 不额外变化，press/active 变深**（primary-active）；禁用去饱和 | claude-design-card/DESIGN.md |
| secondary | 与 primary 同几何 | 画布底 + 1px hairline 边；press 变深 | 同上 |
| secondary-on-dark | 同几何 | 深表面内不反转为浅底，用更深一档深色 | 同上 |
| text-link | 内联文字按钮（无底无边） | primary 色文字，press 下划线 | 同上 |
| icon-circular | **36px 圆形** | 画布底 + hairline 边 | 同上 |
| 产品端按钮 | 透明底 + 0.5px 边框 | **hover 上浅色底、active scale(0.98)** | ui_components.md（同上） |
| 触控 | 主/次按钮 ≥ 40×40px | 图标钮 36px（略低于 WCAG 44，视觉居中） | 同上 |

- **hover 纪律**：「不添加系统已编码之外的状态——primary 按下变深，其余无变化」（DESIGN.md Do/Don'ts）。
  即：**取消上浮位移动效**，反馈靠「变深 + scale(0.98)」。

### 1.4 输入控件

| 项 | 规格 | 来源 |
|---|---|---|
| text-input | 高 **40px**、圆角 8px、padding 10×14、正文 16px、1px hairline 边 | claude-design-card/DESIGN.md |
| focus 态 | 边框变 primary + **3px 强调色 15% 透明外环** | 同上（text-input-focused） |
| 产品端输入 | 高 36px、hover/focus 内置 | ui_components.md |
| composer「一个盒子」 | 输入区+附件钮+发送钮合并为一个统一圆角盒，**focus-within 整盒高亮**（焦点属于整个盒子而非单一控件） | [collie 项目 ADR 0057](https://github.com/altans/collie/blob/099a39a7fda9ab162323f69a882c6a423d0d406b/.adr/0057-the-composer-is-one-box.md) |

### 1.5 间距系统

- 基座 **4px**；令牌：4 / 8 / 12 / 16 / 24 / 32 / 48 / **96（section）**；内容最大宽 ≈ **1200px**。
- 卡片内边距：32px（大卡）/ 24px（代码窗、连接卡）/ 20px（小 tile）；区块间统一 96px（编辑感节奏）。
- 产品端令牌：2/4/5/8/12/16。来源：[Anthropic Design Tokens（Dembrandt 提取）](https://www.dembrandt.com/explorer/anthropic)、claude-design-card/DESIGN.md。

### 1.6 圆角令牌

| 令牌 | 值 | 用途 | 来源 |
|---|---|---|---|
| xs / sm | 4 / 6px | 徽章角、下拉项 | claude-design-card/DESIGN.md |
| **md** | **8px** | **按钮、输入框、分段标签** | 同上 |
| **lg** | **12px** | **内容卡、产品卡** | 同上 |
| xl | 16px | Hero 插图容器、大横幅 | 同上 |
| pill / full | 9999px | 徽章、图标钮 | 同上 |

### 1.7 阴影与层级

- **色块分层优先，阴影极少**：正文区/顶栏零阴影；卡片用 hairline 边框表达层级；
  极少数悬浮态用 `0 1px 3px rgba(20,20,19,.08)`；产品端「无渐变、无装饰阴影（仅功能焦点环）」。
  来源：claude-design-card/DESIGN.md（Elevation）、ui_components.md。

### 1.8 动效与交互细节

| 项 | 规格 | 来源 |
|---|---|---|
| 交互过渡 | 产品端常用 **150ms** 量级；焦点环立即出现（无动画） | ui_components.md（hover/focus 内置）、[open-claude-ui 逆向资料](https://raw.githubusercontent.com/Caho1/open-claude-ui/master/docs/v1/02-%e5%9f%ba%e7%a1%80%e5%8e%9f%e5%ad%90%e7%bb%84%e4%bb%b6%e4%b8%8e%e4%ba%a4%e4%ba%92%e6%8e%a7%e4%bb%b6.md) |
| press 反馈 | scale(0.98) + 变深；**无 hover 上浮** | 同上 |
| 出现动画 | 轻量淡入（营销站动效极克制；类型机/图表动画存在但不在提取范围） | claude-design-card/DESIGN.md「Known Gaps」 |
| 加载态 | 骨架屏 / 状态文案（营销站未提取到具体参数，产品端为转圈+文案） | 同上 |
| 卡片交互 | hover 边框加深（hairline → 可见边框），无阴影放大 | ui_components.md |

### 1.9 卡片与分段控件

- 卡片：surface-card 底 + hairline 边 + 12px 圆角 + 大内边距；深色产品卡用深底承载产品界面（代码窗等）。
- 分段/分类标签（category-tab）：未激活 = 透明底 + muted 字；激活 = **surface-card 底 + ink 字**；padding 8×14、圆角 8px。来源：claude-design-card/DESIGN.md。

### 1.10 来源清单

| # | 来源 | 日期 | 提取内容 |
|---|---|---|---|
| 1 | [geekjourneyx/claude-design-card DESIGN.md](https://github.com/geekjourneyx/claude-design-card/blob/main/DESIGN.md) | 2026-04-24 | 主要来源：全套色彩/字体/按钮/输入/间距/圆角/阴影令牌 |
| 2 | [dwsy/agent 的 claude-guidelines ui_components.md](https://github.com/dwsy/agent/blob/291e371f7dc7a7957f0141d2a5558285231eaa9a/extensions/generative-ui/claude-guidelines/sections/ui_components.md) | 2026-10-31 | claude.ai 产品端：0.5px 边框、36px 输入、按钮 outline+hover+active scale(0.98)、无装饰阴影 |
| 3 | [Caho1/open-claude-ui 基础原子组件逆向资料](https://raw.githubusercontent.com/Caho1/open-claude-ui/master/docs/v1/02-%e5%9f%ba%e7%a1%80%e5%8e%9f%e5%ad%90%e7%bb%84%e4%bb%b6%e4%b8%8e%e4%ba%a4%e4%ba%92%e6%8e%a7%e4%bb%b6.md) | 2026 | 多阶按钮高度标尺、圆角随尺寸缩放（方向性参照） |
| 4 | [altans/collie ADR 0057「The composer is one box」](https://github.com/altans/collie/blob/099a39a7fda9ab162323f69a882c6a423d0d406b/.adr/0057-the-composer-is-one-box.md) | 2026-09-22 | 输入盒统一焦点（focus-within 整盒高亮） |
| 5 | [Anthropic Design Tokens（Dembrandt）](https://www.dembrandt.com/explorer/anthropic) | 2024-12-31 | 产品端间距刻度 2/4/5/8/12/16 |

---

## 2. 融合方案（Claude 骨架 × 暖色两主题）

### 2.1 字体替代方案（OFL，全部可 vendoring）

| 用途 | 字体（按优先级） | 许可证 | 与 ui-design-direction 的关系 |
|---|---|---|---|
| 西文/拉丁标题 | **Cormorant Garamond**（500 字重 + -0.02em 字距）→ 备选 Lora → 系统回退 Georgia / Times New Roman | OFL 1.1 | **替换 Fraunces**（见 §3-1） |
| 中文标题 | 霞鹜文楷 LXGW WenKai | OFL | 保留 |
| 西文正文/UI | **Inter** → 系统回退 Segoe UI / PingFang SC / Microsoft YaHei | OFL 1.1 | **替换 Nunito**（见 §3-2） |
| 中文正文 | Noto Sans SC | OFL | 保留 |
| 数字/哈希/日志 | JetBrains Mono | OFL 1.1 | 保留（与 Claude 一致） |

- 标题字重 **400（西文）/500–600（中文）**；大标题负字距 -0.01 ~ -0.02em；行高：display 1.1–1.3、正文 1.7（中文）。
- 字阶（Claude 阶梯 + 中文折算）：12 / 13 / 14 / 16 / 18 / 22 / 28 / 36 / 48。

### 2.2 按钮规范（融合后）

| 档位 | 几何 | 默认 | hover | press/active | disabled |
|---|---|---|---|---|---|
| primary | 高 40px · 圆角 8px · padding 0 20px · 14px/500 | 实底 `--accent` + `--on-accent` 深色字 | 变深 `--accent-strong` | 更深 `--accent-deep` + scale(.98) | 去饱和 + 降透明度 |
| secondary | 同几何 | `--surface-solid` 底 + 1px `--hairline` 边 + `--ink` 字 | 底 → `--surface-card` | 更深 + scale(.98) | 同上 |
| text-link | 高 32px · 无底无边 | `--accent-strong` 文字 | 下划线 | 保持 | 降透明度 |
| icon | 36px 圆形 | `--surface-solid` + hairline 边 | 底 → `--surface-card` | scale(.95) | 同上 |
| danger（本项目扩展） | 同 secondary | 透明底 + 1px `--danger` 边 + `--danger` 字 | 底 → `--danger-soft`（≈12% 透明危险色） | scale(.98) | 同上 |

- 对比度：保留我们「橙底深棕字」（--on-accent ≈ 6:1），**优于** Claude 的珊瑚底白字（≈3.2:1，未达 AA）——这是刻意的无障碍改进，记录在案。
- 触控：`@media (pointer: coarse)` 下按钮 min-height 升至 44px。

### 2.3 输入控件规范

- 输入框：高 40px、圆角 8px、padding 0 14px、正文 16px、1px hairline 边、`--surface-solid` 底。
- hover：边框 → `--ink-3`；focus：边框 → `--accent` + **box-shadow 0 0 0 3px `--focus-ring`（accent 15% 透明）**，无 outline 动画延迟。
- disabled：降透明度 + `--bg-deep` 底。
- composer「一个盒子」：`focus-within` 整盒高亮 + 36px 圆形发送钮（accent 实底）。

### 2.4 间距 / 圆角 / 阴影令牌（融合后）

- 间距（4px 基座）：`--sp-xxs 4` · `--sp-xs 8` · `--sp-sm 12` · `--sp-md 16` · `--sp-lg 24` · `--sp-xl 32` · `--sp-xxl 48` · `--sp-section 96`；内容最大宽 1180px（≈Claude 1200）。
- 圆角：`--r-xs 4` · `--r-sm 6` · **`--r-md 8`（按钮/输入/分段标签）** · **`--r-lg 12`（卡片）** · `--r-xl 16`（Hero 容器）· pill 9999（徽章/图标钮）。
- 阴影（大幅弱化）：扁平优先——hairline 边框承载层级；小卡 `0 1px 3px` 低透明阴影；**毛玻璃大面板保留 `0 4px 20px` 弱悬浮阴影**（玻璃质感需要极浅环境影）；删除 0 8px 32px 大阴影。

### 2.5 交互细节规范

| 项 | 值 |
|---|---|
| 过渡时长 | hover/press/focus 背景与边框 **150ms**；出现动画 **200ms**（fade + 上移 4px） |
| 缓动 | `cubic-bezier(.4, 0, .2, 1)`（标准 ease-out） |
| 焦点环 | 全局 `:focus-visible`：无 outline，**box-shadow 0 0 0 3px var(--focus-ring)**；有边框控件同时把边框变 accent |
| press | scale(.98)（按钮）/ scale(.95)（图标钮）；**取消 hover 上浮 translateY** |
| 卡片交互 | hover 边框加深（hairline → ink-3），无阴影放大 |
| 加载态 | 骨架屏暖色微光脉冲 1.8s（保留 ui-design-direction 参数）+ 16px 转圈 spinner（.8s）；reduced-motion 全部静止 |
| 列表进场 | stagger 30ms / 项，200ms 单项，上限 12 项 |
| 氛围层（保留） | 光斑漂移 26–44s 错速、粒子漂浮 10–16s、噪点静态 |

### 2.6 保留项（与 ui-design-direction 不冲突，原样保留）

两主题色彩令牌（暖阳奶油/森林夜语）、光斑/粒子/噪点三层氛围、氛围三档（标准/轻量/关闭）、
prefers-reduced-motion 全局降级、R0–R3 徽章「文字+图标双通道」、双语 Hero、等宽数字右对齐（Stripe 表格原则）、
人文文案语气、毛玻璃面板（backdrop-filter + @supports 回退）。

---

## 3. 与 ui-design-direction.md 的冲突处修订建议（供创始人决策）

| # | 原方案（ui-design-direction） | 建议修订（向 Claude 看齐） | 理由（来源） |
|---|---|---|---|
| 1 | 西文标题 Fraunces | 改 **Cormorant Garamond**（主）/ Lora（备） | Copernicus/Tiempos 的 OFL 最近似为 Cormorant（§1.1 来源 1）；Fraunces 高对比「软衬线」偏艺术，偏离 Claude 编辑感 |
| 2 | 西文正文 Nunito | 改 **Inter** | Claude 官方近似替代即 Inter；Nunito 偏圆润童趣，弱化「编辑感」 |
| 3 | 按钮圆角 14px | 改 **8px**（--r-md） | Claude 按钮统一 8px（§1.6） |
| 4 | 面板圆角 16px 通用 | 卡片 **12px**、Hero 容器 16px 分级 | Claude 圆角层级（§1.6） |
| 5 | 毛玻璃按钮（半透明 accent + 白边 + hover 上浮） | 改**扁平实底按钮**；玻璃质感回收给面板/大容器 | Claude 按钮扁平、无上浮（§1.3）；我们签名玻璃仍保留在面板层 |
| 6 | hover `translateY(-1px)` + brightness | 改「变深 + scale(.98)」，取消位移 | Claude hover 纪律（§1.3） |
| 7 | 阴影 `0 8px 32px` | 改 hairline 边框 + `0 1px 3px` 微阴影（玻璃面板 `0 4px 20px`） | Claude 阴影极克制（§1.7） |
| 8 | 焦点环 `outline: 2px solid accent` | 改 **3px accent 15% 透明外环 + 边框变 accent** | Claude text-input-focused（§1.4） |
| 9 | 动效 200–400ms「快入缓出」曲线 | 交互过渡 **150ms**、出现动画 200ms ease-out；氛围长周期不变 | Claude 产品端节奏（§1.8） |
| 10 | 字阶 12/13/14/16/20/28/40、标题字重 600 | 改 Claude 阶梯 12/13/14/16/18/22/28/36/48；**标题字重 400 + 负字距** | §1.1 |
| 11 | 分段控件 pill 容器 | 改 Claude category-tab：透明底 muted 字，激活 `--surface-card` 底 + ink 字，8px 圆角 | §1.9 |
| 12 | 输入控件/加载态未覆盖 | 补 §2.3 / §2.5 规格 | 新增覆盖 |
| 13 | 按钮「三档 + 危险」 | 扩展为 primary/secondary/text-link/icon/danger 五档 | Claude 层级（§1.3）+ 我们 R3 危险语义 |

> 说明：原文件（docs/ui-design-direction.md）由 researcher 维护，属他人写作用域，本笔记只提出建议，
> 不直接修改；是否采纳由创始人裁决后同步。

---

## 4. 资源引入登记（许可证，待创始人审查下载）

| 资源 | 许可证 | 用途 | 状态 |
|---|---|---|---|
| Cormorant Garamond | SIL OFL 1.1 | 西文标题（Claude 衬线近似） | 待审查 vendoring |
| Lora | SIL OFL 1.1 | 西文标题备选 | 待审查 vendoring |
| Inter | SIL OFL 1.1 | 西文正文/UI | 待审查 vendoring |
| 霞鹜文楷 LXGW WenKai | SIL OFL 1.1 | 中文标题 | 待审查 vendoring（沿用原方案） |
| Noto Sans SC | SIL OFL 1.1 | 中文正文 | 待审查 vendoring（沿用原方案，可子集化） |
| JetBrains Mono | SIL OFL 1.1 | 等宽（哈希/日志） | 待审查 vendoring（沿用原方案） |

- 参照字体 Copernicus / Tiempos / Styrene 为商业授权，**不引入**，仅作设计参照。
- 下载方式走 tools/fetch_wheels.py 同款「直接下载」路径或人工下载后放入
  `src/continuity/webui/static/fonts/`（W3a 授权后落地），逐项经创始人审查（AGENTS.md 依赖流程）。

## 5. 落地衔接（W3a 授权后）

- `src/continuity/webui/static/` 重构时直接复用本笔记 §2 令牌与规格；
  预览页 preview/style-preview.html v2 即本笔记的可运行实现（系统字体回退栈，零外部资源）。
- 多语言（中英）：`src/continuity/webui/locales/` 目录与 W3 并行规划，本笔记不展开。

## 6. 待创始人确认清单

1. 西文标题是否采纳 Cormorant Garamond（主）+ Lora（备），替换 Fraunces；
2. 西文正文是否采纳 Inter，替换 Nunito；
3. 按钮扁平化（取消毛玻璃按钮）与 hover 取消上浮是否接受；
4. 卡片圆角 16→12px、按钮 14→8px 是否接受；
5. 保留「橙底深棕字」（对比度优于 Claude 白字）是否认可。

---

## 7. 产品页改版后的艺术家审阅（2026-11-07，仅建议，未改代码）

> 背景：产品页改版已按 docs/frontend-redesign-brief.md 交付上库，创始人认可「先这样」，投放已暂停。
> 本节约定：frontend-developer 以【艺术家】思考（AGENTS.md 第 12 条），对视觉、体验与细节精益求精；
> 以下为对已上库产品页（src/continuity/webui/static/）的自发审阅清单，**全部只记录、不落地**，
> 等创始人新一轮前端指令再动工。
> 适用性提醒：本笔记 §1–§6 为预览页（preview/style-preview.html）的 Claude 骨架方向记录；
> **产品页**以 frontend-redesign-brief.md 与 frontend-redesign-delivery.md 为准（宋体标题/黑体正文、
> 禁楷体、语义令牌、无粒子装饰）。两套笔记并行，勿混用。

### 7.1 P1 细节修正（低成本、收益明确，建议下一轮优先）

1. **hover 与 focus 的色彩语法分离**：现 `.input:hover { border-color: var(--focus) }` 把「悬停」与
   「键盘聚焦」共用同一色，交互语法混淆（悬停不该喊出焦点环的颜色）。建议新增中性加深边框令牌
   `--border-strong`（浅色 ≈ `#8A7554`、深色 ≈ `#84A693`，均按 ≥3:1 实测），hover 用它，
   `--focus` 只留给 `:focus-visible`。
2. **标题行高**：h1–h4 未设 line-height，继承正文 1.7，22px/18px 标题显得松散（衬线标题的尊严
   在紧凑行距）。建议 h2/h3/h4 显式 `line-height: 1.4`（hero-title 已 1.35，不动）。
3. **长路径防溢出**：`.scan-summary` 是 h3，未加 `overflow-wrap: anywhere`（只有 `.list li` 有）；
   深目录路径在 320px 屏会把摘要撑破。这是稳健性细节，非纯美学。
4. **加载文案去行话**：「正在检查…（请稍候，检查为串行任务）」中「串行任务」是内部术语；
   建议改为「正在检查…（大目录可能需要一会儿）」，语气更「人话」且不撒谎。
5. **reduced-motion 与平滑滚动**：Hero「了解修复等级」用 `scrollIntoView({behavior:"smooth"})`，
   未查询 `matchMedia("(prefers-reduced-motion: reduce)")`；减少动态偏好下应退回 `behavior:"auto"`。
6. **结果出现的呼吸感**：扫描完成后 `#scan-result` 从 `display:none` 硬切出现，像被砸出来；
   建议 200ms 淡入（`@keyframes fade-in`，属「状态反馈动效」合规），并在 reduced-motion 规则里
   显式关闭（延续当前「不用 !important」的显式清单写法）。
7. **成功态的仪式感**：`.scan-summary::before` 加一个 `--success` 色的「✓ 」标记——
   文字+符号双通道，与 R0 徽章同一语言；伪元素不干扰 textContent 写入。
8. **选区颜色**：加 `::selection { background: var(--primary); color: var(--primary-text) }`
   （两主题下均 5:1 以上），复制路径时有一抹品牌暖色——零成本的温度细节。
9. **主题切换的过渡范围**：现只有 `body` 过渡背景/文字色，顶栏、面板、按钮在切主题时是
   「瞬间换装」的割裂感；建议把 `background-color/border-color/color 150ms` 过渡覆盖到
   `.topbar/.nav/.hero-work/.input/.btn/.level-list` 等表面元素（并同步进 reduced-motion 显式清单）。

### 7.2 P2 结构节奏（需创始人点头的视觉改动）

10. **间距尺度令牌化**：`--levels` 上距 56px、`.info-block` 上距 48px、主容器底 48px、页脚上距 48px
    是随手值，不成节奏。建议建立 `--sp-*` 尺度（8/16/24/32/48/64）并统一到 48/64 两档，
    页面垂直呼吸立刻变「有作曲感」。
11. **目录操作面板的呼吸**：`.hero-work` 内边距 20px 偏挤，标题+说明+表单密度高；
    建议 24px，desc 下距 14→16px，h2 与徽章间留 8px——右侧操作区是首页的主角，值得更贵的留白。
12. **R0–R3 分隔线消重**：2×2 网格里外框 + 内分隔线在交叉点形成双线加粗；
    建议新增 `--border-soft`（浅色 ≈ `#C4B49A`、深色 ≈ `#55705F` 级别，仅作细分隔）用于格内线，
    外框保持 `--border`——层级立刻干净。
13. **主题切换按钮图形化**：纯文字「深色主题/浅色主题」在顶栏识别度低；建议加一个
    `aria-hidden` 的内联日/月小图标（文字保留，图标+文字双通道），与全局焦点环天然兼容。
14. **空状态文案**：发现数为 0 时列表区是空的，只有「0 项」；建议 `renderScan` 在 findings 为 0
    时显示「没有发现明显问题，一切安好。」——空状态是产品语气的最佳舞台（需改 app.js，等指令）。

### 7.3 P3 战略（等新一轮指令再排期）

15. **字体 vendoring 优先级上调**：Windows 下宋体标题回退 SimSun，600 字重会被浏览器伪加粗，
    观感发「糊」；建议优先审批 **Noto Serif SC 标题子集** vendoring（体积小、收益最大），
    正文 Noto Sans SC 可缓（PingFang/雅黑已够用）。
16. **品牌小标记**：顶栏目前只有 20px 字标；可考虑一个内联 SVG 的「暖光/小巢」极简标记
    （aria-hidden，零外部资源），让「守护者」的人格有形状——但必须克制，避免图标噪音。
17. **预览页令牌同步**：预览页仍用 sun/forest 旧命名与旧令牌；下一轮建议把预览页令牌
    与产品页语义令牌（light/dark + 15 个语义角色）对齐，让预览页继续担任可信的设计参照。
18. **i18n 铺垫**：页脚英文行与顶栏 pledge 已双语；W3 多语言时把文案抽到
    `src/continuity/webui/locales/` 词典（中英先行），本轮不动。

### 7.4 自我约束（艺术家也要守规矩）

- 以上全部为「自发灵感」记录，**未改动任何代码与测试**；产品页保持创始人认可的交付状态。
- 每一条落地前须对照 frontend-redesign-brief.md 的禁令（无粒子/光斑/装饰动画、无斜体/负字距、
  对比度实测、reduced-motion、零外部资源），并过 qa-reviewer 三轮审核。
- 动效类建议（6/8/9）全部属于「状态反馈」范畴；任何循环氛围动画仍不进入产品页（那是预览页的领地）。
