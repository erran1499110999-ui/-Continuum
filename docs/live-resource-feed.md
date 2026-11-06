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

---

## 待办备注

- 修订队列：ui-design-direction.md、claude-design-study.md 需与 frontend-redesign-brief.md（规则 10：
  禁粒子/光斑、中文标题宋体系、玻璃阴影从简）对齐（我的写作用域，后续批次执行）。
- 批次 2 资源预告：风险主题资源（备份完整性验证技能、restic check 语义）、中文社区新帖跟踪、
  ST 1.20 动向等。
