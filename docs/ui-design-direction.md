# UI 设计方向（ui-design-direction）

> 编制：researcher（Agent Teams）｜ 修订日期：2026-11-07（按创始人拍板的美学方向修订，推翻原「科技风」方案）
> 定位：**娱乐 / 陪伴类产品**的人文关怀美学——温暖、柔和、有生机、朦胧梦幻；
> 不采用硬核科技风（Linear/Raycast 系已整体移除，仅保留个别可用交互细节并降级说明）。
> 约束：本地 Web UI 为零构建原生 JS + 纯 CSS（方案 A）；所有实现资源可 vendoring、无 npm/CDN；
> 本文件只出方案与落地规格，不写项目代码。

---

## 1. 美学基调（一句话）

**「有生命力的温暖朦胧」**：像傍晚暖光穿过毛玻璃、像森林夜色里漂浮的萤火——界面是一个能让人安心停靠的
「数据小窝」，而不是一台机器控制台。

### 1.1 定位声明
- 产品本质：陪伴用户多年的角色与故事的**守护者**，界面要传达「被照顾」「安心」「鲜活」，而非「专业工具」。
- 设计原则：**温润 > 锐利**（大圆角、柔和阴影、无直角警告条）；**呼吸感 > 信息轰炸**（留白、缓动、渐进出现）；
  **朦胧梦幻 > 高对比硬派**（毛玻璃、光斑、粒子，但正文永远清晰可读）。

### 1.2 参考对象（新方向）

| 参考 | 借鉴点 |
|---|---|
| **Journey（风之旅人）** | 暖沙色、漂浮光尘粒子、神圣感的微光——粒子系统与暖光的直接参照（[thatgamecompany.com/journey](https://thatgamecompany.com/journey/)） |
| **动物森友会（Animal Crossing）** | 奶油底色、柔和圆角、生活化图标、低压力氛围（[animal-crossing.com](https://animal-crossing.com/)） |
| **lo-fi 温馨美学** | 暖渐变、颗粒质感、慢速漂移、黄昏色调 |
| **Apple「Liquid Glass」概念（WWDC24）** | 液态玻璃面板：`backdrop-filter` 模糊 + 边缘折射高光 + 悬浮层次（[Apple 设计资源](https://developer.apple.com/design/)） |
| **claymorphism 黏土风（轻量版）** | 圆润凸起、奶油色块、柔软投影（[2024–2026 SaaS 风格分类学](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md) 第 5 类） |
| **吉卜力式柔和场景感**（只取色彩语言，不模仿美术资产） | 暖绿、奶油、天空渐变 |

> 移除项说明：原 Linear/Raycast/Vercel「深黑+细边框+命令面板」方向整体删除；命令面板降级为
> 可选快捷键提示，不作为视觉语言；「科技风」色彩令牌（#0A0A0F 系）废弃。

---

## 2. 两主题 × 同一基调（原「两方案对比」改为此结构）

| 维度 | 主题 A「暖阳奶油」（明亮，默认） | 主题 B「森林夜语」（暗色） |
|---|---|---|
| 场景感 | 下午四点的暖光书房：奶油墙、橘色晚霞、漂浮的细小光尘 | 森林夜晚的营地：深绿树影、萤火微光、雾气般的玻璃面板 |
| 背景 | 奶油米 `#FAF3E8` + 缓慢漂移的暖色光斑（桃/杏/浅玫瑰） | 深森林绿 `#16251F` + 苔藓绿/雾青色光斑 |
| 面板 | 暖白毛玻璃 `rgba(255,249,240,.55)` + blur(20px) | 雾绿毛玻璃 `rgba(34,58,48,.45)` + blur(20px) |
| 强调色 | 暖橘（杏橙） | 鼠尾草绿（新叶色） |
| 粒子 | 金色光尘（黄昏感） | 萤火绿光点（森林感） |
| 共同基调 | 同一套圆角（12–20px）、同一柔缓动效曲线、同一毛玻璃语言、同一人文文案语气 | 同左 |

两主题共享全部结构、间距、组件与动效；切换只换令牌（CSS 变量）+ 粒子配色，零结构性改动。

---

## 3. 色彩令牌（两套完整，含语义与对比度说明）

### 3.1 主题 A「暖阳奶油」（默认亮色）

| 令牌 | 值 | 用途 |
|---|---|---|
| `--bg-canvas` | `#FAF3E8` | 页面画布（暖奶油） |
| `--bg-deep` | `#F3E7D3` | 次级底（区块分隔） |
| `--surface-glass` | `rgba(255,249,240,.55)` | 毛玻璃面板底色 |
| `--ink` | `#4A3B2C` | 正文（暖棕墨，对比度 ≈ 10:1） |
| `--ink-2` | `#8A7A64` | 次级文本（≈ 4.6:1，AA 通过） |
| `--ink-3` | `#B09A7E` | 弱文本/占位（仅辅助，不承载关键信息） |
| `--border` | `rgba(122,96,64,.14)` | 1px 边框 |
| `--accent` | `#E8843C` | 主强调（杏橙）：大按钮底/图标/焦点环 |
| `--accent-strong` | `#B95F1F` | 链接/关键强调文字（≈ 4.9:1，AA 通过） |
| `--accent-deep` | `#8A4A1C` | 按钮悬浮深橙 |
| `--on-accent` | `#3D2B1A` | **橙底上的文字用深棕**（≈ 6:1），**禁用白字橙底** |
| `--success` | `#6E9A5B` | R0 成功（苔绿） |
| `--warn` | `#C98A2B` | R1 待确认（蜂蜜黄） |
| `--suggest` | `#8A7A64` | R2 仅建议（中性暖灰） |
| `--danger` | `#C96A54` | R3 隔离（陶土红，柔和而非警报红） |
| 光斑色 | `#FFD9B8` `#FFE3B3` `#F9C9BE` | 背景漂移光斑（blur 80px，透明度 .45–.55） |
| 粒子色 | `#F2B25C` / `#FFE0A3` | 金色光尘 |

### 3.2 主题 B「森林夜语」（暗色）

| 令牌 | 值 | 用途 |
|---|---|---|
| `--bg-canvas` | `#16251F` | 页面画布（深森林绿，非冷黑） |
| `--bg-deep` | `#1B2E26` | 次级底 |
| `--surface-glass` | `rgba(34,58,48,.45)` | 毛玻璃面板 |
| `--ink` | `#EAF2EA` | 正文（浅鼠尾草，≈ 12:1） |
| `--ink-2` | `#A8C0B2` | 次级（≈ 7:1） |
| `--ink-3` | `#6E8A7A` | 弱文本 |
| `--border` | `rgba(190,220,200,.14)` | 边框 |
| `--accent` | `#7FBF9A` | 主强调（新叶绿，≈ 7.5:1 于画布） |
| `--accent-strong` | `#9AD8B4` | 链接文字（≈ 9:1） |
| `--accent-deep` | `#4F8A6B` | 悬浮深绿 |
| `--on-accent` | `#12241B` | 绿底上的深色文字（≈ 8:1） |
| `--success` | `#8CC9A8` | R0 |
| `--warn` | `#E3C06B` | R1（柔和琥珀） |
| `--suggest` | `#A8C0B2` | R2 |
| `--danger` | `#E08E7E` | R3（柔和珊瑚） |
| 光斑色 | `#2E5C44` `#3E7A5C` `#2A4D45` | 背景光斑（blur 90px，透明度 .4–.5） |
| 粒子色 | `#A3E6C0` / `#D8F5E2` | 萤火微光 |

### 3.3 语义规范（两主题共用）
- 状态识别**不只靠颜色**：R0/R1/R2/R3 与成功/警告/危险**永远伴随文字标签 + 图标形状**（色弱友好）。
- 对比度底线：正文 ≥ 4.5:1（AA），弱文本只用于辅助信息；关键数字与哈希用等宽字体右对齐（保留 Stripe 表格原则，视觉上软化处理）。
- 渐变只用于背景光斑与品牌区；组件表面零渐变（保持「毛玻璃 + 暖色」的克制）。

---

## 4. 液态玻璃 / 毛玻璃落地规格（零构建）

### 4.1 毛玻璃面板（frosted glass）
```css
/* 规格参考（非项目代码）：面板 */
.glass-panel {
  background: var(--surface-glass);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border: 1px solid var(--border);
  border-radius: 16px;               /* 温润圆角 */
  box-shadow: 0 8px 32px rgba(90,70,50,.10);   /* 柔和环境影，暗色主题用 rgba(0,0,0,.25) */
}
/* 顶部内侧高光：模拟玻璃折射 */
.glass-panel::before {
  content: "";
  position: absolute; inset: 0;
  border-radius: inherit;
  background: linear-gradient(135deg, rgba(255,255,255,.35), rgba(255,255,255,0) 40%);
  pointer-events: none;
}
```
- 层级：玻璃面板可叠 1–2 层（弹窗再模糊一层）；避免三层以上叠加（性能与可读性）。
- 降级：不支持 `backdrop-filter` 的环境自动回退纯色面板（`@supports` 检测）。

### 4.2 液态玻璃背景（liquid glass 氛围）
- 背景层放 3–4 个**大尺寸渐变光斑**：`position:fixed`、`filter: blur(80–100px)`、`opacity:.45–.55`、
  缓慢漂移（`transform: translate/scale`，周期 20–40s，`ease-in-out` 交替）；`pointer-events:none`、`z-index:-1`。
- 玻璃「流动感」：光斑错速漂移（相邻光斑周期差 1.3–1.7 倍）制造视差流动。

### 4.3 颗粒噪点（朦胧质感）
- 用 **SVG feTurbulence 的 data-URI** 作为全屏覆盖层：`opacity:.035`（亮）/`.05`（暗）、
  `mix-blend-mode: soft-light`（暗色主题可 `overlay`）、`pointer-events:none`；
  不引入外部噪点图片（零构建、无网络）。

### 4.4 毛玻璃按键（frosted buttons）
```css
/* 规格参考：主按钮（毛玻璃暖色） */
.btn-primary {
  background: color-mix(in srgb, var(--accent) 78%, transparent); /* 半透暖橙/新叶绿 */
  backdrop-filter: blur(12px);
  color: var(--on-accent);
  border: 1px solid rgba(255,255,255,.35);
  border-radius: 14px;
  transition: transform .2s, filter .2s;
}
.btn-primary:hover  { filter: brightness(1.06); transform: translateY(-1px); }
.btn-primary:active { transform: translateY(0); }
/* 次按钮：纯玻璃 */
.btn-ghost {
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
  color: var(--ink);
  border: 1px solid var(--border);
}
```
- 所有按钮文字用 `--on-accent`/`--ink` 深色或高对比色，**不使用白字低对比底**。

---

## 5. 粒子系统实现方案（轻量、可关、不挡内容）

### 5.1 方案选择
- **首选：CSS-only 粒子**（12–16 个 `<span>`/伪元素，`keyframes` 上浮+左右摇曳+透明度呼吸）——零 JS、
  零 rAF 开销，适合静态氛围；周期 8–16s 错开相位。
- **增强（可选）：单 `<canvas>` 粒子**（≤40 粒子，`requestAnimationFrame`），支持鼠标轻推（视差 <10px）
  与「萤火聚集」式轻微跟随；用于首屏与空状态页。
- 位置：`position:fixed` 背景层（`z-index:0`，内容在 `z-index:1`），**永不覆盖正文区域**；
  粒子密度在内容密集页（报告/表格）自动降为 0 或极低。

### 5.2 性能预算
- 目标：空闲 CPU ≤ 5%；canvas 在 `document.hidden` 时暂停；DPR 上限 2；容器尺寸变化时重建。
- 粒子数上限：桌面 40 / 移动 16；单粒子半径 1.5–4px + `box-shadow` 微光（CSS 粒子用 `filter: blur` 需谨慎，
  改为预制光晕径向渐变背景）。

### 5.3 主题切换
- 粒子颜色全部读 CSS 变量（`--particle-color`），主题切换只换变量；canvas 实现监听
  `matchMedia('(prefers-color-scheme: dark)')` + 手动主题开关双源，变更即重绘。

### 5.4 可关与无障碍
- `prefers-reduced-motion: reduce` → 粒子**静止为静态微光点**（或全关）、光斑停止漂移、所有呼吸动画降级。
- 设置页提供「氛围效果」三档：**标准 / 轻量 / 关闭**（默认标准；关闭档同时停 canvas 与光斑，省电友好）。

---

## 6. 字体与排版（温暖柔和，OFL 可 vendoring）

| 用途 | 字体 | 许可证 | 说明 |
|---|---|---|---|
| 西文标题/展示 | [Fraunces](https://fonts.google.com/specimen/Fraunces)（可变，soft 轴） | OFL | 柔和衬线，温暖文学感 |
| 西文正文/UI | [Nunito](https://fonts.google.com/specimen/Nunito) | OFL | 圆润无衬线，友善易读 |
| 中文标题/诗意场景/空状态 | [霞鹜文楷 LXGW WenKai](https://github.com/lxgw/LxgwWenKai) | OFL | 手写温润，陪伴感强 |
| 中文正文 | [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) | OFL | 长文可读性保障 |
| 数字/哈希/日志（仅技术区） | [JetBrains Mono](https://www.jetbrains.com/lp/mono/) | OFL | 等宽右对齐，视觉上弱化为辅助元素 |

- 字阶：12/13/14/16/20/28/40；行高 1.6–1.75（中文）；标题字重 600（文楷 500–600）。
- 排版语气：错误信息写「没关系，我们看看哪里出了问题」式的人话（配合 marketing-copy 的人文文案），
  但**技术结论（文件名、错误码、哈希）必须精确**。

---

## 7. 动效节奏（柔和缓动、呼吸感）

- 主曲线：`cubic-bezier(.22, 1, .36, 1)`（快入缓出，200–400ms）；出现动画：淡入 + 上移 6px。
- 呼吸感：光斑漂移 20–40s；粒子明暗呼吸 3–4s `ease-in-out alternate`；骨架屏用暖色微光脉冲（1.8s，透明度 .4–.7）。
- 列表逐项进场 stagger 30–50ms（上限 12 项，超出一次性出现，避免拖沓）。
- 危险操作弹窗：保留「文件元数据 + 双重确认」（源自失败案例库 CASE-10 的用户诉求），语气柔和但步骤不省。

---

## 8. 无障碍（对比度 / 色弱 / 动效开关）

1. 对比度：见第 3 节令牌表（正文 AA 达标；`--on-accent` 深色文字方案规避橙底白字低对比）。
2. 色弱：状态与修复等级**全部文字+图标双通道**；成功/警告/危险不依赖红绿区分（R3 用陶土红+圆形警示图标，R0 用苔绿+对勾图标）。
3. 动效：`prefers-reduced-motion` 全局降级 + 设置内「氛围效果」三档开关（第 5.4 节）。
4. 焦点：暖色焦点环（`outline: 2px solid var(--accent)` + 2px offset）；键盘可完成全部主流程。
5. 触控：最小点击区 44×44px；毛玻璃按钮 hover 态均配 active 态（触屏可见反馈）。

---

## 9. 落地资源清单（全部零构建 vendoring）

- 字体（OFL）：Fraunces、Nunito、LXGW WenKai、Noto Sans SC、JetBrains Mono —— 本地文件。
- 图标：[Lucide](https://lucide.dev/)（ISC）SVG 内联，1.8px 圆头描边（`stroke-linecap: round` 更温润）。
- 噪点：SVG feTurbulence data-URI（自生成，无依赖）。
- 光斑/粒子：纯 CSS + 可选单 canvas（自实现，见第 4–5 节规格）。
- 起步基线：无框架；Pico.css 仅作语义重置参考（不复用其默认视觉）。
- 风格参数来源：[2024–2026 SaaS 风格分类学（claymorphism 节）](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md)（2026-04）、[Apple 设计资源（Liquid Glass）](https://developer.apple.com/design/)、[Journey](https://thatgamecompany.com/journey/)、[Animal Crossing](https://animal-crossing.com/)。

---

## 10. 给创始人的一句话确认摘要

**「暖阳奶油（亮）+ 森林夜语（暗）两套主题共用同一种『朦胧、温润、有生机』的人文陪伴美学——
暖色光斑、萤火粒子、液态玻璃与毛玻璃按键全部零构建可落地，动效柔和、可一键关闭，正文对比度达标。」**

> 待确认小项（不影响开工）：① 中文标题字体是否采用霞鹜文楷（正文仍用 Noto Sans SC）；② 粒子默认档位
> 「标准」（建议）；③ 原命令面板快捷键是否保留为隐藏彩蛋（建议保留但不在 UI 露出）；④ 落地页随产品界面
> 同步改为暖色人文风（原「明亮编辑感」方案废弃，涉及 marketing-copy.md 的后续同步，由 lead 协调）。
