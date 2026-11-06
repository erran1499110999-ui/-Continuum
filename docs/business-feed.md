# 商业情报流（business-feed）

> 维护：researcher（Agent Teams，常驻资源与智慧中枢）｜ 建立：2026-11-07
> 格式：每批次追加；每条含 来源+日期 / 事实要点 / 对产品的启示。
> 规则：只记录可核验的公开信息；不虚构数据；价格类信息标注「快照，复核官方页」；
> 不含 NFT/代币/钱包/云上传建议（规则 8）。

---

## 批次 1（2026-11-07）

| # | 来源+日期 | 事实要点 | 对产品的启示 |
|---|---|---|---|
| 1 | [aipartnerguides Chub 评测](https://aipartnerguides.com/reviews/chub-ai/)（2026-09-24 观测） | Chub 订阅从 Mercury/Mars 多档（约 $5–20/月）收敛为**单一 $20/月档**；评测另称其计费仅加密币（待复核官方） | 托管推理订阅在涨价收敛——「订阅疲劳」给一次性买断的本地工具留出定价空间（企划书 4.3 的 Pro 一次性 ¥39–99 更显合理） |
| 2 | [App Store Backyard.ai 页面](https://apps.apple.com/us/app/backyard-ai/id6498968886)（2025-08 快照）+ [评测](https://www.promptquorum.com/zh/power-local-llm/backyard-ai-review-local-roleplay)（2026-09） | Backyard 本地免费 + 云订阅 $7–35/月（商店页另见 $12/$34.99）；云对话在服务器处理 | 竞品把收入压在云端推理——我们「完全本地、无订阅推理」是差异化卖点；但也要预期部分用户习惯订阅制 |
| 3 | [ST 1.19.0 发布说明](https://github.com/SillyTavern/SillyTavern/releases/latest)（2026-11-06 访问为 latest） | 官方修复聊天完整性静默覆盖、CJK 备份键冲突、分支 integrity 等（案例库 P0 多条被上游修复） | 短期新装用户的事故率下降 → 我们的价值重心从「防新事故」转向「存量数据抢救/独立验证/跨版本迁移」；引擎 P0 检测项仍保留（旧版本用户量巨大） |
| 4 | [TavernAI 2 迁移文档](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/) | TavernAI 2 官方提供从 ST/TAI v1 批量导入（卡/聊天/群聊/lorebook/预设/图片） | 竞品把「迁移」做成获客功能——我们的差异化应是**诊断+修复分级+可回滚**（迁移向导之外的能力），并在文案强调 |
| 5 | [Foreverse 整站搬家教程](https://foreverse.app/zh/docs/guide-roleplay/migrate-from-sillytavern)（2026-08-11）；[SillyDroid 迁移文档](https://github.com/alipymanbu/Android/blob/master/%E5%AE%98%E7%BD%91%E7%89%88APP%E4%B8%8B%E8%BD%BD/SillyDroid/Termux%E6%95%B0%E6%8D%AE%E8%BF%81%E7%A7%BB%E4%B8%8E%E5%A4%87%E4%BB%BD.md)（2026-09-28） | 移动端玩家把「整站迁移/一键备份」做成产品能力；Foreverse 明示备份不含密钥 | 迁移需求被持续验证；我们迁移向导的 UX 应对标其「数量预览+逐类核对」；密钥处理口径（默认不含密钥）与我们规则 2 一致，可作文案背书 |
| 6 | [RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)（2025-12）、[st-saves](https://github.com/breezewb/st-saves)（2025-07） | 社区免费救援工具持续存在（误删找回/云备份） | 免费替代品挤压「简单备份」付费意愿——收费点必须压在免费替代品做不了的：批量体检、修复预览、版本比较、迁移报告（企划书 4.3 分层正确） |
| 7 | [RP-Card-Vault 目录页](https://www.toolcenter.ai/zh/tools/rp-card-vault)（2026-10） | local-first 卡管理（搜索/标签/备份/发送到 ST 等）已上架工具目录 | 最接近的定位竞品仍在卡管理层面；我们「聊天记录+世界书+配置」全量连续性是区隔，后续批次跟踪其功能动态 |
| 8 | [nat20-bridge](https://github.com/tapestria/nat20/blob/e187c813bb4e43c4e4e62942ecd83831f1cdbcaa/packages/nat20-bridge/README.md)（2026-10） | 社区出现「ST 扩展 + 本地 Python sidecar」开源先例 | 验证我们的插件架构路线可被社区接受；可关注其后续生态作为选项 2 参考 |

## 批次 2（2026-11-07）

| # | 来源+日期 | 事实要点 | 对产品的启示 |
|---|---|---|---|
| 1 | [QA 裁决书 validation-verdict.md](./validation-verdict.md)（2026-11-07 02:05） | 审判官抽检 3 个竞品来源：RecordRecoveryAssistant 实为「Safe Restore：另存新档、绝不覆盖」（非覆盖式）；st-saves「会覆盖本地数据」逐字准确；nat20-bridge 先例成立 | 竞品能力盘点必须逐条核对原文，我方「安全恢复」卖点与 RRA 重叠——差异化重心进一步压向「诊断+修复分级+迁移验证」而非恢复方式 |
| 2 | [ST 1.19.0](https://github.com/SillyTavern/SillyTavern/releases/latest)（2026-11-06 访问） | 官方合并 #5458/#5944/#5980：首行损坏不再静默覆盖、CJK 备份键独立、覆盖前落快照 | 「防新事故」价值窗口收窄（承接批次 1 #3）；引擎告警话术应按用户 ST 版本区分，避免对新版用户过度恐吓（live-resource-feed 批次 2 #4 已列行动） |
| 3 | [zer0thgear/character-card-editor](https://relatedrepos.com/gh/zer0thgear/character-card-editor)（2024-09） | 独立 V2/V3 规范卡编辑器（社区小工具生态活跃信号） | 卡编辑需求有工具覆盖——我们不与编辑器争市场，「体检+迁移」定位正确；可跟踪其 V3/CHARX 支持进度作为格式生态晴雨表 |
| 4 | [research-community.md](./research-community.md) NGA 白屏抢救帖（2025） | 中文社区「界面打不开也要救数据」需求持续存在（社区手工教复制 data 文件夹） | 「无界面抢救」内容页选题（升级前自查清单/白屏抢救手册）的市场窗口仍在；投放冻结期间可先完成内容创作备稿 |
| 5 | [business-feed 批次 1 待跟踪项](./business-feed.md) 复核 | Chub 加密币计费说法仍无官方页佐证（仅第三方评测），保持「待复核」不采信 | 竞品定价情报一律按「快照+待复核」口径引用，避免以讹传讹（与 QA 裁决 E3 同源教训） |
| 6 | 市场机会观察（本批次推断，标注为推断） | 「多版本并存用户的迁移往返保真验证」仍无工具覆盖（ST 官方导入无验证报告、TavernAI 2 无字段级核对） | 迁移验证（提示词 7）仍是抽检范围内未发现的组合要素之一；可作为首个「内容页+产品」联合选题 |

---

## 待跟踪清单（下一批优先）

- ST 1.20 动向与内置备份能力变化；Chub 加密币计费说法复核；Backyard 定价官网复核；
- 中文社区（贴吧/NGA）新一轮求助热点的题材变化（判断引擎 P0 检测项的市场窗口）；
- Discord/Reddit 凭据获批后的社区情绪抽样。
