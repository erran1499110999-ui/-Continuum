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

---

## 待跟踪清单（下一批优先）

- ST 1.20 动向与内置备份能力变化；Chub 加密币计费说法复核；Backyard 定价官网复核；
- 中文社区（贴吧/NGA）新一轮求助热点的题材变化（判断引擎 P0 检测项的市场窗口）；
- Discord/Reddit 凭据获批后的社区情绪抽样。
