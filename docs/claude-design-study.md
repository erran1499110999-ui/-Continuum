# Claude 网页端设计系统研究报告（claude-design-study）

> 编制：researcher（Agent Teams）｜ 日期：2026-11-07
> **权威规范声明**：[frontend-redesign-brief.md](./frontend-redesign-brief.md)（创始人 2026-11-07，AGENTS.md 规则 10）
> 为前端执行权威规范，冲突时以 brief 为准（如：中文标题宋体系禁楷体/霞鹜文楷/手写、无粒子/光斑、
> 玻璃与阴影从简）；本报告的按键排布/动效/排版参数在 brief 无冲突处参考 Claude 网页端。
> 用途：按创始人指令（AGENTS.md 规则 8：前端字体、按键排布、交互方式**严格参照 Claude 网页端设计**；
> 美学基调为已确认的「温暖、可信、有生机」），为 frontend-developer 修订预览页提供设计依据。
> 方法：公开资料 + 高保真逆向工程手册（open-claude-ui，基于对 Claude Desktop 生产包 REA 逆向取证）
> + 品牌字体资料；逆向类数据标注来源版本，落地前由 frontend-developer 在真机复核关键值。
> 只出文档、不写代码；所有字体资源 OFL 可 vendoring。

---

## 1. 总览：Claude 的设计语言 = 「Warm Editorial（温暖编辑风）」

- 一句话：**衬线标题 + 人文无衬线正文 + 奶油纸感底色 + 陶土橙单一强调色 + 发丝细边框**——
  与创始人已确认的「暖阳奶油」主题天然同源，两套方向合并毫无违和。
- 关键特征：编辑感（serif/sans 分层）、微对比表面（Surface 0–3 四级阶梯）、陶土橙只给「整页最关键的
  一个 CTA」、0.5px 发丝边框、纸张堆叠式 24px 大圆角卡片。
- 来源：[Warm Editorial 设计文档](https://raw.githubusercontent.com/rohitg00/awesome-claude-design/main/design-md/warm/claude.md)、
  [Anthropic 品牌排版资料](https://github.com/asgeirtj/system_prompts_leaks/blob/79447393f49792cf0b77ccd9ec03af302d0c8eb2/Anthropic/artifact-types/design/artifact-type/reference/brand-typography.md)（2025-12）、
  [open-claude-ui 逆向手册](https://github.com/Caho1/open-claude-ui)（2026-10，基于 @ant/desktop v2.37337.1 ASAR 取证）。

---

## 2. 字体系统

### 2.1 Claude 官方字体（专有，仅作参照）
| 角色 | Claude 字体 | 特性 |
|---|---|---|
| 标题/展示（serif） | Tiempos Headline / Copernicus（品牌侧称 Anthropic Serif） | 字重 400–500 为上限（**永不用 700+**）；大字号 letter-spacing −1.5% |
| 正文/UI（sans） | Styrene A（品牌侧称 Anthropic Sans） | 人文几何无衬线，可变字重 300–800；UI 标签 500、字距 +2% |
| 代码/数字（mono） | GT America Mono（品牌侧称 Anthropic Mono） | 仅用于代码与数据 |

官方 fallback 栈（可原样借用）：Sans `system-ui,'Segoe UI',Roboto,Helvetica,Arial`；Serif `Georgia,'Times New Roman'`；Mono `'JetBrains Mono','SF Mono',Monaco`。

### 2.2 可 vendoring 的 OFL 近似字体清单（对照 resource-map 补充）
| 角色 | 推荐近似（OFL） | 备选（OFL） | 说明 |
|---|---|---|---|
| 标题 serif | **[Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond)**（主选） | Fraunces、Lora | 高对比衬线、编辑感强；备选 Fraunces（软衬线+光学轴）或 Lora；字重锁定 400–500；**最终以创始人确认为准** |
| 正文 sans | **[Inter](https://rsms.me/inter/)** | Instrument Sans | Claude 社区文档的公认 fallback；替换原 ui-design-direction 中的 Nunito（Nunito 过圆，与 Styrene 的人文几何感不符） |
| 中文标题 | **[Noto Serif SC（思源宋体）](https://fonts.google.com/noto/specimen/Noto+Serif+SC)** | `"Songti SC","STSong","SimSun",serif` | **宋体系（brief 强制：禁楷体/霞鹜文楷/手写）**；不照搬西文负字距，保持自然字距 |
| 中文正文 | **[Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)** | `"PingFang SC","Microsoft YaHei",sans-serif` | 黑体系正文（brief 四） |
| 代码/哈希 | **[JetBrains Mono](https://www.jetbrains.com/lp/mono/)** | SF Mono 不可 vendoring | 恰为 Claude 官方 mono fallback，零争议 |

> 结论：字体栈 = `Cormorant Garamond(西文标题主选；备选 Fraunces/Lora，最终以创始人确认为准) + Noto Serif SC(中文标题，宋体系；禁楷体/霞鹜文楷/手写) + Inter(西文正文/UI) + Noto Sans SC(中文正文，黑体系) + JetBrains Mono(代码/数字)`，全部 OFL 可 vendoring；本轮以已批准资源 + 系统回退为先（brief 四）。

---

## 3. 色彩系统（与「暖阳奶油」主题直接合并）

| 令牌 | Claude 值 | 我们的映射建议 |
|---|---|---|
| 画布（Parchment） | `#f5f4ed` | 暖阳奶油 `--bg-canvas` 微调至 `#f7f4ec`（两版取中） |
| 墨色（Near Black） | `#141413` | `--ink` 暖棕墨可保留 `#4A3B2C`（Claude 营销页用纯暖黑，产品 UI 用暖棕更软，二选一由 frontend 预览定） |
| 次级文本（Olive Gray） | `#5e5d59` | `--ink-2`（≈4.6:1，AA 通过） |
| **陶土橙（Clay）** | `#d97757` | `--clay`：**整页唯一的最强 CTA 专用色**（Claude 铁律：never 用于装饰或第二按钮）；常规强调仍用我们的杏橙 `--accent #E8843C` |
| 品牌深陶土 | `#c6613f` | 桌面版品牌色，可选作按钮 hover 深色 |
| 特色编辑卡 | `#f5e3c7` | 精选/重点卡片的奶油底 |
| 微对比表面 | Surface 0–3 四级 | 面板层级改为「玻璃 + 四级微对比」：Surface 0 透明玻璃、1–3 逐级加深 |
| 禁忌 | **禁止冷灰**（cool grays） | 与已确认基调一致：中性色一律带暖/绿色相 |

暗色主题（森林夜语）沿用已确认令牌（`#16251F` 底、新叶绿强调），按 Claude 暗色做法：深色半透明表面（`white/10`、`white/15` 层级）+ 暖黑非纯黑。

---

## 4. 按键样式与层级（逆向精确值，frontend 可直接照做）

### 4.1 五阶高度标尺（--cds-rem-scale: 16/17 ≈ 0.9412 光学缩放）
| 尺寸 | 高度 | padding | 圆角 | 字号/角色 |
|---|---|---|---|---|
| xxs | ≈19px | px-1.5 py-0 | 4px | 11px 行内微操作 |
| xs | ≈23px | px-2 py-0.5 | 6px | 11.5px 标签删除、辅助栏 |
| sm | ≈26px | px-2.5 py-1 | 8px | 12.5px 菜单项、输入框内胶囊 |
| **md（默认）** | ≈32px | px-3.5 py-1.5 | 8px | 13.5px 标准动作 |
| lg | ≈40px | px-5 py-2 | 12px | 15px 首要引导 |
| 嵌套衰减 | 17 / 18.8 / 20.7 / 26.35px | — | — | 工具栏/Composer 内按钮自动缩小 |

### 4.2 六大变体（两层结构：外层重置壳 + 内层绘景层 data-cds-part="paint"，杜绝 hover 尺寸抖动）
| 变体 | 样式要点 |
|---|---|
| **secondary（默认）** | 透明底、**无硬边框**（单闭合边框原则）、hover 微灰（dark: white/10→15）、pressed 强调色文字 |
| **primary** | 陶土实色填充 + 深色文字/白色文字（按对比度），hover 变深、active brightness .95；**全页仅一处** |
| ghost | 图标/内联微操作，hover 5% 灰度渐入 |
| danger | 警示深红 + 专属红色 focus 光晕 |
| brand | `#c6613f` 深陶土（桌面品牌动作） |
| **onContent** | 悬浮在图片/内容上的毛玻璃按钮：`backdrop-blur-md` + 4px 羽化 + 深色半透明；**注意 brief 七「阴影与玻璃效果从简」——仅在确有内容浮层时按此变体处理，不扩散为装饰性玻璃层** |

### 4.3 交互物理（Claude 特色，可抄）
- **15 阶纯 CSS 弹簧**（`linear()` 曲线）：按压 0.975 缩放，松开 40% 时刻过冲至 1.0915 → 微回弹 0.9914 → 1.0004 收敛；小按钮细腻、大按钮扎实（阻尼随高度自适应）。
- 焦点：`focus-visible` 发丝环（hairline ring，高分屏视网膜补偿），无粗黑描边。
- 组合按钮（joined）：首项去右圆角、中间全直角、末项去左圆角。
- 签名细节：**填充按钮底部 8px 圆角**（bottom-only radius，替代胶囊）。

### 4.4 分段控件（Segmented Pills）
- 轨道：999px 全圆角 + **严格 1px 环绕内边距**；滑块几何等分（`left: 1px + index×(100%−2px)/n`）。
- 双层光学投影（浅色 `0 1px 2px #0000000f + 0 2px 6px #0000000d`，暗色对应加深）。
- 容器查询自适应折叠：两段 ≤180px / 三段 ≤254px 时隐藏非激活项标签（只留图标）。

---

## 5. 间距与栅格

- 间距基网格 **4px**（4/8/12/16/24/32/48/64/96/128），16px 为基础单位（卡片内边距、元素间距）。
- 栅格：应用界面 = 侧栏 + 主内容；内容栏行长 65–72 字符；容器上限 1280–1440px（标准参考值，Claude 具体值以真机测量复核）。
- 响应式断点（标准四档）：640 / 768 / 1024 / 1280px；移动端 serif 大标题 62→36px 收缩。
- 长文排版：`text-wrap: balance`（标题）/ `pretty`（正文）。

---

## 6. 卡片、输入控件与附件磁贴

- **卡片**：24px 圆角（paper-stacked 纸张堆叠感）、0.5px 发丝边框（border-tertiary）、Surface 0–3 层级；
  特色编辑卡可用 `#f5e3c7`。
- **输入控件**：预样式裸标签（input/select/textarea/range），0.5px 边框 + hover 次级底色；聚焦发丝环。
- **附件磁贴（可直接用于我们的备份文件清单）**：
  - 严格正方形 `7.5rem`（缩放后 ≈112.94px）+ 同心圆角（rounded-card）；
  - 移除按钮：**20px 圆形、悬浮右上角外凸 8px**（absolute -end-2 -top-2）、按压 scale .9；
  - **双向中间截断**：长文件名保留扩展名（`…stem.ext`），扩展名永远 `shrink-0` 锁定——正是我们
    长文件名/路径展示的刚需；
  - 左上角**大写类型徽标**（PNG/JSON/JSONL/CHARX…），等宽字形 + 微弱背景胶囊。

---

## 7. 动效节奏

| 元素 | Claude 参数（可照抄） |
|---|---|
| 按钮弹簧 | 15 阶 `linear()` 曲线（见 4.3），按下 fast ease-out、松开 slow 弹簧 |
| 状态灯（6px） | ready 常亮；running 1.2s blink（透明度 .3↔1）；**clay 呼吸 3.0s（scale .86→1、brightness .96→1.06）**——映射我们的「扫描中/备份中」运行态 |
| 思考三点 | 3px 圆点、gap 3.5px、周期 1.9s cubic-bezier(.4,0,.2,1)、相位 0/.15/.3s——映射「引擎任务执行中」 |
| 骨架扫光 | 105° 倾角渐变、**严格 2.0s linear**、translate ±100%——映射扫描页/列表加载 |
| 弹窗 | 双层投影（外高斯模糊 + 内倒角高光）；嵌套弹窗父级 `blur(2px)` + 半透明遮罩；滚动渐隐遮罩（28px 渐变） |
| 全局 | 快缓出（duration-fast ease-out）、慢弹簧（duration-slow spring）；`prefers-reduced-motion` 全降级 |

> 与已确认基调的衔接：呼吸感光斑（20–40s 漂移）与粒子（萤火/光尘）叠加在 Claude 的
> 「快交互、慢氛围」节奏之上——**交互动效抄 Claude（克制的毫秒级），氛围动效走已确认的朦胧路线（秒级）**。

---

## 8. 响应式断点与布局行为汇总

- 断点：640（sm）/ 768（md）/ 1024（lg）/ 1280（xl）。
- 侧栏：窄屏折叠为图标态；分段控件容器查询折叠（见 4.4）；弹窗六阶宽度 400/520/720/880/1024/1152 + 视口
  安全上限（`100dvh − 标题栏 − safe-area`），移动端弹窗自动接近全宽。
- 大标题：62px 桌面 → 36px 移动；正文列宽 65–72ch。

---

## 9. 给 frontend-developer 的 10 条可直接照做的规范要点

1. **字体栈（全 OFL，对齐 brief 四）**：Cormorant Garamond(西文标题主选，≤500 字重；备选 Fraunces/Lora，**最终以创始人确认为准**) / Noto Serif SC(中文标题宋体系，回退 `Songti SC/STSong/SimSun`；**禁楷体/霞鹜文楷/手写**) / Inter(西文正文/UI) / Noto Sans SC(中文正文黑体系，回退 `PingFang SC/Microsoft YaHei`) / JetBrains Mono(代码数字)；西文 fallback 顺序抄 Anthropic 官方栈。
2. **颜色令牌双主题**：暖阳奶油（Claude 系：Parchment #f5f4ed、墨 #141413、Olive Gray #5e5d59）+ 森林夜语；**Clay #d97757 只给每页唯一最强 CTA**，常规强调用杏橙 #E8843C；全站禁用冷灰。
3. **按钮五阶高度标尺**（19/23/26/32/40px + 嵌套衰减），md 为默认；secondary 为默认变体（无硬边框+hover 微灰）；onContent 毛玻璃变体用于悬浮控件。
4. **按钮物理**：15 阶 linear() 弹簧 + 按下 0.975 缩放 + 绘景层分离；focus-visible 发丝环；组合按钮三态圆角协议；填充按钮用底部 8px 圆角签名细节。
5. **边框与圆角**：0.5px hairline 边框；控件 4/6/8/12px；卡片 24px paper-stacked；玻璃面板叠加四级微对比 Surface。
6. **分段控件**：999px 轨道 + 1px 内边距 + 几何等分滑块 + 双层投影；两段 ≤180px / 三段 ≤254px 容器查询折叠。
7. **状态系统**：6px 状态点四态（ready/running 1.2s/error/clay 3s 呼吸）；思考三点波（3px、1.9s、相位 0/.15/.3）；骨架 105° 扫光 2s——全部映射到扫描/备份/迁移的运行与等待态。
8. **弹窗**：六阶宽度 400–1152px；视口安全上限；嵌套弹窗父级 blur(2px)；危险确认弹窗保留「文件元数据 + 双重确认」（案例库 CASE-10 诉求）。
9. **附件磁贴**：7.5rem 正方形、同心圆角、20px 悬浮移除按钮、双向中间截断保扩展名、大写类型徽标——直接用于备份包文件清单与扫描结果列表。
10. **排版与响应式**：字号模块 1.25 阶（13/15/17/21/26/32/40/50/62）、大标题 −1.5% 字距与 balance、间距 4px 基网格、断点 640/768/1024/1280、内容列 65–72ch；所有交互动效毫秒级克制、氛围动效秒级朦胧、reduced-motion 全降级。

> 落地提示：open-claude-ui 的 **tokens.css / pure.css 可脱离 React/Tailwind 单独 vendoring**
> （261 个设计令牌 + 零 JS 滚动消隐），是快速对齐的捷径——**许可证待核实后方可引入**（依赖审查流程）。

---

## 10. 来源

- [open-claude-ui 逆向手册（五阶按钮/弹簧/分段控件/状态灯/弹窗/磁贴，REA v6.5 取证 @ant/desktop v2.37337.1）](https://github.com/Caho1/open-claude-ui)（2026-10）
- [Claude (Anthropic) — Warm Editorial 设计文档](https://raw.githubusercontent.com/rohitg00/awesome-claude-design/main/design-md/warm/claude.md)
- [Anthropic 品牌排版（字体栈/字阶/fallback）](https://github.com/asgeirtj/system_prompts_leaks/blob/79447393f49792cf0b77ccd9ec03af302d0c8eb2/Anthropic/artifact-types/design/artifact-type/reference/brand-typography.md)（2025-12）
- [Claude 设计系统模板（Parchment/Clay 用法铁律）](https://github.com/yc-software/qm/blob/5546fa13e620a3835e1b36cd945d43842ec29955/skills-seed/popular-web-designs/templates/claude.md)（2026-11）、[Refero 风格库 Anthropic 条目](https://styles.refero.design/style/d469cba4-c448-4a43-a033-883f8bfcdc42)（2026-02）
- [Claude 生成式 UI 组件指南（0.5px 边框/按钮预样式）](https://github.com/dwsy/agent/blob/291e371f7dc7a795f0141d2a5558285231eaa9a/extensions/generative-ui/claude-guidelines/sections/ui_components.md)（2026-10）
- 字体（OFL）：[Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond)（西文标题主选）、[Fraunces](https://fonts.google.com/specimen/Fraunces)、[Lora](https://fonts.google.com/specimen/Lora)（备选）、[Noto Serif SC](https://fonts.google.com/noto/specimen/Noto+Serif+SC)（中文标题宋体系）、[Inter](https://rsms.me/inter/)、[Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)（中文正文黑体系）、[JetBrains Mono](https://www.jetbrains.com/lp/mono/)；霞鹜文楷已按 brief 废弃（禁楷体/手写风格）。
- 项目内联动：[ui-design-direction.md](./ui-design-direction.md)（暖阳奶油/森林夜语）、[failure-case-library.md](./failure-case-library.md)（CASE-10）

> 说明：逆向类数值（按钮像素、弹簧曲线等）来自第三方对 Claude Desktop 生产包的取证手册，
> 属「参考规格」而非官方文档；frontend-developer 落地前应以真机实测复核关键值，避免照搬误差。
