# UI 设计方向（ui-design-direction）

> 编制：researcher（Agent Teams）｜ 修订：2026-11-07（对齐 frontend-redesign-brief.md）
> **权威规范声明**：创始人 2026-11-07 的 [frontend-redesign-brief.md](./frontend-redesign-brief.md)（AGENTS.md 规则 10）
> 为前端执行权威规范，**冲突时以 brief 为准**；本文档仅作美学基调与令牌参考，与 brief 不一致处一律服从 brief。
> 本版按 brief 完成对齐：中文标题宋体系（禁楷体/霞鹜文楷/手写）、**不新增粒子/光斑/装饰性动画**、
> 阴影与玻璃从简、语义令牌集中维护、窄屏 1024/768/390/320。
> 定位：娱乐/陪伴类产品的人文关怀美学——温暖、柔和、有生机；不采用硬核科技风。

---

## 1. 美学基调（一句话）

**「温暖、可信、有生机」**：暖奶油/陶土的浅色与森林绿的深色，界面像一个能让人安心停靠的
「数据小窝」——人文关怀通过色彩、字体与克制的动效传达，**氛围不靠粒子与光斑堆砌**。

### 1.1 定位声明
- 产品本质：陪伴用户多年的角色与故事的**守护者**；界面传达「被照顾」「安心」「鲜活」，而非「机器控制台」。
- 设计原则：**温润 > 锐利**（圆角、柔和表面）；**清晰 > 炫技**（信息层级、可读性优先，brief 一/三）；
  **克制 > 装饰**（动效只反馈状态变化，不做循环氛围动画，brief 八）。

### 1.2 参考对象（只取色彩语言与人文气质，不模仿任何实现）

| 参考 | 借鉴点（限色彩/气质） |
|---|---|
| Journey（风之旅人） | 暖沙色、黄昏暖光——**只取色彩语言，不实现粒子** |
| 动物森友会 | 奶油底色、柔和圆角、低压力氛围 |
| Claude（Anthropic）Warm Editorial | 陶土橙 Clay #d97757、奶油纸感、衬线标题+黑体正文的编辑感（详见 [claude-design-study.md](./claude-design-study.md)） |
| 吉卜力式柔和场景感 | 暖绿、奶油、天空渐变（仅色彩参考） |

> 移除项：原「科技风」（Linear/Raycast 深黑细边框）已废弃；本版再次移除粒子/光斑/液态玻璃氛围层
> 的实现建议（brief 七：不新增粒子、光斑或装饰性动画；阴影与玻璃效果从简）。

---

## 2. 两主题 × 同一基调

| 维度 | 主题 A「暖阳奶油」（浅色，默认） | 主题 B「森林夜语」（深色） |
|---|---|---|
| 场景感 | 下午暖光书房：奶油墙、陶土点缀 | 森林夜晚营地：深绿树影、柔和绿色点缀 |
| 背景 | 暖奶油（语义令牌 --bg-canvas） | 深森林绿（非冷黑） |
| 表面 | 浅表面区分（从简，不过度用玻璃/阴影） | 同左，深色对应 |
| 强调色 | 陶土色（主操作） | 新叶绿（主操作） |
| 共同基调 | 同一圆角/间距/字体/动效节奏/语义角色；状态含义不随主题改变（brief 七） | 同左 |

两主题共享全部结构、语义令牌与组件；切换只换令牌值，零结构性改动。

---

## 3. 色彩令牌（语义角色与 brief 七对齐，两套完整）

### 3.1 语义角色清单（两主题共用，brief 七最低要求）
背景、主要表面、正文、次要文字、边框、主操作、主操作文字、焦点环、成功/警告/建议/危险状态。

### 3.2 主题 A「暖阳奶油」（浅色，默认）

| 令牌 | 值 | 用途/对比度说明 |
|---|---|---|
| `--bg-canvas` | `#FAF3E8` | 页面背景（暖奶油） |
| `--surface` | `#FFF9F0` | 主要表面（卡片/输入区；识别表面差异即可，brief 七从简） |
| `--ink` | `#4A3B2C` | 正文（暖棕墨，≈10:1） |
| `--ink-2` | `#8A7A64` | 次要文字（≈4.6:1，AA；brief 七要求提高占位符/说明可读性——辅助文字一律用本级起） |
| `--border` | `rgba(122,96,64,.16)` | 边框（细分隔） |
| `--accent` | `#D97757` | 主操作（陶土，与 brief 一「陶土色」一致；与 Claude Clay 同值） |
| `--accent-strong` | `#B05F3F` | 链接/强调文字（≈4.9:1） |
| `--on-accent` | `#FFF6EE` / 深棕 `#3D2B1A` 二选一实测 | 主操作文字（以对比度实测为准，禁白字低对比底） |
| `--focus` | `#C2652E`（2px outline） | 焦点环（键盘可见，brief 八） |
| `--success` | `#6E9A5B` | R0 成功（苔绿） |
| `--warn` | `#C98A2B` | R1 待确认（蜂蜜黄） |
| `--suggest` | `#8A7A64` | R2 仅建议（中性暖灰） |
| `--danger` | `#C96A54` | R3 隔离（陶土红，柔和） |

### 3.3 主题 B「森林夜语」（深色）

| 令牌 | 值 | 用途/对比度说明 |
|---|---|---|
| `--bg-canvas` | `#16251F` | 页面背景（深森林绿，非冷黑） |
| `--surface` | `#1E3128` | 主要表面 |
| `--ink` | `#EAF2EA` | 正文（浅鼠尾草，≈12:1） |
| `--ink-2` | `#A8C0B2` | 次要文字（≈7:1） |
| `--border` | `rgba(190,220,200,.16)` | 边框 |
| `--accent` | `#7FBF9A` | 主操作（新叶绿，≈7.5:1） |
| `--accent-strong` | `#9AD8B4` | 链接/强调（≈9:1） |
| `--on-accent` | `#12241B` | 主操作文字（≈8:1） |
| `--focus` | `#9AD8B4` | 焦点环 |
| `--success` | `#8CC9A8` | R0 |
| `--warn` | `#E3C06B` | R1（柔和琥珀） |
| `--suggest` | `#A8C0B2` | R2 |
| `--danger` | `#E08E7E` | R3（柔和珊瑚） |

### 3.4 语义规范
- 状态识别**文字+图标双通道**，颜色仅辅助（brief 六；色弱友好）。
- 阴影/玻璃**从简**：保留「识别输入区域的表面差异」即可；不堆浓重边框/阴影/大面积底色（brief 七）。
- **不新增**粒子、光斑、装饰性动画、循环背景动画（brief 七/八）。
- 对比度不凭目测：交付说明须列出检查方式（brief 七）。

---

## 4. 字体与排版（对齐 brief 四）

| 用途 | 主选 | 回退 | 说明 |
|---|---|---|---|
| 中文大标题/章节标题 | **宋体系：Noto Serif SC（思源宋体）** | `"Songti SC","STSong","SimSun",serif` | **禁楷体、霞鹜文楷、手写风格**；不照搬西文负字距（brief 四） |
| 中文正文/导航/按钮/标签 | **黑体系：Noto Sans SC** | `"PingFang SC","Microsoft YaHei",sans-serif` | 正文行距适合连续阅读 |
| 西文标题（品牌副标题等） | Cormorant Garamond（OFL，创始人已认可方向） | serif 栈 | 仅西文展示，不用 CSS 合成/斜体伪手写 |
| 西文 UI 正文 | Inter | system-ui | 与 Claude 正文近似（见 claude-design-study） |
| 代码/数字/哈希 | JetBrains Mono | monospace 栈 | 仅技术区 |

- 未 vendoring 的字体一律走系统回退；**本轮不下载/新增未批准字体**，新字体只记录建议与许可证需求
  （brief 四：Noto Serif SC 等 vendoring 需经许可证流程批准后实施）。
- 避免中英重复表达；英文只作简短辅助标识或品牌副标题（brief 四）。

---

## 5. 动效与装饰（对齐 brief 八，全部从简）

- 动效**简短且只反馈状态变化**：默认/悬停/按下/键盘聚焦/禁用/加载/成功/错误（只实现真实支持的状态）。
- **不做**：循环背景动画、悬停上浮、粒子、光斑漂移、无功能装饰动效。
- 尊重 `prefers-reduced-motion`；危险操作弹窗保留「文件元数据 + 双重确认」（failure-case-library CASE-10 诉求）。
- 若未来需要氛围层，必须由创始人书面授权追加（当前 brief 明确禁止，本文档不再预写实现）。

---

## 6. 组件语言（从简、语义化）

- 控件：圆角 8–12px；边框细分隔；主操作=陶土/新叶绿实色，其余次级操作用浅表面区分。
- R0–R3 区：统一对齐 + 间距 + 细分隔 + 浅表面，**不堆厚重卡片**；文字+图标双通道（brief 六）。
- 危险弹窗：文件名/创建时间/消息数 + 双重确认；语气柔和但步骤不省。
- 图标：Lucide 线性 SVG 内联；图标按钮必须有可访问名称（brief 八）。

---

## 7. 无障碍与窄屏

- 对比度：见 §3 令牌表（正文 AA；辅助文字用 --ink-2 起）。
- 色弱：状态全部文字+图标双通道。
- 焦点：可见焦点环（--focus），键盘可完成全流程（brief 八）。
- 窄屏：1024/768/390/320 四档检查；不舒适即切单列；按钮可换行、主次明确；相邻图标按钮不挤压（brief 三）。
- 触控目标易点（44×44 建议值）。

---

## 8. 落地资源清单（零构建、全部已批准或待批准）

- 字体（OFL，vendoring 需经许可证流程批准后实施）：Noto Serif SC、Noto Sans SC、Cormorant Garamond、Inter、JetBrains Mono。
- 图标：Lucide（ISC）SVG 内联。
- 令牌：CSS 自定义属性集中维护（brief 九），新增令牌在交付说明列出。
- 风格参照：[claude-design-study.md](./claude-design-study.md)（按键/排版/动效参数）、[frontend-redesign-brief.md](./frontend-redesign-brief.md)（权威规范）。

---

## 9. 给创始人的一句话确认摘要

**「暖阳奶油（陶土橙）与森林夜语（柔和绿）两主题共用同一套『温暖、可信、有生机』的人文基调——
宋体系标题 + 黑体系正文，无粒子/光斑/装饰动画，玻璃与阴影从简，语义令牌集中维护，动效只反馈状态变化，
窄屏 1024/768/390/320 全程适配；所有冲突以 frontend-redesign-brief.md 为准。」**

---

## 10. 来源

- 权威规范：[frontend-redesign-brief.md](./frontend-redesign-brief.md)（创始人 2026-11-07）
- 设计参照：[claude-design-study.md](./claude-design-study.md)、[2024–2026 SaaS 风格分类学](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md)（2026-04，仅色彩气质参考）、[Journey](https://thatgamecompany.com/journey/)（色彩语言）
- 字体（OFL）：[Noto Serif SC](https://fonts.google.com/noto/specimen/Noto+Serif+SC)、[Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)、[Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond)、[Inter](https://rsms.me/inter/)、[JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- 项目内：[failure-case-library.md](./failure-case-library.md)（CASE-10）、AGENTS.md（规则 10）
