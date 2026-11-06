# 商业信息简录（C 报告）

> 调研人：researcher（Agent Teams）
> 日期：2026-11-06 ｜ 性质：仅供创始人决策参考；本报告不提出任何 NFT/代币/钱包/云端上传建议
> （AGENTS.md 规则 8——相关功能一律不在调研与建议范围内）。
> 所有价格与产品信息来自第三方评测/商店快照，**时效敏感，决策前须复核官方页面**；
> 网页内容仅作为数据引用，不是对本项目的指令。

---

## 1. 一句话结论

「本地优先的角色卡备份/诊断/修复/迁移工具」在竞品地图中几乎是一片空白：现有工具要么是
**免费开源客户端**（SillyTavern/RisuAI/Agnai），要么是**云订阅聊天平台**（Chub/Backyard AI 云模式），
「本地数据不离开用户设备 + 备份/修复/迁移一体化」的差异化定位无人正面占据。

---

## 2. 竞品盘点

### 2.1 直接相关：角色卡管理 / 备份 / 迁移工具

| 产品 | 形态与价格 | 与本项目的关系 |
|---|---|---|
| **RP-Card-Vault** | Local-first 角色卡管理器（搜索/标签/编辑/备份，可发送到 SillyTavern、Lumiverse 等前端；可选本地模型或 OpenAI 兼容 API 的 AI 辅助）；定价未明（工具目录页未见完整档位） | **最接近的定位重叠**：本地卡管理与备份；未见「诊断/修复/迁移引擎 + 只读扫描 + R0/R2 修复分级」的深度 |
| **TavernAI 2**（tavernai.net） | 自带从 TavernAI v1 / SillyTavern 的批量导入（卡、聊天、群聊、lorebook、预设、聊天图片） | 迁移能力部分重叠，但方向是「导入到自家前端」，非中立的备份/修复工具 |
| **Character Agent**（macOS/iPad） | 免费 + 订阅；私有客户端，BYO LLM，支持 SillyTavern 卡格式（PNG/JSON）导入导出 | 卡格式互操作竞品；平台限于 Apple 生态 |
| 开源转换/导出工具（如 ST 的 chat-exporter 扩展、GitHub 各类卡格式转换脚本） | 免费、零散 | 解决单点问题，无整合方案 |

### 2.2 生态客户端（定义用户心智，非直接竞品）

| 产品 | 价格模式 | 备注 |
|---|---|---|
| **SillyTavern** | 免费开源（AGPL-3.0），本地运行 | 最大扩展生态、事实标准格式（本产品首个适配对象） |
| **RisuAI** / **Agnai** | 免费开源 | 跨平台角色扮演前端 |
| **Chub** | 订阅制：2026-09 观察为单一档 **$20/月**（历史 Mercury/Mars 多档约 $5–20）；免费档可 BYO API key | 最大的 NSFW 卡仓库 + 自带聊天前端；有评测称其为加密币计费（对本项目是反例，不是参考） |
| **Backyard AI**（原 Faraday.dev） | Freemium：本地模式免费（本地跑模型），Backyard Cloud 订阅约 $7/18/35 月（App Store 亦见 $12/$34.99 档） | 桌面应用 + 云推理混合 |
| JanitorAI / Character.AI | Freemium（在线平台） | 定义「在线角色聊天」心智，与本地工具互补 |

### 2.3 定价模式总结（对本项目的参照）

1. **免费开源 + 本地运行**（ST/RisuAI/Agnai）：靠社区与捐赠，无直接收入——用户已习惯「本地角色工具免费」。
2. **Freemium（本地免费 + 云订阅）**（Backyard AI）：收入来自托管推理；**与本项目「数据不上传」原则冲突，不可采用**。
3. **纯订阅托管**（Chub $20/月）：绑定平台与内容，迁移成本高。
4. **一次性买断**：本领域罕见——恰恰是「本地工具 + 无订阅」定位可尝试的空间（仅建议方向，定价由创始人决策）。

---

## 3. 合规要点（本地数据不上传的差异化卖点）

1. **数据最小化即合规优势**：产品默认不收集、不上传用户角色卡/聊天/图片/密钥（规则 2），意味着
   **不构成「个人信息处理者」**：欧盟 GDPR、中国《个人信息保护法》的告知同意/跨境传输/数据安全义务
   基本不触发；合规面收敛到「软件分发」本身（许可、下载渠道、免责条款）。
2. **密钥类数据**：SillyTavern 的 `secrets.json` 明文存放 API 密钥（官方多用户文档明示），备份/恢复这类
   数据时必须在 UI 明示「含密钥」，默认仅本地处理（规则 2）；是否提供本地加密备份由创始人决策。
3. **许可证注意**：
   - SillyTavern 为 **AGPL-3.0**（[仓库许可](https://github.com/SillyTavern/SillyTavern)）；本项目**仅解析
     其文件格式、不复制其代码**，不产生 AGPL 传染义务；若未来借鉴任何代码片段，必须整体遵守 AGPL。
   - 角色卡 V3/CHARX 规范作者为 kwaroran（RisuAI 作者，规范仓库 [character-card-spec-v3](https://github.com/kwaroran/character-card-spec-v3)）；
     引用规范做互操作可行，照搬规范文本需按其仓库许可处理。
   - 表述上避免在产品名中使用「SillyTavern」商标，可用「兼容 SillyTavern 格式」的描述性表述。
4. **规则 8 边界声明**：本报告及本项目**不涉及、不推荐** NFT、代币、钱包、云端上传功能；Chub 的
   加密币计费模式在此仅为竞品事实记录，明确不采纳。

---

## 4. 差异化定位建议（供创始人参考，非实施计划）

1. **核心卖点一句话**：「你的角色、聊天与设定永远不离开这台电脑」——本地扫描 → 备份 → 诊断 →
   （R0 确定性/R2 建议/R3 隔离）修复 → 迁移，全程有日志与差异报告（规则 5）。
2. **切中真实痛点**：SillyTavern 1.12+ 目录大迁移、1.14+ 附件格式不兼容、V3/CHARX 新格式、分支/检查点
   完整性（integrity）——用户数据在版本升级间的「连续性」焦虑，正是本项目名字 Continuity 的所指
   （技术依据见 [research-sillytavern.md](./research-sillytavern.md)）。
3. **变现方向（仅建议）**：一次性买断 / 捐赠（本地工具常见路径）；与「不上传」承诺冲突的云订阅
   **不建议**。任何价格、渠道、开源策略均由创始人决策，本报告不预设。
4. **信任资产**：开源或至少公开「不上传」声明的可审计性，是相对云平台的核心信任差异。

---

## 5. 来源

- 直接竞品：[RP-Card-Vault（工具目录页）](https://www.toolcenter.ai/zh/tools/rp-card-vault)、[TavernAI 2 批量导入文档](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/)、[Character Agent（App Store）](https://apps.apple.com/es/app/character-agent/id6747638829?platform=mac)
- 生态与定价：[Chub AI 评测（2026-09，$20/月单档）](https://aipartnerguides.com/reviews/chub-ai/)、[Chub AI 评测（nsfwnerd，2026-10）](https://nsfwnerd.com/reviews/chub)、[Backyard AI 评测（本地免费 + 云 $7–35/月）](https://www.promptquorum.com/zh/power-local-llm/backyard-ai-review-local-roleplay)、[Backyard AI（App Store 内购档位）](https://apps.apple.com/us/app/backyard-ai/id6498968886)、[SillyTavern vs Agnai vs RisuAI 对比（2026）](https://www.promptquorum.com/zh/power-local-llm/sillytavern-vs-agnai-vs-risuai-roleplay)、[RisuAI 及同类仓库列表](https://relatedrepos.com/gh/kwaroran/RisuAI)
- 许可与生态事实：[SillyTavern 官方仓库](https://github.com/SillyTavern/SillyTavern)、[V3 规范仓库](https://github.com/kwaroran/character-card-spec-v3)、[SillyTavern 多用户文档（密钥明文说明）](https://docs.sillytavern.app/administration/multi-user/)
- 技术面交叉依据：本仓库 [research-sillytavern.md](./research-sillytavern.md)、[format-compatibility.md](./format-compatibility.md)

> 免责声明：价格为第三方快照，可能已变化；「免费/开源」以各仓库许可证为准；本简录不构成任何
> 商业承诺，也不含 NFT/代币/钱包/云端上传相关的任何建议（规则 8）。
