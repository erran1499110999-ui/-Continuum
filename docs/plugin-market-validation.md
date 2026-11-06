# ST 插件市场验证报告（plugin-market-validation）

> 编制：researcher（Agent Teams，诗人/哲学家视角）｜ 日期：2026-11-07
> 依据：创始人指令（AGENTS.md 规则 12/13）——**投放已暂停**，本报告用可检验证据回答
> 异质性 / 原创性 / 先进性 / 市场竞争力四个问题，附「对项目的严厉质疑」与 go/no-go 结论。
> 证据全部标注来源；结论不得作为投放授权（投放须创始人另行确认）。
> 测试规模口径：以最新真实运行输出为准（AGENTS.md 基线 182 collected；lead 最新口径 364 例）。

---

## 1. 异质性：功能差异矩阵

> 比较对象：RP-Card-Vault、TavernAI 2、RecordRecoveryAssistant、st-saves、chat-exporter 类、
> nat20-bridge、社区脚本（SillyDroid 迁移脚本 / liya 卡工具 / docker tar 备份教程）。
> 「我们」= Continuity 插件（选项 1：内存态体检+唤起）+ 本地 Web UI/引擎（一体产品）。

| 能力 | RP-Card-Vault | TavernAI 2 | RecordRecoveryAssistant | st-saves | chat-exporter 类 | nat20-bridge | 社区脚本 | **我们** |
|---|---|---|---|---|---|---|---|---|
| 形态 | 独立应用（local-first） | 客户端（迁移向导） | ST server 插件 | ST server 插件+Git | 纯前端扩展 | 前端扩展+Python sidecar | 单文件脚本 | 前端扩展 + 本地 Web UI/引擎 |
| 角色卡管理 | ✅ 搜索/标签/编辑/备份 | ✅ 导入 | ❌ | 随 data 备份 | ❌ | ❌ | liya：✅ 生成/校验 | ⚠️ 体检级（同名卡/字段缺失），管理后续 |
| 聊天误删找回 | ❌ | ❌ | ✅ 核心 | ⚠️ 回滚到存档 | ❌ | ❌ | ❌ | ⚠️ 引擎恢复能力（尚未开放 UI），插件不直接做 |
| 备份 | ✅ 卡备份 | ⚠️ 导入即副本 | ⚠️ 只读 backups/ | ✅ 云备份（GitHub） | ❌ | ❌ | ✅ tar/zip 脚本 | ✅ 本地全量+manifest+SHA-256（引擎） |
| **诊断（体检）** | ❌ | ❌ | ❌（只找回） | ❌ | ❌ | ❌ | liya：卡校验（写卡视角） | ✅ **案例驱动 23 项事故场景 → 引擎全量 + 插件 6 项内存提示** |
| **修复分级（R0/R1/R2/R3 + diff）** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ **引擎独有（生态内未见同款）** |
| **迁移验证（往返保真）** | ❌ | ⚠️ 导入无验证报告 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ 迁移报告+字段级核对（提示词 7） |
| **可回滚（输出新目录）** | ⚠️ 备份可回 | ⚠️ | ⚠️ 另存新档（非覆盖；README 原文 Safe Restore，QA 核验） | ⚠️ 覆盖本地数据（自警告） | ❌ | ❌ | ⚠️ 手工 | ✅ 恢复新目录+哈希校验 |
| 本地优先闭环 | ✅ | ⚠️ 本地客户端 | ✅ | ❌（云） | ✅ | ✅ | ✅ | ✅ |
| 插件↔网页/引擎一体 | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ 架构先例（非一体产品） | ❌ | ✅ 品牌一体（选项 1 为跳转式，深度一体待选项 2） |
| 来源 | [RP-Card-Vault](https://www.toolcenter.ai/zh/tools/rp-card-vault) | [tavernai.net 迁移文档](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/) | [RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant) | [st-saves](https://github.com/breezewb/st-saves) | [HTML-Export](https://cocos-homes.com/writing/SillyTavern-HTML-Export)、[Dataset-Export](https://github.com/Cohee1207/SillyTavern-Dataset-Export) | [nat20-bridge](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md) | [SillyDroid 脚本](https://github.com/alipymanbu/Android/blob/master/%E5%AE%98%E7%BD%91%E7%89%88APP%E4%B8%8B%E8%BD%BD/SillyDroid/Termux%E6%95%B0%E6%8D%AE%E8%BF%81%E7%A7%BB%E4%B8%8E%E5%A4%87%E4%BB%BD.md)、[liya 工具](https://github.com/feverZHONG/liya-sillytavern-cards) | 本团队文档 |

**结论**：**截至 2026-11-07 抽检的 7 个已知竞品中，未发现同款组合**（盘点范围见本句名单；
未穷尽闭源/未收录工具——官方内容库全量盘点列入补充证据清单第 1 条）：诊断（事故案例驱动）+
修复分级 + 迁移验证 + 本地优先闭环 + 插件↔网页一体。注意：其中「可回滚」**不构成单项差异化**——
RecordRecoveryAssistant 的 Safe Restore 同样另存新档、绝不覆盖（QA 核验 README），上版据此的
差异化表述已被撤回。已被覆盖的单项：误删找回、云备份、聊天导出、卡管理、sidecar 架构、写卡校验——
**每项都有成熟免费替代**。

---

## 2. 原创性：诚实清单

### 2.1 真创新（相对生态，程度：弱—中，无一项是硬创新）

| 点 | 程度 | 说明与来源 |
|---|---|---|
| 体检项源自 **23 案例真实事故库**（H1–H6 逐条对应 CASE 编号，非凭空想象） | 中 | [failure-case-library.md](./failure-case-library.md)；生态内工具多为「作者自己遇到一个问题」驱动，少见系统化案例驱动的检测规则 |
| **薄壳 + token 零接触唤起**（token 由服务器 meta 注入首页，插件不接触、不存储） | 弱-中 | [st-plugin-plan.md](./st-plugin-plan.md) §6.3；属安全设计细节创新，非能力创新 |
| **防投毒静态契约体系**（Python 侧对 JS 源码 lint：禁 eval/innerHTML/外部 URL/密钥字样 + manifest schema 校验） | 中 | [st-plugin-plan.md](./st-plugin-plan.md) §5.2；把规则 3「不执行导入内容」变成可回归的测试，生态内未见同款做法 |
| 插件（提示）↔引擎/Web UI（深度）一体架构与同一品牌转化漏斗 | 弱-中 | [st-plugin-plan.md](./st-plugin-plan.md) §0.1；组合形态未见同款（nat20-bridge 只有桥、没有产品一体性） |

### 2.2 借鉴 / 已有轮子（逐项承认）

| 我们做的 | 借鉴自 | 承认程度 |
|---|---|---|
| 插件形态、manifest、getContext()、slash command | ST 官方模板与最佳实践（[Writing Extensions](https://docs.sillytavern.app/for-contributors/writing-extensions/)） | 完全照标准做，无原创 |
| 唤起本地服务（sidecar 思想） | nat20-bridge（2026-10 先例） | 架构上无原创 |
| 备份扫描/误删找回思路 | RecordRecoveryAssistant（tail-read、按 metadata 显示） | 我们的引擎实现更完整，但思路非原创 |
| 单项检查（integrity 缺失、同名卡、疑似重置） | 社区 issue 与手工排查帖早有做法 | 检测逻辑无原创，原创在「系统化+案例编号+测试」 |
| 修复规则（尾逗号等） | jsonrepair 等库规则集 + seriot 实证 | 规则本身非原创 |
| 设计语言 | Claude 设计系统（claude-design-study、open-claude-ui） | 完全借鉴 |

**诚实结论**：本产品的原创性不在「点子」，而在**组合、证据链与工程质量**；若竞品以同样投入复刻，
我们没有不可逾越的护城河。因此差异化必须持续靠「事故库更新速度 + 适配速度 + 信任积累」维持。

---

## 3. 先进性：技术层面优劣

### 3.1 相对社区工具（多为单文件脚本/轻插件）的优势

| 维度 | 我们 | 社区典型 | 证据 |
|---|---|---|---|
| 测试规模 | 数百例真实运行（基线 182 collected，最新口径 364） | 多数脚本零测试或几个用例 | AGENTS.md / lead 口径 |
| 质量流程 | 三轮严格审核（功能/安全攻击路径/回归发布） | 无 | TEAM-COORDINATION 创始人指令 1 |
| 代码注释 | 全注释覆盖（规则 6/11，含核心引擎） | 稀疏 | AGENTS.md 规则 11 |
| 语义安全 | 静态契约防投毒、textContent 渲染、禁外部 URL | 无系统保障 | st-plugin-plan §5.2 |
| 数据原则 | 只读、输出新目录、未知字段保留、默认不上传 | 部分工具覆盖式恢复（st-saves 自警告「会覆盖」） | AGENTS.md 规则 1/2/9 |

### 3.2 不足（诚实）

1. **真机未验**：插件 P2/P3 未完成，零真实 ST 环境运行记录（沙箱无浏览器）。
2. **无 AI 辅助功能**：定位使然，但「AI 帮我修卡」是社区常见诉求（NGA 帖里「丢给 AI 检查」），我们在生态话语里缺一角。
3. **未收录官方内容库**：审核等待期不可控（st-launch-plan §1）。
4. **安装摩擦高于单文件脚本**：需手动放扩展目录 + 需先运行本地 Web UI（双进程）；对比「curl 一条命令」的 SillyDroid 脚本体验更重。
5. **移动端断档**：插件在移动浏览器可跑，但引擎/Web UI 需桌面 Python——而社区大量重度用户在 Termux/安卓（案例库多起来自 Termux）。

---

## 4. 市场竞争力

| 维度 | 证据与判断 |
|---|---|
| 替代品强度 | **高**：免费、多款、覆盖各单项（找回/云备份/导出/迁移导入/卡管理）；全链组合（诊断+修复分级+迁移验证+本地优先闭环+插件↔网页一体）在抽检范围内未见替代（第 1 节矩阵，E2 措辞已降级）；单点「安全恢复/回滚」**并非差异化**（RecordRecoveryAssistant 亦为非覆盖式另存新档） |
| 用户切换成本 | **低**：生态内工具切换几乎零成本（都免费小工具）→ 我们留不住「浅层用户」，只能靠深度价值与信任留「重度用户」（企划书 2.3 的目标人群判断正确） |
| 分发可达性 | 官方收录=申请制+等待期（st-launch-plan §1）；GitHub Release 立即可达但自然流量低；社区渠道需凭据且受限（research-community §0）；**内容分发（教程/清单）是现实中的最短路径**（live-resource-feed 发散主题 1） |
| 免费替代挤压 | 备份/找回类付费意愿被免费替代压制（business-feed #6）→ 收费点只能压在免费工具做不了的：批量体检、修复预览、版本比较、迁移报告（企划书 4.3 分层再次被验证） |
| 定价空间 | 企划书 Pro 一次性 ¥39–99 / US$8–15 为测试假设；Chub 订阅变化（[aipartnerguides 评测](https://aipartnerguides.com/reviews/chub-ai/) 2026-09-24 快照：多档收敛为单一 $20/月；**第三方评测快照，官方页待复核**）是背景利好（business-feed #1），但**前提是用户先认可增量价值**，而非定价本身有空间 |

---

## 5. 对项目的严厉质疑（≥10 条，附证据与初步回答；答不上来的如实标注）

1. **用户凭什么装一个陌生扩展？** 信任成本是真实门槛；开源+双语 README+「零出站可审计」对开发者有说服力，对普通用户无效。→ 回答：只能靠内容先行（自查清单）与口碑；**待验证：真实装机意愿零证据**。
2. **体检提示会不会制造虚假安全感？** 六项内存检查≠全量健康；用户看到「体检完成」可能停止深查。→ 回答：面板必须明示覆盖范围与「内存态初步提示」话术（已设计，R4）；**待验证：用户是否真看话术**。
3. **我们的壁垒只是工程规范，随时可被复制？** 是。测试/审核/注释/案例库都可被复刻，时间差约 1–2 个月。→ 回答：护城河只能是持续更新速度+信任；不把工程规范当护城河。
4. **ST 官方自己修掉 P0 后，我们还剩什么价值？** 1.19 已修复多条 P0（business-feed #3）；存量旧版用户、跨版本迁移、独立验证、白屏抢救仍是价值，但**窗口在收窄是事实**。→ **待验证：存量旧版/多版本用户比例**。
5. **插件与网页版真的一体，还是两张皮？** 选项 1 现状 = 「新标签跳转」，无 API 联通——诚实说目前是「两张皮+同品牌」；一体性要等选项 2（面板内嵌 API）。→ 回答：接受此批评；投放话术不得宣称「无缝一体」。
6. **免费替代品简单组合是否≈我们？** 近似：找回+云备份+导出组合可覆盖日常；组合缺统一体验、修复分级与批量报告。→ 回答：差异化真实但「必须自己安装三个工具 vs 装一个」的便利价值未经验证；**待验证**。
7. **安装摩擦（手动放文件夹 + 先跑 Web UI）会劝退多数目标用户吗？** 中文社区用户连「复制 data 文件夹」都要一步步教（research-community NGA 案例）→ 大概率劝退浅层用户。→ **待验证：5 人装机实测通过率**。
8. **内存态启发式（同名卡/疑似重置）误报一次就失信，值吗？** R4 已列；误报成本高。→ 回答：阈值保守+免责话术+可关闭；**待验证：真实样本误报率**。
9. **测试数百例但真实用户数据为零——工程信心≠市场信心。** 是。授权样本至今为零（12 章门槛未动）。→ 回答：投放冻结正确；先补真实样本再说。
10. **双进程架构把移动端/Termux 用户排除在外？** 是（第 3.2-5）。→ **待验证：目标用户中移动端占比**（若高，需重新设计分布形态）。
11. **收费功能会不会被 ST 官方免费覆盖？** ST 已内置 Download Backup、自动备份、1.19 修复——官方持续补强是最大战略风险。→ 回答：收费点必须比官方快且深（修复预览/版本比较/批量报告是官方未做的）。
12. **「本地优先」是卖点，还是用户根本无所谓？** st-saves 的存在证明部分用户主动上云。→ 回答：隐私是加分项不是唯一卖点；定位文案不押单点（marketing-copy 已注意）。

---

## 6. 结论：conditional-go（条件通过）

- **继续开发**（沉没成本小、信息价值高），但**一切投放冻结**（Release/社区帖/收录申请全部停止，规则 13），直至以下条件满足并经创始人确认：
  1. **真机验证**：5–10 名真实 ST 用户完成「安装→启用→体检→唤起→slash」且 ≥5 人愿意一周内再次使用（复用率初值）；
  2. **授权样本 ≥3 个**入库（修复/体检项用真实脱敏样本跑通，替代纯合成样本的信心缺口）；
  3. **付费/预售信号 ≥2**（或创始人确认收缩为免费开源诊断器定位）；
  4. 移动端用户占比与「双进程容忍度」两项访谈数据回收（决定是否需重新设计分布形态）。
- **补强清单（条件期间并行）**：面板覆盖范围声明、误报阈值调优方案、官方收录申请材料预写（不提交）、
  案例内容页（教程/清单）双语稿、st-launch-plan.md 顶部加「投放暂停」横幅（需 lead 授权我修订）。
- **需创始人用户访谈验证的假设清单（优先序）**：① 装机意愿与双进程容忍度；② 体检信任边界（是否误读为全量健康）；③ 付费锚点测试（¥39 vs ¥99）；④ 移动端占比；⑤ 云备份偏好画像（st-saves 用户是否也愿意本地备份）；⑥ 官方内容库收录等待期对用户发现的真实影响。

## 7. 补充证据清单（QA 裁决退回后追加，2026-11-07）

> 维持 conditional-go 的必要证据路径；全部标注状态与负责人，未收集前不得作为结论引用。

| # | 证据 | 补哪条缺口 | 状态 / 负责人 |
|---|---|---|---|
| 1 | **官方内容库现存扩展全量盘点**（官方 org `topic:extension` 仓库列表 + 内容库清单；部分需登录或申请渠道） | E2/C2（生态未穷尽） | 待收集（researcher/lead；公开部分可先做，登录部分待凭据） |
| 2 | **四条件数据**：① 真机 5–10 人复用率（操作化：一周后仍在扩展列表启用且主动打开过面板）；② 授权样本 ≥3；③ 付费/预售信号 ≥2；④ 移动端占比与双进程容忍度访谈 | 投放放行门槛（§6） | 待收集（创始人/lead 主导；qa 复核口径） |
| 3 | **每 release 冒烟测试首次执行记录**（st-launch-plan T4 对应项，作为「兼容最新 release」声明的第一份实证） | 先进性/兼容性声明 | 待执行（developer 执行、qa 留档） |
| 4 | E1 修正记录：矩阵与结论中「可回滚=差异化」表述已撤回（本版已修） | QA 裁决退回项 | ✅ 已完成（见 §1） |

---

## 8. 来源

- 矩阵/原创性证据：[RP-Card-Vault](https://www.toolcenter.ai/zh/tools/rp-card-vault)、[TavernAI 2](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/)、[RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)、[st-saves](https://github.com/breezewb/st-saves)、[HTML-Export](https://cocos-homes.com/writing/SillyTavern-HTML-Export)、[Dataset-Export](https://github.com/Cohee1207/SillyTavern-Dataset-Export)、[nat20-bridge](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md)、[SillyDroid](https://github.com/alipymanbu/Android/blob/master/%E5%AE%98%E7%BD%91%E7%89%88APP%E4%B8%8B%E8%BD%BD/SillyDroid/Termux%E6%95%B0%E6%8D%AE%E8%BF%81%E7%A7%BB%E4%B8%8E%E5%A4%87%E4%BB%BD.md)、[liya](https://github.com/feverZHONG/liya-sillytavern-cards)
- 官方：[Writing Extensions](https://docs.sillytavern.app/for-contributors/writing-extensions/)、[ST 1.19.0](https://github.com/SillyTavern/SillyTavern/releases/latest)
- 项目内：[st-plugin-plan.md](./st-plugin-plan.md)、[failure-case-library.md](./failure-case-library.md)、[research-community.md](./research-community.md)、[business-feed.md](./business-feed.md)、[research-st-plugin.md](./research-st-plugin.md)、[st-launch-plan.md](./st-launch-plan.md)（投放已暂停）
