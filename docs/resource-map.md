# 资源地图（resource-map）

> 编制：researcher（Agent Teams）｜ 日期：2026-11-07
> 目的：按创始人指令 5（资源整合、不闭门造车），系统搜集可借鉴的开源项目、成熟产品、学术成果、
> UI 设计资源；每条标注用途、许可证、可复用点、与规则 8 的冲突检查。
> 使用规则：引入任何第三方资源必须走 AGENTS.md 依赖审查流程（逐项经创始人审查）；
> 「待核实」的许可证在采纳前必须先确认；不引入与规则 8 冲突的内容。
> 备注：本会话 arXiv API 不可达（http/https 均失败），学术部分采用**可核验的经典文献主页/DOI 链接**，
> 未虚构任何论文条目；后续网络恢复后可补充 arXiv 检索。

---

## 1. 开源项目

### 1.1 SillyTavern 社区工具（直接同域，重点借鉴）

| 项目 | 用途 | 许可证 | 可复用点 | 规则 8 冲突检查 |
|---|---|---|---|---|
| [RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)（2025-12） | 找回误删对话（server 插件） | 待核实 | 备份目录扫描逻辑、恢复 UX（按时间点/角色过滤）、「读尾部 100KB + 读 metadata 而非文件名」的移动端性能优化思路 | 无冲突（纯本地） |
| [st-saves / Cloud Saves](https://github.com/breezewb/st-saves)（2025-07） | `/data` 目录备份到私有 GitHub 仓库（server 插件 + Git） | 待核实 | server 插件架构（plugins/ 目录、npm、/api/plugins/*/ui 面板）、版本化快照交互 | **有冲突**：云备份方向与本产品「默认不上传」相反——仅借鉴本地版本管理交互，不采用其云端方案 |
| [nat20-bridge](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md)（2026-10） | UI 扩展 + localhost Python sidecar（FastAPI 127.0.0.1） | 待核实 | **本项目插件架构直接先例**：ST 页面跨域 fetch loopback、CORS 处理、双进程状态提示 | 无冲突（纯本地） |
| [SillyTavern-HTML-Export](https://cocos-homes.com/writing/SillyTavern-HTML-Export)（2026-04） | 聊天导出 HTML（纯前端扩展 + slash command） | 待核实 | 纯前端扩展不碰文件系统实现导出/报告的模式、`/html-export` 命令参数设计（消息区间、用户名替换） | 无冲突 |
| [sillytavern-ext-chat-exporter](https://relatedrepos.com/gh/ztdf123/sillytavern-ext-chat-exporter)（2025-07） | 纯文本导出 | 待核实 | 最小扩展参考 | 无冲突 |
| [Cohee1207/SillyTavern-Dataset-Export](https://github.com/Cohee1207/SillyTavern-Dataset-Export)（2023-12） | 聊天转 Alpaca 数据集 | 待核实 | 扩展 manifest/打包范式 | 无冲突 |
| [SillyDroid Termux 迁移文档](https://github.com/alipymanbu/Android/blob/master/%E5%AE%98%E7%BD%91%E7%89%88APP%E4%B8%8B%E8%BD%BD/SillyDroid/Termux%E6%95%B0%E6%8D%AE%E8%BF%81%E7%A7%BB%E4%B8%8E%E5%A4%87%E4%BB%BD.md)（2026-09） | Android 一键迁移/备份（curl 脚本 + ZIP） | 待核实 | 整包打包-导入的交互与校验清单 | 无冲突 |
| [TavernWeave D4/D5 参考手册](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/D4_ST%E6%95%B0%E6%8D%AE%E7%9B%AE%E5%BD%95%E4%B8%8E%E9%83%A8%E7%BD%B2%E8%BF%90%E7%BB%B4.md)（2026-11 更新） | ST 数据目录/备份机制/扩展开发源码级手册 | 待核实 | 目录结构、备份字段（backups.chat.*/allowFullDataBackup）、扩展 API 双版本快照——已用于本团队多份报告 | 无冲突 |

### 1.2 角色卡解析/校验库（引擎层借鉴）

| 项目 | 用途 | 许可证 | 可复用点 | 规则 8 冲突 |
|---|---|---|---|---|
| [tavern-card](https://packages.ecosyste.ms/registries/pypi.org/keywords/sillytavern?order=desc&sort=dependent_packages_count)（PyPI，0.1.1） | 零依赖解析/写 ST 卡（V1/V2/V3 JSON + PNG tEXt/zTXt 嵌入） | 待核实 | Python 侧 V1/V2/V3 字段映射与 PNG 嵌入写法交叉验证；**不直接引入**，作为行为对照（我们已有适配器） | 无冲突 |
| [feverZHONG/liya-sillytavern-cards](https://github.com/feverZHONG/liya-sillytavern-cards)（2026-10） | 中文写卡方法 + 纯标准库 Python 工具（生成/校验/PNG 嵌卡） | 待核实 | V2 必填 14 字段校验、写卡质量深度检查（与我们修复分级可对照）；中文社区 ground truth | 无冲突 |
| [zer0thgear/character-card-editor](https://relatedrepos.com/gh/zer0thgear/character-card-editor)（2024-09） | 独立 V2/V3 规范卡编辑器 | 待核实 | V3/CHARX 编辑交互参考 | 无冲突 |
| [relatedrepos 同类清单（含 Rust 后端的多前端角色解析库等）](https://relatedrepos.com/gh/zer0thgear/character-card-editor) | 生态同类库索引 | — | 挖更多轮子入口 | 无冲突 |
| ST 官方 in-repo：[character-card-parser.js](https://github.com/SillyTavern/SillyTavern)（AGPL-3.0） | PNG chara/ccv3 块读写 | **AGPL-3.0** | **只读参考行为、不得复制代码**（AGPL 传染）；我们的 PNG 解析已用纯 Python 自研 | 无冲突（仅行为对照） |
| [trojblue/png-image-info](https://huggingface.co/spaces/trojblue/png-image-info/blob/788dfaa0e19f185cc9dbc88134f65d9dfd61c619/app.py)（2025-10） | PNG tEXt/zTXt/iTXt 块提取（stdlib struct+zlib） | 待核实 | 纯标准库 PNG 文本块解析写法参考 | 无冲突 |

### 1.3 PNG / JSON 容错解析与校验（引擎层）

| 项目 | 用途 | 许可证 | 可复用点 | 规则 8 冲突 |
|---|---|---|---|---|
| [pypng](https://pypi.org/project/pypng/) | 纯 Python PNG 读写 | MIT | 结构级 PNG 处理参考；注意：默认忽略 tEXt 块，文本块须自行处理（我们的 pngutil 已实现） | 无冲突 |
| [Pillow](https://pillow.readthedocs.io/) | 图像库（含 iTXt/tEXt 元数据） | MIT-CMU（HPND） | **不建议引入**：C 扩展 wheel，沙箱内安装与审查成本高；仅在需缩略图渲染时评估 | 无冲突 |
| [jsonrepair](https://github.com/josdejong/jsonrepair) | 损坏 JSON 自动修复（npm） | ISC/MIT 类（待核实） | 修复规则集参考（缺引号/尾逗号/截断处理）——与我们的 R0-001 尾逗号修复对照 | 无冲突 |
| [seriot.ch: Parsing JSON is a Minefield](https://seriot.ch/projects/parsing_json.html)（2016/2018 更新） | JSON 解析器差异实证研究 | 文章 | 解析歧义与容错边界的设计依据（规则 9：不猜字段，但要知道不同解析器行为差异） | 无冲突 |

### 1.4 备份工具（设计语义借鉴，非引入）

| 项目 | 用途 | 许可证 | 可复用点 | 规则 8 冲突 |
|---|---|---|---|---|
| [restic](https://restic.readthedocs.io/) | 快照式备份（去重/哈希树） | BSD-2-Clause | 快照+manifest+哈希校验语义、恢复 UX、「check 命令」体检概念 | 无冲突（本地仓库模式） |
| [BorgBackup](https://borgbackup.readthedocs.io/) | 去重压缩备份 | BSD-3-Clause | 版本化归档与完整性校验思路 | 无冲突 |
| [备份完整性验证技能示例](https://raw.githubusercontent.com/NeverSight/skills_feed/refs/heads/main/data/skills-md/mukul975/anthropic-cybersecurity-skills/validating-backup-integrity-for-recovery/SKILL.md)（2026-04） | SHA-256 manifest + 恢复演练工作流 | 文档 | 与我们的 manifest/恢复验证设计一致，可作为运维文档参考 | 无冲突 |

---

## 2. 成熟产品（竞品与借鉴对象）

| 产品 | 借鉴点 | 与我们的关系 | 规则 8 冲突 |
|---|---|---|---|
| [SillyTavern](https://docs.sillytavern.app/)（AGPL-3.0） | 内置「Download Backup」整包 zip、聊天自动备份、integrity 机制 | 首个适配对象；其自带能力是我们「体检+外部备份」的差异化空间 | 无 |
| [TavernAI 2](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/) | 从 ST 批量导入的向导式交互（类型预览、按类核对） | 迁移向导的直接参照 | 无 |
| [Foreverse](https://foreverse.app/zh/docs/guide-roleplay/migrate-from-sillytavern)（2026-08） | 整站搬家教程的产品化（备份 zip 识别、数量预览、逐类核对清单） | 迁移 UX 参照；注意其「密钥不随包走」声明与我们的规则 2 一致 | 无 |
| [RP-Card-Vault](https://www.toolcenter.ai/zh/tools/rp-card-vault) | local-first 卡管理（搜索/标签/备份） | 定位最接近的竞品 | 无 |
| [Backyard AI](https://backyard.ai/)、[Chub](https://chub.ai/) | 本地免费 + 云订阅的定价结构（反例：云推理与本地原则冲突） | 定价参照/反例 | **不作为方向**（云上传） |
| Linear / Vercel / Stripe / Raycast（见第 4 节） | 现代主义 UI 风格基准 | 设计方向参照 | 无 |

---

## 3. 学术成果（数据完整性 / 损坏修复 / 容错解析 / 本地优先）

> 本节为**文献级参考**（设计依据），不引入任何代码。arXiv API 本会话不可达，采用主页/DOI 链接，均为可核验的知名文献。

| 文献 | 主题 | 对本产品的启示 |
|---|---|---|
| [Ink & Switch: Local-first software](https://www.inkandswitch.com/local-first/)（2019，Kleppmann 等） | 本地优先软件七理想（无网络可用、数据自有等） | 产品哲学背书：本地优先不是妥协而是信任资产；「数据属于用户」写入定位与合规文案 |
| [Kleppmann & Beresford: A Conflict-Free Replicated JSON Datatype](https://arxiv.org/abs/1608.03960)（IEEE TPDS 2017） | JSON 并发编辑的 CRDT 合并 | 多人/多设备场景（团队版）的合并策略参考；当前 MVP 不做多端同步，留档 |
| [Bailis 等: Feral Concurrency Control（SIGMOD 2015）](https://www.bailis.org/papers/feral-sigmod2015.pdf) | 现实应用完整性的实证调查 | 「应用层完整性与并发写入风险是常态」——支持我们把「聊天被静默覆盖」（案例库 P0）当作一类通用工程问题设计防御 |
| [W3C: PNG 规范（ISO/IEC 15948）](https://www.w3.org/TR/png/) | PNG 块结构与 CRC | 我们 PNG 结构校验（块边界/CRC/IEND）的规范依据 |
| [seriot.ch: Parsing JSON is a Minefield](https://seriot.ch/projects/parsing_json.html) | 各解析器行为差异实证 | 容错解析边界设计（规则 9 的技术依据） |
| [ST 官方文档与源码级指南（DeepWiki 5.2/5.4/6.3、TavernWeave D4/D5）](https://deepwiki.com/SillyTavern/SillyTavern/5.2-chat-storage-and-persistence) | 聊天存储/资产/向量/扩展机制 | 已有报告 A/B 的事实底座（再次索引） |

> 说明：以上未虚构 arXiv 条目；「JSON 修复」「PNG 恢复」尚无公认的单一权威论文，实务以 jsonrepair 等开源实现与 W3C/ISO 规范为基准——与本项目「先样本后规则」的路径一致（规则 9）。

---

## 4. UI 设计资源

### 4.1 风格基准（借鉴对象）

| 对象 | 借鉴点 | 参考来源 |
|---|---|---|
| [Linear](https://linear.app/) | 深色底 + 单一强调色、1px 细边框、键盘优先、一次只展示一层信息 | [2026 SaaS 仪表盘设计趋势](https://adminlte.io/blog/saas-dashboard-design-examples/) |
| [Vercel](https://vercel.com/) + [Geist 字体](https://github.com/vercel/geist-font) | 黑白单色 + 胶片颗粒、编辑级克制排版 | 同上 + [2024–2026 SaaS 风格分类学](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md) |
| [Stripe](https://stripe.com/) | 表格即主界面、数字右对齐、虹彩渐变点缀 | 同上 |
| [Raycast](https://www.raycast.com/) | 深紫暗色、命令面板交互 | 官网 |
| [Arc](https://arc.net/) / [Notion](https://www.notion.so/) | 多彩流动 / 极简与 emoji 点缀 | 官网 |

### 4.2 可直接采用的开源资源（匹配「零构建原生 JS」约束）

| 资源 | 用途 | 许可证 | 采用方式 |
|---|---|---|---|
| [Pico.css](https://picocss.com/) | 单文件 classless CSS（深/浅色自动切换） | MIT | 候选：纯 CSS 文件 vendoring 进仓库，无需 npm/CDN |
| [Inter](https://rsms.me/inter/) | UI 西文字体 | OFL | 字体文件 vendoring（需创始人审查下载） |
| [Geist](https://github.com/vercel/geist-font) | 编辑感西文字体（Vercel 风格） | OFL | 候选西文字体 |
| [JetBrains Mono](https://www.jetbrains.com/lp/mono/) | 等宽字体（报告/哈希/日志） | OFL | vendoring |
| [Noto Sans SC](https://fonts.google.com/noto) | 中文正文字体 | OFL | vendoring（体积大，可选子集化） |
| [Radix Colors](https://www.radix-ui.com/colors) | 无障碍设计令牌（含 dark/light scale） | MIT | 颜色数值参考（实现用 CSS 变量，不引包） |
| [Open Color](https://yeun.github.io/open-color/) | 色彩系统 | MIT | 参考 |
| [Lucide](https://lucide.dev/) | 图标集（SVG） | ISC | 按需下载单个 SVG 内联 |
| [Heroicons](https://heroicons.com/) | 图标集（SVG） | MIT | 参考 |
| [shadcn/ui](https://ui.shadcn.com/) + [Radix UI](https://www.radix-ui.com/) + [Tailwind CSS](https://tailwindcss.com/) | React 组件生态（视觉与交互规范） | MIT | **不引包**（我们是原生 JS）；仅作组件语言/间距/交互的视觉参照 |
| [Appica UI](https://github.com/appica-dev/appica-ui)、[Sakani](https://www.npmjs.com/package/@sakaniui/react) | AI 应用组件库（Figma token 同源） | 待核实 | 深色面板/状态组件视觉参考 |
| [2024–2026 SaaS 风格分类学](https://raw.githubusercontent.com/MohamedAbdallah-14/prompt-to-asset/refs/heads/main/docs/research/10-ui-illustrations-graphics/10b-hero-images-and-marketing-banners.md)（2026-04） | 8 种现代落地页风格 + 配色/光照参数 | 文档 | 见 [ui-design-direction.md](./ui-design-direction.md) 两个风格方案的直接输入 |

### 4.3 多语言与动效

| 资源 | 用途 | 许可证 |
|---|---|---|
| [i18next](https://www.i18next.com/) | JS i18n 框架 | MIT（如需框架）；零依赖方案 = 自建 JSON 词典（先中英，W3 要求） |
| CSS `prefers-color-scheme` + `:has()`/容器查询 | 深色模式与响应式（原生，零依赖） | 标准 |
| [Framer Motion](https://motion.dev/) | 动效（React） | MIT——**仅参考其动效语言**（时长/缓动曲线），实现用 CSS transition 原生完成 |

---

## 5. 团队可立即采用的 Top 10 清单

1. **nat20-bridge 架构模式**（UI 扩展 + localhost sidecar）——ST 插件选项 2 的直接蓝图；先例已跑通 CORS/双进程问题。
2. **Pico.css 或等价单文件 CSS 起步**——零构建、深色模式内置，符合方案 A 约束；后续可替换为自建设计系统。
3. **Radix Colors / Open Color 的深色刻度**——直接产出色彩令牌（CSS 变量），无障碍对比度有保障。
4. **Inter + JetBrains Mono + Noto Sans SC（vendoring）**——中西文排版基线，无需 CDN。
5. **Lucide SVG 按需内联**——图标语言统一，零运行时依赖。
6. **restic/Borg 的「快照 + manifest + check」语义**——备份/体检模块的 UX 与校验设计参照（引擎侧已有同构设计）。
7. **jsonrepair 规则集 + seriot JSON 实证**——修复引擎 R0/R1 规则扩充的对照清单。
8. **TavernWeave D4/D5 手册**——ST 目录/备份/扩展 API 的源码级速查，供开发与 QA 直接引用。
9. **2024–2026 SaaS 风格分类学**——UI 两个风格方案（暗色科技风 / 明亮极简风）的参数来源。
10. **liya-sillytavern-cards 的校验方法**——中文社区写卡质量检查视角，与我们的体检报告互相补充（不引代码，只对照规则）。

---

## 6. 来源（补充说明）

- 主要来源已随条目内联标注（URL + 日期）。
- 学术部分：arXiv API 在本会话不可达，所列文献均为长期稳定的主页/DOI 链接，未虚构条目；恢复网络后可补充「JSON repair / data corruption detection」的 arXiv 检索结果。
- 「待核实」许可证项：采用前须由创始人/QA 确认许可证文本（AGENTS.md 依赖审查流程）。
