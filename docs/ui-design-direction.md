# UI 设计方向（ui-design-direction）

> 编制：researcher（Agent Teams）｜ 日期：2026-11-07
> 目的：按创始人指令 3（UI 现代化重设计 + 中英双语并入 W3），建立明确美学基调与设计系统，
> 供创始人从两个风格方向中二选一。只出方案、不写代码。
> 约束：本地 Web UI 为零依赖原生 JS + 纯 CSS（方案 A），所有实现资源须可 vendoring、无 npm/CDN。

---

## 1. 调研摘要：国外主流科技网站的风格特征

| 对象 | 关键特征 | 对我们的启示 |
|---|---|---|
| [Linear](https://linear.app/) | 近黑底色、单一强调色、1px 细边框、无冗余装饰、一次只展示一层信息、键盘优先 | 深色工具型产品的信息密度与克制基准 |
| [Vercel](https://vercel.com/) | 黑白单色 + 可见胶片颗粒、编辑级排版、大留白 | 官网/落地页的「编辑感」范式 |
| [Stripe](https://stripe.com/) | 表格即主界面、数字右对齐与等宽数字、虹彩渐变仅作点缀 | 报告/清单页的表格语言 |
| [Raycast](https://www.raycast.com/) | 深紫暗色 + 命令面板（⌘K）交互 | 「命令面板」与我们 CLI 出身天然契合 |
| [Arc](https://arc.net/) | 多彩流动、轻盈动效 | 动效尺度参考（少而准） |
| [Notion](https://www.notion.so/) | 极简留白、emoji 点缀、层次靠字体而非装饰 | 空状态与文档型页面的参照 |

分类学依据：[2024–2026 SaaS 风格分类学（8 种风格+参数）](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md)（2026-04）、[2026 SaaS 仪表盘设计趋势](https://adminlte.io/blog/saas-dashboard-design-examples/)（2026-07）。

---

## 2. 公共基础（两个方案共用，无论选哪个）

### 2.1 组件语言（全站统一）
- **容器**：1px 边框 + 圆角（8–12px）；面板用「边框分层」而非重阴影；深色模式禁用大面积投影。
- **状态色**（与修复等级语义绑定）：R0 确定性=绿、R1 需确认=琥珀、R2 仅建议=灰蓝、R3 隔离=红；「安全/成功」「警告」「危险」三元色贯穿扫描结果、diff、toast。
- **数字与表格**：报告页数字一律等宽字体 + 右对齐（Stripe 原则）；哈希值截断显示 + 悬停全量。
- **危险操作**：删除/覆盖弹窗必须显示**文件元数据（文件名、创建时间、消息数）+ 双重确认**——直接吸收失败案例库 CASE-10（#5797）的用户诉求。
- **空状态**：用短句说明「缺什么、从哪恢复」，呼应案例库 CASE-14（无界面抢救数据场景）。
- **图标**：Lucide 线性风格，1.5px 描边，24px 网格（SVG 内联，零依赖）。

### 2.2 动效与交互模式
- 原则：**少而准**。微交互 120–200ms `ease-out`；进度类（扫描/备份）用真实进度条 + 阶段文案，不用装饰性动画。
- 交互模式：**命令面板（⌘K / Ctrl+K）**——直接映射 CLI 子命令（scan/backup/restore/migrate/report），键盘优先是 Linear/Raycast 式专业感的低成本实现；列表 hover 1px 边框提亮；diff 双栏高亮。
- 无障碍：全部动效受 `prefers-reduced-motion` 约束；焦点环可见；正文对比度 ≥ WCAG AA（4.5:1）。

### 2.3 字体与排版（vendoring，无 CDN）
| 用途 | 字体 | 许可证 |
|---|---|---|
| UI 正文西文 | [Inter](https://rsms.me/inter/)（或 [Geist](https://github.com/vercel/geist-font) 作展示字） | OFL |
| 中文正文 | [Noto Sans SC](https://fonts.google.com/noto) | OFL |
| 数字/哈希/日志/代码 | [JetBrains Mono](https://www.jetbrains.com/lp/mono/) | OFL |
- 字阶：12/13/14/16/20/28/40；行高 1.5–1.6；标题字重 600–700；正文 400–450（中文）。
- 数字场景（备份大小、哈希、时间戳）强制 `font-variant-numeric: tabular-nums`。

### 2.4 多语言（中英优先，W3 并入）
- 实现：**零依赖 JSON 词典**（`zh-CN.json`/`en-US.json` + 简单 `t(key)`），语言切换存入本地偏好并联动 `lang` 属性；不用 i18next 框架（符合方案 A）。
- 规范：所有界面文案键名语义化；日期统一 ISO 8601 + 本地化显示；中文为主、英文全量覆盖（创始人双语要求）；避免字符串拼接复数和占位符硬编码；**诊断/修复报告术语中英对照表**随词典维护（R0/R1/R2/R3、manifest、integrity 等）。

---

## 3. 方案一：暗色科技风（Dark Product-First，推荐）

### 视觉关键词
克制、专业、深夜工具感、单点强调色、细边框、信息密度高。

### 色彩系统
- 背景层：`#0A0A0F`（画布）/ `#101014`（面板）/ `#16161C`（悬浮）
- 边框：`rgba(255,255,255,.08)` 常规 / `.14` hover
- 文本：`#EDEDEF` 主 / `#9B9BA3` 次 / `#6E6E77` 弱
- 强调色：主 `#6E79D6`（靛蓝，Linear 系）+ 功能色青 `#5EE1FF`；成功 `#4ADE80`、警告 `#FBBF24`、危险 `#F87171`
- 暗色渐变仅用于首屏品牌区（极低频），产品内零渐变
- **亮色模式配套**（同令牌双主题）：画布 `#FAFAFB`、面板 `#FFFFFF`、文本 `#1A1A1F`、强调色不变——两主题共用同一套 CSS 变量

### 参考对象
[Linear](https://linear.app/)（主）、[Raycast](https://www.raycast.com/)（命令面板）、ST 自身 UI（用户熟悉度）。

### 取舍
- 优点：与目标用户使用场景（深夜、酒馆内暗色 UI）无缝；「开发者工具」信任感；插件内嵌预览（酒馆也是暗色）无割裂；深色下细边框信息分层效果最佳。
- 代价：亮色模式需额外维护一套令牌；纯暗色在白天/浅色习惯用户中接受度略低（以 `prefers-color-scheme` 自动切换缓解）。

---

## 4. 方案二：明亮极简风（Monochrome Editorial / Light Minimal）

### 视觉关键词
明亮、留白、编辑感、黑白为主、胶片颗粒点缀（仅品牌页）。

### 色彩系统
- 背景层：`#F8F8F6`（纸感暖白）/ `#FFFFFF`（面板）；暗色模式配套 `#0A0A0F`
- 边框：`#E5E5E1`；文本：`#1A1A1A` 主 / `#6B6B70` 次
- 强调色：**黑**为主强调（Vercel 式）+ 单一彩点（如靛蓝 `#5E6AD2`）仅用于状态与链接
- 阴影：浅层软阴影（`0 1px 2px rgba(0,0,0,.04)`）替代重边框
- 品牌页允许可见胶片颗粒（Vercel monochrome-grain 风格），产品页保持纯净

### 参考对象
[Vercel](https://vercel.com/)（主）、[Stripe](https://stripe.com/)（表格与明快）、[Notion](https://www.notion.so/)（留白）。

### 取舍
- 优点：白天观感友好、截图/视频传播清晰；「纯净=可信」的隐私产品气质；实现成本略低（浅色默认）。
- 代价：与酒馆/深夜使用场景反差大，插件内嵌时像「跳到一个白色世界」；深色模式是补充而非原生；长列表扫视疲劳高于深色细边框方案（Linear 式信息分层更难在浅色复现）。

---

## 5. 推荐结论（供创始人选择）

**推荐组合策略（双轨）**：
1. **产品界面（Web UI + 插件面板）＝方案一暗色科技风**为默认主题，自动适配系统亮色（两套令牌并存）——理由：目标用户深夜重度使用、与 ST 生态视觉连续、插件内嵌协调、Linear 式「工具感」最利于建立专业信任。
2. **官网/落地页＝方案二明亮极简风的编辑感**（黑白 + 颗粒 + 大字号标语）——与产品内暗色形成「外亮内暗」的品牌节奏，落地页在社交传播中更醒目。
3. 若创始人只选其一：选**方案一**（产品为根本）；若创始人偏好明快气质：选**方案二**并把命令面板与表格语言保留（两者公共基础相同，切换成本低——公共设计令牌已按双主题设计）。

### 落地资源（来自 resource-map.md，均需按流程 vendoring）
- 色彩令牌：Radix Colors / Open Color 数值 → 项目 CSS 变量
- 字体：Inter + JetBrains Mono + Noto Sans SC（OFL，本地文件）
- 图标：Lucide SVG 内联
- 起步样式：Pico.css 单文件可作过渡期基线（最终以自建设计系统为准）
- 风格参数：2024–2026 风格分类学（暗色产品风 / 黑白颗粒风两节）

---

## 6. 来源

- [2024–2026 SaaS 风格分类学](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md)（2026-04-18）
- [10 Best SaaS Dashboard Design Examples & Trends (2026)](https://adminlte.io/blog/saas-dashboard-design-examples/)（2026-07-26）
- 风格基准官网：[Linear](https://linear.app/)、[Vercel](https://vercel.com/)、[Stripe](https://stripe.com/)、[Raycast](https://www.raycast.com/)、[Arc](https://arc.net/)、[Notion](https://www.notion.so/)
- 资源：[Radix Colors](https://www.radix-ui.com/colors)、[Open Color](https://yeun.github.io/open-color/)、[Inter](https://rsms.me/inter/)、[Geist](https://github.com/vercel/geist-font)、[JetBrains Mono](https://www.jetbrains.com/lp/mono/)、[Noto](https://fonts.google.com/noto)、[Lucide](https://lucide.dev/)、[Pico.css](https://picocss.com/)
- 项目内依据：[resource-map.md](./resource-map.md)、[failure-case-library.md](./failure-case-library.md)（CASE-10 弹窗设计）、AGENTS.md（方案 A 与 W3 要求）
