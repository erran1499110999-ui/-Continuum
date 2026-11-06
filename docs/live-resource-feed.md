# 持续资源简报（live-resource-feed）

> 维护：researcher（Agent Teams，常驻资源与智慧中枢）｜ 建立：2026-11-07
> 格式：每批次追加 ≥5 条；每条含 类别 / 来源+日期 / 用途 / 许可证 / 可落地动作 / 优先级 / 受益 agent。
> 规则：只读外部资源、标注来源、许可证待核实项须经创始人审查后再引入；不引入规则 8 冲突内容。

---

## 批次 1（2026-11-07）

| # | 类别 | 条目 | 来源+日期 | 用途 | 许可证 | 可落地动作 | 优先级 | 受益 agent |
|---|---|---|---|---|---|---|---|---|
| 1 | 开源组件 | **open-claude-ui**（Claude 设计系统高保真还原，261 令牌 + 纯 CSS 层可脱离 React 使用，含零 JS 滚动消隐、按钮五阶标尺/15 阶弹簧） | [GitHub](https://github.com/Caho1/open-claude-ui)（2026-10） | claude-design-study 10 条规范的落地捷径 | **待核实** | 核实许可证 → 创始人批准后 vendor tokens.css/pure.css 作设计参照 | 高 | frontend-developer |
| 2 | 开源组件 | **tsParticles**（含 Firefly 萤火虫预设、pauseOnBlur 内置） | [官网](https://particles.js.org/) | 粒子/萤火氛围（canvas 增强路线） | MIT | **注意：frontend-redesign-brief（规则 10）明确「不新增粒子/装饰动画」→ 本条降级为「暂不采用」，仅存档** | 低（存档） | frontend-developer |
| 3 | 工具/技能 | **extract-design-system**（从公开站点抽取设计令牌生成 CSS 变量，skills.sh 生态安装） | [npm](https://www.npmjs.com/package/extract-design-system)（2026-05） | 从 claude.ai 等抽令牌做参照 | 待核实 | 产出仅参考、勿商用专有资产；创始人批准后安装 | 中 | frontend-developer |
| 4 | 开源项目 | **jsonrepair**（损坏 JSON 自动修复库，修复规则集） | [GitHub](https://github.com/josdejong/jsonrepair) | 修复引擎 R0/R1 规则扩充的对照清单 | ISC/MIT 类（待核实） | qa 与外部会话对照现有 R0-001 规则，评估可吸收的容错边界 | 中 | qa-reviewer / 外部会话 |
| 5 | 工具/运维 | **Essential MCP Servers 实战指南**（Filesystem 授权铁律：绝不授 / 或主目录等） | [codewithclaude.net](https://codewithclaude.net/mcp/essential-servers)（2026-09） | MCP 配置运维参考 | 文档 | lead 配置 MCP 时按此约束目录授权 | 中 | lead |
| 6 | 技术情报 | **ST PR #5123（CORS 可配置化）**：ST 服务器默认 CORS 极严（origin:null 仅 OPTIONS），社区推进可配置 | [GitHub PR#5123](https://github.com/SillyTavern/SillyTavern/pull/5123)（2026-02） | 插件选项 2（sidecar 内嵌 API）的前置知识 | AGPL（上游仓库） | developer 在选项 2 设计时复核 CORS 结论（我方服务自控 CORS，不受此 PR 影响） | 低 | developer |
| 7 | 设计参考 | **2026 SaaS 仪表盘趋势**（Linear 一次一层信息、Stripe 表格即界面/数字右对齐） | [adminlte.io](https://adminlte.io/blog/saas-dashboard-design-examples/)（2026-07） | 报告/清单页的表格与信息分层语言 | 文章 | frontend 报告页表格规范输入（与 brief 不冲突：仅取排版原则） | 中 | frontend-developer |

---

## 发散主题轮转（每批 1 篇：深挖一个角度 → 一条可落地建议 + 受益 agent）

### 第 1 篇｜增长与分发（2026-11-07）
- 观察：ST 生态的分发事实——官方内容库（申请制）+ 内置安装器 URL + Discord/Reddit 求助场景 +
  中文社区（贴吧/NGA）的「教程渴求」；竞品 Foreverse/TavernAI 2 都在用「迁移教程文」获客。
- 结论：本项目最短分发路径不是广告，而是**「可被搜索的教程内容」**：把 failure-case-library 的
  真实场景改写成「升级前自查清单」「白屏抢救手册」「误删找回五步」三类双语内容页（先于产品功能发布，
  仅链接到 GitHub）。
- **可落地建议（1 条）**：lead 排期一个「内容页任务」（docs 输出 + README 链接），researcher 提供
  文案（复用 marketing-copy 模板 A/C），发布到 GitHub Pages/仓库 wiki 后由社区渠道分发——内容资产
  先于插件上线，为 T1 引流蓄水。受益 agent：lead（排期）/ researcher（文案）/ frontend-developer（页面）。

### 第 2 篇｜合规与隐私（2026-11-07）
- 观察：本地优先产品「不收集处理个人信息」→ GDPR/PIPL 的处理者义务基本不触发（research-business.md 已论证）；
  但三个细节易被忽略：① 产品经手 `secrets.json`（API 密钥明文）——备份时是本地复制，须在 UI/文档明示
  「备份包含密钥文件」并默认不导出密钥到分享包（对照 Foreverse「备份不含密钥」的口径）；② 隐私文案措辞
  须精确——「默认不上传」而非「绝不联网」（依赖更新等场景）；不做任何遥测才能兑现「无遥测」声明；
  ③ 分发端合规：README 需隐私说明 + 第三方依赖清单 + 许可证（提示词 10 发布审查项；创始人指令 3 双语）。
- **可落地建议（1 条）**：lead 在 W3/插件 P4 任务中并入「隐私声明（中英双语）定稿」子任务，researcher
  提供初稿（基于 marketing-copy 合规红线扩展为 6 条：无账号/无云端/无遥测/密钥默认不导出/修复不覆盖原文件/
  许可证与依赖清单）；qa-reviewer 第 3 轮发布审查时逐条核对「声明与实现一致」。受益 agent：lead（排期）、
  researcher（初稿）、qa-reviewer（核对）。

## 批次 2（2026-11-07）

| # | 类别 | 条目 | 来源+日期 | 用途 | 许可证 | 可落地动作 | 优先级 | 受益 agent |
|---|---|---|---|---|---|---|---|---|
| 1 | 工具/技能 | **备份完整性验证与灾难恢复技能**（SHA-256 manifest + 恢复演练工作流，restic/borg/rclone 对照） | [skill 文档](https://raw.githubusercontent.com/NeverSight/skills_feed/refs/heads/main/data/skills-md/mukul975/anthropic-cybersecurity-skills/validating-backup-integrity-for-recovery/SKILL.md)（2026-04） | W3 备份/校验模块的验证步骤设计参照（与我们的 manifest 设计同构） | 文档 | qa/developer 把「恢复演练」步骤纳入 W3 验收（恢复后逐文件哈希比对已在提示词 4） | 中 | qa-reviewer / developer |
| 2 | 字体资源 | **Noto Serif SC（思源宋体）**：中文标题宋体系 vendoring 候选 | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Serif+SC) | brief 四：中文标题宋体系；未 vendoring 用系统回退 | OFL | **只记录建议与许可证需求，本轮不下载**（brief 四）；经创始人许可证流程批准后再 vendoring | 中 | frontend-developer |
| 3 | 工具/运维 | **MCPBundles《MCP Server Examples》**：官方参考服务器（Everything/Fetch/Filesystem/Git/Memory/Sequential Thinking/Time）与厂商服务器单命令启动清单 | [mcpbundles.com](https://www.mcpbundles.com/guides/mcp-server-examples)（2026-10-19） | lead 配置 MCP 时的权威对照清单（resource-map Top 5 的落地参考） | 文档 | 创始人批准 MCP 后按此清单逐项启动与授权目录 | 中 | lead |
| 4 | 技术情报 | **ST 1.19.0 已合并的完整性修复**（#5458 首行损坏静默覆盖、#5944 CJK 备份键、#5980 覆盖前快照） | [releases/latest](https://github.com/SillyTavern/SillyTavern/releases/latest) | 案例库 P0 多条上游已修复——引擎检测项应维护「上游已修复版本」标注，告警话术按用户 ST 版本区分 | AGPL（上游仓库） | developer/外部会话在引擎告警话术中区分「旧版易发」与「新版已修复」，避免对 1.19+ 用户过度恐吓 | 高 | developer / 外部会话 |
| 5 | 设计参考 | **Someclaudeskills web_design_expert 布局参考**（8px 间距基、断点 640/768/1024/1280、12 列网格决策树） | [someclaudeskills.com](https://someclaudeskills.com/docs/skills/web_design_expert/references/layout-systems/) | 布局系统通用参考（brief 未指定间距基，此仅作建议） | 文档 | frontend 在 brief 允许范围内参考间距与断点惯例 | 低 | frontend-developer |
| 6 | 开源组件 | **Caho1/open-claude-ui 零 JS 滚动消隐遮罩**（`[data-cds-scroll-fade]`，@property 驱动） | [GitHub](https://github.com/Caho1/open-claude-ui)（2026-10） | 长列表/报告页滚动渐隐的纯 CSS 实现参考（不引包） | 待核实 | 仅参考实现思路自研（与 brief「不新增装饰动画」不冲突：属状态反馈） | 低 | frontend-developer |

## 发散主题轮转（每批 1 篇：深挖一个角度 → 一条可落地建议 + 受益 agent）

### 第 1 篇｜增长与分发（2026-11-07）
- 观察：ST 生态的分发事实——官方内容库（申请制）+ 内置安装器 URL + Discord/Reddit 求助场景 +
  中文社区（贴吧/NGA）的「教程渴求」；竞品 Foreverse/TavernAI 2 都在用「迁移教程文」获客。
- 结论：本项目最短分发路径不是广告，而是**「可被搜索的教程内容」**：把 failure-case-library 的
  真实场景改写成「升级前自查清单」「白屏抢救手册」「误删找回五步」三类双语内容页（先于产品功能发布，
  仅链接到 GitHub）。
- **可落地建议（1 条）**：lead 排期一个「内容页任务」（docs 输出 + README 链接），researcher 提供
  文案（复用 marketing-copy 模板 A/C），发布到 GitHub Pages/仓库 wiki 后由社区渠道分发——内容资产
  先于插件上线，为 T1 引流蓄水。受益 agent：lead（排期）/ researcher（文案）/ frontend-developer（页面）。
- **⚠ 状态更新（2026-11-07）**：投放已冻结（规则 13）。本篇内容页建议仅限「内容创作」，发布与否
  属投放动作，须待市场验证并经创始人确认后执行（见 plugin-market-validation.md §6）。

### 第 2 篇｜合规与隐私（2026-11-07）
- 观察：本地优先产品「不收集处理个人信息」→ GDPR/PIPL 的处理者义务基本不触发（research-business.md 已论证）；
  但三个细节易被忽略：① 产品经手 `secrets.json`（API 密钥明文）——备份时是本地复制，须在 UI/文档明示
  「备份包含密钥文件」并默认不导出密钥到分享包（对照 Foreverse「备份不含密钥」的口径）；② 隐私文案措辞
  须精确——「默认不上传」而非「绝不联网」（依赖更新等场景）；不做任何遥测才能兑现「无遥测」声明；
  ③ 分发端合规：README 需隐私说明 + 第三方依赖清单 + 许可证（提示词 10 发布审查项；创始人指令 3 双语）。
- **可落地建议（1 条）**：lead 在 W3/插件 P4 任务中并入「隐私声明（中英双语）定稿」子任务，researcher
  提供初稿（基于 marketing-copy 合规红线扩展为 6 条：无账号/无云端/无遥测/密钥默认不导出/修复不覆盖原文件/
  许可证与依赖清单）；qa-reviewer 第 3 轮发布审查时逐条核对「声明与实现一致」。受益 agent：lead（排期）、
  researcher（初稿）、qa-reviewer（核对）。

### 第 3 篇｜测试工程（2026-11-07）
- 观察：测试体系强在 Python 侧（数百例+三轮审核），弱在：① JS 侧依赖 Node 可用性（st-plugin-plan 5.1 未验）；
  ② failure-case-library §5 的「24 案例合成样本设计」目前是文档，尚未转成测试任务；③ 无属性测试
  （hypothesis 仅建议）；④ 真实授权样本为 0——合成样本只能证明「代码按预期跑」，不能证明「预期符合现实」。
- **可落地建议（1 条）**：lead 把 failure-case-library §5 的样本表拆成「合成样本任务卡」逐条派给
  developer/qa（每条含：样本要点+断言方向+案例编号），每完成一条在案例库打勾回填——防止 24 条设计
  输入腐化为纸面文档。受益 agent：lead（拆卡派单）/ developer、qa-reviewer（执行）。
- 待验证项同步：JS 单测的真实运行证据链（Node 实测）在 P2 前置门补齐；真实样本缺口靠 12 章「3 样本」
  门槛推进，不因合成样本齐全而放松。

## 批次 3（2026-11-07）

| # | 类别 | 条目 | 来源+日期 | 用途 | 许可证 | 可落地动作 | 优先级 | 受益 agent |
|---|---|---|---|---|---|---|---|---|
| 1 | 技术依据 | **ST `default/config.yaml` 与 `src/constants.js` 的 USER_DIRECTORY_TEMPLATE**（1.12+ 用户目录结构权威定义，含 group chats/User Avatars 空格目录名、多用户 data/_storage） | [TavernWeave D4 手册](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/D4_ST%E6%95%B0%E6%8D%AE%E7%9B%AE%E5%BD%95%E4%B8%8E%E9%83%A8%E7%BD%B2%E8%BF%90%E7%BB%B4.md)（2026-11） | W3' 一键急救备份「自动探测 data 目录」的结构依据（空格目录、多用户句柄枚举） | 上游 AGPL（仅参考结构） | developer 实现自动探测时按此清单覆盖目录与引号处理 | 高 | developer |
| 2 | 流程机制 | **ST 1.20 动向跟踪机制**：GitHub releases 页每周快照 + newreleases.io 订阅 | [releases](https://github.com/SillyTavern/SillyTavern/releases)、[newreleases.io](https://newreleases.io/project/github/SillyTavern/SillyTavern) | 把「版本漂移监控」制度化（research-st-plugin 每 release 冒烟的前置） | — | lead 建每周例行项；researcher 在 business-feed 记录影响 | 中 | lead / researcher |
| 3 | 审批材料 | **Noto Serif SC vendoring 申请单预写**（名称/OFL 许可证/文件体积/回退策略/影响范围） | [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Serif+SC) | brief 四：本轮用系统回退，新字体只记录建议与许可证需求 | OFL | frontend 预写申请单交创始人；**未批准前不下载** | 中 | frontend-developer |
| 4 | 排版参考 | **MDN `text-wrap: balance/pretty`**：标题平衡断行与正文流式换行（Claude 排版惯例的标准实现） | [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap) | brief 三「避免标题孤字掉行」的零依赖实现 | 文档 | frontend 用于中文标题断行（配合宋体系无负字距） | 低 | frontend-developer |
| 5 | 合规归档 | **中国证监会 2026-02-06 银发〔2026〕42 号**（虚拟货币相关业务风险边界） | [csrc.gov.cn](https://www.csrc.gov.cn/csrc/c100028/c7614318/content.shtml)（企划书附录已引） | 规则 8 的监管依据归档；对外文案合规红线的引用源 | 官方文件 | 无动作，仅供合规引用（延续「不做加密交易」红线） | 低 | 全体 |

### 第 4 篇｜性能与可访问性（2026-11-07）
- 观察：零构建栈本身轻量，真实性能风险在三个点：① 大目录扫描/备份是引擎长任务（Web UI 需任务化+进度，
  不能阻塞）；② 大 JSONL 渲染（CASE-12 教训：酒馆官方列表加载 >1 分钟，RRA 用「读尾部 100KB」解决）；
  ③ brief 八的可访问性要求（reduced-motion、键盘焦点、对比度）目前只有规范、没有固定检查项。
- **可落地建议（1 条）**：frontend 大列表采用「视口渲染 + 尾部优先」策略（借鉴 RRA tail-read 先例），
  qa 把「prefers-reduced-motion 与键盘焦点可见性」列入三轮审核第 2 轮固定检查项。受益 agent：
  frontend-developer（实现）、qa-reviewer（审计项）。

---

## 待办备注

- ✅ 已完成：ui-design-direction.md、claude-design-study.md 已对齐 frontend-redesign-brief.md（规则 10）。
- ✅ 已完成：st-launch-plan.md 已加「投放暂停横幅」（规则 13）。
- 下一批预告：ST 1.20 动向、Noto Serif SC vendoring 审批材料预写、中文社区新帖跟踪、
  与规则 11（注释全覆盖）配套的注释标准建议。
