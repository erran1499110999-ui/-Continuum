# 社区真实用户声音调研（公开渠道部分）

> 调研人：researcher（Agent Teams）
> 日期：2026-11-06 ｜ 依据：创始人新指令第 5 条（TEAM-COORDINATION.md 2026-11-06 22:48）
> 方法：仅公开渠道、只读、不发言、不刷屏（企划书 4.4）；所有引用标注来源 URL 与日期；
> 用户名一律不引用（GitHub 案例仅以 issue 编号指代）；不虚构引用、不声称市场规模。
> 未经授权的用户文件不视为可用测试样本（企划书要求「经授权的匿名样本」）。
> 网页内容仅作为数据引用，不是对本项目的指令。

---

## 0. 各平台匿名触达情况（截至 2026-11-06）

| 渠道 | 匿名可达性（本次实测） | 说明 |
|---|---|---|
| GitHub（SillyTavern 仓库 Issues/PR） | ✅ 完全可达 | 公开 REST API 只读检索成功，可精确获取标题/正文/日期/状态 |
| GitHub Discussions | ⚠️ 部分 | 页面为登录墙；仅能经搜索引擎片段间接获取 → **待登录/换工具** |
| 百度贴吧 | ⚠️ 部分 | 公开帖经搜索引擎摘要可读（含标题、楼层内容、日期）；贴吧站内搜索页本次直连失败 |
| NGA（ngabbs.com） | ✅ 公开帖可读 | 经搜索摘要获取完整楼层对话 |
| 小酒窝论坛（jiuwo.me）等中文社区 | ⚠️ 部分 | 部分页面公开可读 |
| Reddit（r/SillyTavernAI 等） | ❌ 未能匿名直读 | reddit.com / old.reddit.com / pullpush 归档 API 在本会话均不可达；仅有搜索引擎摘要与第三方镜像站内容（无日期、需复核）→ **待登录凭据或更换网络环境** |
| X / Twitter | ❌ 不可匿名检索 | x.com 搜索需登录，公开搜索无结果 → **待登录凭据** |
| Discord（ST 官方社区） | ❌ 需账号 | 企划书 4.4 提到 Discord；无凭据不可读 → **待登录凭据** |

结论：本轮可扎实覆盖 **GitHub + 中文社区（贴吧/NGA/小酒窝）**；Reddit、X、Discord 的深度调研需创始人提供登录凭据（仅存环境变量、只读使用）后方可继续。

---

## 1. GitHub 官方仓库：数据丢失 / 备份 / 损坏类真实报告

> 全部来自 SillyTavern 官方仓库公开 Issues/PR（api.github.com 检索，访问日 2026-11-06）。
> 引用格式：编号（创建日期，状态）。

### 1.1 聊天数据被静默覆盖 / 串档（数据丢失类，最重）

- **[#6032](https://github.com/SillyTavern/SillyTavern/issues/6032)**（2026-09-13，open）：同一角色的多个聊天之间切换时发生「跨聊天 integrity 错配」，多次导致**已有内容的聊天被重置为「header + 新生成的开场白」**（整段历史只剩 2 行记录）。用户保留了现场视频与被覆盖的 JSONL。原文摘录：*"In several earlier occurrences, a populated chat was ultimately replaced with only its metadata/header and a newly instantiated character greeting."*
- **[#5454](https://github.com/SillyTavern/SillyTavern/issues/5454)**（2026-04-14）：v1.16.0 在 integrity 不匹配时**无确认弹窗直接重置聊天文件**；旧版本有确认对话框。日志：*"File does not have integrity metadata matching …"*。
- **[#5864](https://github.com/SillyTavern/SillyTavern/issues/5864)**（2026 年，open，在 #6032 中被引用）：整聊「陈旧写入」（whole-chat stale writes），讨论 integrity UUID 只保身份、不保版本内容的局限。
- **PR [#5458](https://github.com/SillyTavern/SillyTavern/pull/5458)**（2026-04-15，closed）：修复「首行不可解析（损坏、Termux BOM、截断）时静默覆盖聊天文件」——官方确认此路径曾造成**静默数据丢失**。
- **PR [#5980](https://github.com/SillyTavern/SillyTavern/pull/5980)**（2026-08-24）：修复「用户确认 OVERWRITE 后旧版本永远消失」——此前确认覆盖前不落快照，用户确认后**永久失去旧文件**。

### 1.2 自动备份缺口 / 备份机制缺陷

- **[#5796](https://github.com/SillyTavern/SillyTavern/issues/5796)**（2026-06-25，open）：v1.18.0 聊天自动备份出现**数周级时间空洞**（5 月底至 6 月初完全没有备份文件），误删后无备份可恢复。原文：*"Losing months of creative writing due to this backup fracture has been deeply upsetting."*
- **[#5797](https://github.com/SillyTavern/SillyTavern/issues/5797)**（2026-06-25，open，Feature Request）：清理聊天时误删「最珍贵的聊天记录」，删除弹窗**不显示被删文件信息**；请求删除对话框加文件元数据 + 双重确认。原文：*"I'm heartbroken."* 同时指出内置备份未能找回。
- **[#5780](https://github.com/SillyTavern/SillyTavern/issues/5780)**（2026-06-17，Confirmed，2026-09-14 关闭）：**中文角色名**在备份文件名中被全部替换为下划线（雷电将军 → `chat______`），所有中文名角色**共享同一个备份配额**，活跃聊天会把安静聊天的备份挤掉（即静默丢备份）。
- **[#4936](https://github.com/SillyTavern/SillyTavern/issues/4936)**（2025-12-31，open）：中文聊天名备份报 ENOENT + 手机端备份列表加载 >1 分钟；报告者为此自研了救援插件（见 1.3）。
- **[#3895](https://github.com/SillyTavern/SillyTavern/issues/3895)**（2025-04-20）：从备份导入的聊天**无法正常续聊**——导入后 prompt 只含聊天开头；导出→删除→再导入的往返**不保真**。
- **PR [#5944](https://github.com/SillyTavern/SillyTavern/pull/5944)**（2026-08-18）：官方修复非 ASCII 聊天名备份键冲突，PR 自述「busy chats silently evict the backups of quiet ones, which is backup data loss」。

### 1.3 用户自造「救援工具」——痛点强度的旁证

- **[SenriYuki/RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)**（2025-12-18）：「SillyTavern 之对话纪录海底捞，寻回误删的对话纪录」后端插件，解决「意外删对话、换预设导致纪录消失、想找回某时间点暂存档」。
- **[breezewb/st-saves（Cloud Saves）](https://github.com/breezewb/st-saves)**（2025-07-31）：把 `/data` 目录备份到私有 GitHub 仓库的插件，README 原话问句即痛点：*"你是否曾经担心过不小心丢失精心培养的 SillyTavern 角色卡、珍贵的聊天记录或者辛苦配置的世界信息？"*

### 1.4 角色卡损坏 / 导入失败 / 卡片串档

- **[#5756](https://github.com/SillyTavern/SillyTavern/issues/5756)**（2026-06-09）：v1.18.0 导入**同名角色卡**时随机覆盖已有卡（仅封面留存），用户持 8000+ 张卡、每次批量导入后都能发现卡内容被替换。原文：*"This causes the old card to be completely lost (only the cover image remains)."*
- **[#3667](https://github.com/SillyTavern/SillyTavern/issues/3667)**（2025-03-12，closed）：聊天过程中角色 A 的定义被角色 B 覆盖，A 的全部聊天记录挂到 B 名下；用户上传了现场 jsonl。
- **[#3560](https://github.com/SillyTavern/SillyTavern/issues/3560)**（2025-02-25，open）：报错 *"Could not import character. The file is likely invalid or corrupted."*，连默认角色 Seraphina 也导入失败，用户无诊断手段。
- **PR [#3361](https://github.com/SillyTavern/SillyTavern/pull/3361)**（2025-01-26）：官方确认「导入图片损坏时使用默认头像」——损坏头像导入是常见路径。
- **[#4166](https://github.com/SillyTavern/SillyTavern/issues/4166)**（2025-06-15，closed 2025-12）：清理连接配置时**settings.json 损坏**，webapp 白屏转圈，无任何容错。

---

## 2. 中文社区（贴吧 / NGA / 小酒窝论坛）：导入、迁移、降级痛点

- **[NGA：酒馆导入不了人物卡](https://ngabbs.com/read.php?tid=46880846&rand=628)**（2026-05-29）：新手从类脑社区「右键保存图片」得到的是**没有角色数据的图**或损坏文件，多人跟帖复现同样错误；共识是需要「新窗口打开原图再另存」。典型原话：*"json格式损坏。你确认一下保存的文件是不是png格式……"*、*"我也是研究了好一会才明白怎么把那个图片给下载下来。"*
- **[NGA：酒馆无法导入角色卡](https://ngabbs.com/read.php?tid=46837169&page=e&_fp=13&rand=80)**（2026-05）：*"导入角色卡的时候无论是png还是js格式都说文件损坏"*；热心回复给出「发给 AI 检查 JSON」「新建卡自测导入」等手工诊断法——**没有现成的本地诊断工具**。
- **[NGA：本地部署酒馆无法导入角色卡](https://ngabbs.com/read.php?tid=44940658&topid=837719626&page=1&rand=911)**（2025-08-27）：Discord CDN 拉取超时导致链接导入失败、本地导入报 *"The file is likely invalid or corrupted"*；改代理、换版本、管理员运行均被列为排查项。
- **[NGA：怎么在没开酒馆界面的情况下把角色卡跟聊天纪录拿出来？](https://ngabbs.com/read.php?tid=43673259&rand=368)**（2025）：酒馆「不明原因声称缺少档案」、界面白屏，用户想**不通过界面抢救数据**；社区一步步教「复制 data 文件夹→先开一次新酒馆再粘贴→data/default-user/character 手动批量导入」；最后结论：*"理论上所有用户数据都在data文件夹里面，里面没东西就是没了。"* ——数据抢救完全依赖手工 + 社区经验。
- **[小酒窝论坛回复（2026-03-27）](https://jiuwo.me/u/polaris/activity/replies)**：*"版本回退并非无损操作！新版本的配置文件（config.yaml）和聊天记录可能与旧版本不兼容。直接降级可能导致数据不兼容，出现酒馆白屏打不开等问题。回退之前一定要先备份，先备份，先备份"*——社区自发的降级风险警告。
- **[百度贴吧 p/9111790336](https://tieba.baidu.com/p/9111790336)**（2025-07-10 前后）：部署脚本作者特意把脚本拆分「这样会更方便对酒馆内容进行备份、导出（角色卡、聊天记录、预设、背景图等）」并在评论区贴备份导出方法——备份需求要靠散落教程满足。
- **[百度贴吧 p/8715454843](https://tieba.baidu.com/p/8715454843)**（2025）：世界书（lorebook）导入与生效问题反复求助（"世界书不生效怎么办啊？"），云端版与本地版界面不一致加剧困惑。
- **[百度贴吧 deepseek吧 p/9740390586](https://tieba.baidu.com/p/9740390586##1)**（2026）：用户为「在官方 App 玩酒馆角色卡」自研读卡预设 + 知识库方案，提到酒馆靠「世界观和正则」解决记忆丢失、角色人设漂移——**配置复杂度是真实的门槛**。
- **[GitCode 教程：SillyTavern 数据迁移（<1.12.0 → ≥1.20.0）](https://blog.gitcode.com/721d95268eb69baa62808cc295a5ceac.html)**（2026-02-03）：第三方教程列出必须备份的文件/目录清单并警告 *"不要复制整个public文件夹！"*——官方迁移指南之外还需要民间教程，说明**迁移知识没有被官方充分覆盖**。

---

## 3. Reddit（r/SillyTavernAI 等）：间接材料与触达限制

> 本会话内 reddit.com / old.reddit.com / pullpush 归档 API 均无法匿名直读；
> 以下内容来自搜索引擎收录的第三方镜像页 [ski52nn.ru 镜像](http://ski52nn.ru/x10zu/silly-tavern-import-characters-reddit.html)（无日期、非官方，原始帖子与用户名未能核对，**列为「待复核」**，不得作为确定证据引用）。

镜像页可见的重复主题（与 GitHub/中文社区高度一致）：
- 「朋友换了新手机，不想手动搬角色卡和聊天文件，有没有办法做一个备份直接传给新手机」——**跨设备整包迁移需求**；
- 「导入 JSON 后只剩 2 个默认角色（Darkness 和 Megumin）怎么办」——导入失败后无诊断路径；
- 「这个更新太仓促，我所有角色都不兼容 oobabooga 了」——客户端/后端联动升级引发的兼容断裂；
- 「Risu 有点 bug，会删掉我的角色和聊天记录」——竞品可靠性口碑问题；
- 「Discord 最近几周移除了 PNG 元数据功能，所有新旧上传的 PNG 都被剥掉了角色数据」——分发渠道静默破坏角色卡元数据的案例；
- ST 更新日志片段：「Added import of V3 cards characters (PNG, JSON, CHARX)」——V3/CHARX 已进入官方导入面（与 [research-sillytavern.md](./research-sillytavern.md) 一致）。

**待登录后可做**：r/SillyTavernAI、r/CharacterAI_NSFW 等子版按关键词（data loss / backup / corrupted / migration）检索 1 年内帖子并核对原文与日期。

---

## 4. X / Twitter、Discord

- X：x.com 公开搜索页需登录；本次搜索引擎未返回任何可核对的公开帖 → **内容与日期均不可得，不引用、不猜测**。
- Discord（ST 官方社区等）：需账号登录；企划书 4.4 将其列为早期增长渠道之一，**待创始人提供凭据后**再做只读调研（服务器公告、求助频道关键词检索）。

---

## 5. 竞品口碑与迁移工具生态（公开渠道）

- **RisuAI**（kwaroran/RisuAI 仓库公开 Issues）：
  - [#1519](https://github.com/kwaroran/RisuAI/issues/1519)（2026-07-27）：重掷/swipe 的多个变体在继续聊天或删除后续消息后丢失，无法恢复；
  - [#1018](https://github.com/kwaroran/RisuAI/issues/1018)（2025-08-17）：降级版本后自动保存失效，重启即丢修改。
  → 竞品同样存在「静默不保存」类可靠性口碑问题；用户对数据可靠性的焦虑是跨客户端的。
- **TavernAI 2（tavernai.net）**：官方文档提供从 TAI v1 / SillyTavern 的批量导入（卡、聊天、群聊、lorebook、预设、聊天图片）——[迁移文档](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/)。「迁移到自家前端」是竞品的获客手段，也印证了跨端迁移需求真实存在。
- **Foreverse（手机端）**：官方教程 [从 SillyTavern 整站搬家](https://foreverse.app/zh/docs/guide-roleplay/migrate-from-sillytavern)（2026-08-11）提供「整包备份导入」，并明确 *"密钥不随包走要重填"*；另有 [角色卡导入失败模式博客](https://foreverse.app/blog/import-character-cards-android)（2026-07-18）归纳三种最常见的「卡导不进来」失败模式。→ **「导入/迁移失败」已成为竞品做内容获客的主题**。
- **OrbWeaver**：[Coming from SillyTavern wiki](https://github-wiki-see.page/m/Inktomi93/OrbWeaver/wiki/Coming-from-SillyTavern)（2026-10-10）支持整站导入 ST 数据，并指出 *"a SillyTavern persona has no file of its own"*（Persona 无独立文件，散在 settings 内）——与我们的技术调研一致。
- **SillyDroid（Android 官方壳）**：[Termux 数据迁移与备份文档](https://github.com/alipymanbu/Android/blob/master/%E5%AE%98%E7%BD%91%E7%89%88APP%E4%B8%8B%E8%BD%BD/SillyDroid/Termux%E6%95%B0%E6%8D%AE%E8%BF%81%E4%B8%8E%E5%A4%87%E4%BB%BD.md)（2026-09-28）：「一条命令就能把整套数据搬进 SillyDroid」「换机不丢卡」——迁移被做成 Android 端的产品能力，说明需求强到值得单独做文档。

**付费意愿信号（公开渠道）**：未见用户为「备份/迁移工具」付费的直接公开证据；生态内可见的付费集中在**云端推理订阅**（Chub $20/月、Backyard AI $7–35/月，见 [research-business.md](./research-business.md)）。社区自发开发/使用免费救援插件（Cloud Saves、Record Recovery Assistant）说明**需求强但当前免费替代存在**——定价验证只能靠第 12 章的访谈/预售测试，不能由本调研推断。

---

## 6. 痛点主题聚类（基于以上公开证据）

| 聚类 | 典型证据 | 频率信号 |
|---|---|---|
| A. 备份机制不可靠（静默缺口/配额冲突/中文名碰撞） | #5796、#5780、#4936、#5944、#3895 | **高**（多起独立报告 + 官方确认修复） |
| B. 聊天被静默覆盖/串档（integrity 体系边界） | #6032、#5454、#5458、#5980、#5864、#3667 | **高**（跨版本持续出现） |
| C. 误删无救（UI 不显示被删对象、备份找不回） | #5797、#5796、RecordRecoveryAssistant、st-saves | **高**（情感强度最高："heartbroken"） |
| D. 升级/降级/迁移断裂（1.12 布局、版本回退白屏） | 1.12 迁移指南、小酒窝回退警告、GitCode 教程、NGA 白屏求救 | **高**（中英文社区均有独立表达） |
| E. 角色卡导入失败且无诊断手段（下错图/元数据被剥/损坏无提示） | NGA×3、#3560、#3361、Local Waifu/Foreverse 博客 | **高**（新手重灾区） |
| F. 配置复杂度（世界书/预设/正则） | 贴吧 p/8715454843、deepseek吧 p/9740390586 | 中（学习门槛而非数据事故） |
| G. 跨设备整包备份/换机迁移 | Reddit 镜像、SillyDroid、Foreverse | 中-高 |

---

## 7. 对企划书第 12 章验证门槛的对照（初步证据，非结论）

> 门槛（12.3）：≥5/10 人讲真实迁移/损坏/恢复问题；≥3 人愿提供脱敏样本；≥3 人愿试用；≥2 人愿付费/预售。

| 门槛 | 公开渠道初步证据 | 判定 |
|---|---|---|
| 5/10 真实问题 | 已收集 **15+ 起独立公开案例**（GitHub 11 起 + 中文社区 4 起以上），覆盖全部 7 个痛点聚类；其中多起被官方确认 | **初步证据强**，但「5/10」是访谈口径，必须由创始人访谈复证 |
| 3 人愿提供脱敏样本 | 多位 issue 作者公开贴出 jsonl/视频/截图，但**未授权本项目使用**；企划书要求「经授权」 | **待授权**（可向 issue 作者征询，或等访谈样本） |
| 3 人愿试用 | 公开渠道无法观察意向 | **待访谈** |
| 2 个付费信号 | 公开渠道未见为备份/迁移付费的直接证据；免费替代品存在 | **无证据，待访谈/预售测试** |

对第 8 章指标的提醒：下载量/点赞不构成验证（企划书原文如此），本报告同样不以此类数据作证。

---

## 8. 需要登录凭据才能深入的内容

1. **Reddit**：r/SillyTavernAI 等子版关键词检索（近 1 年 data loss / backup / corrupted / migration），核对镜像页内容与日期；可参与观察但**不发言**。
2. **X/Twitter**：搜索「SillyTavern + 数据丢失/备份」的公开讨论与创作者抱怨；x.com 搜索需登录。
3. **Discord（ST 官方社区）**：求助频道、公告与插件讨论；企划书 4.4 的早期增长渠道。
4. **GitHub Discussions**：官方讨论区的备份/迁移主题（当前登录墙）。
5. 说明：凭据由创始人提供并仅存环境变量、只读使用（TEAM-COORDINATION.md 新指令第 5 条）；本会话不自行注册任何账号。

---

## 9. 主要来源（URL + 日期）

**GitHub（SillyTavern 官方仓库，检索日 2026-11-06）**
- [#6032](https://github.com/SillyTavern/SillyTavern/issues/6032)（2026-09-13）｜[#5797](https://github.com/SillyTavern/SillyTavern/issues/5797)（2026-06-25）｜[#5796](https://github.com/SillyTavern/SillyTavern/issues/5796)（2026-06-25）｜[#5780](https://github.com/SillyTavern/SillyTavern/issues/5780)（2026-06-17）｜[#5756](https://github.com/SillyTavern/SillyTavern/issues/5756)（2026-06-09）｜[#5454](https://github.com/SillyTavern/SillyTavern/issues/5454)（2026-04-14）｜[#4936](https://github.com/SillyTavern/SillyTavern/issues/4936)（2025-12-31）｜[#4166](https://github.com/SillyTavern/SillyTavern/issues/4166)（2025-06-15）｜[#3895](https://github.com/SillyTavern/SillyTavern/issues/3895)（2025-04-20）｜[#3667](https://github.com/SillyTavern/SillyTavern/issues/3667)（2025-03-12）｜[#3560](https://github.com/SillyTavern/SillyTavern/issues/3560)（2025-02-25）
- PR：[#5944](https://github.com/SillyTavern/SillyTavern/pull/5944)（2026-08-18）｜[#5980](https://github.com/SillyTavern/SillyTavern/pull/5980)（2026-08-24）｜[#5458](https://github.com/SillyTavern/SillyTavern/pull/5458)（2026-04-15）｜[#3361](https://github.com/SillyTavern/SillyTavern/pull/3361)（2025-01-26）
- 救援工具：[RecordRecoveryAssistant](https://github.com/SenriYuki/RecordRecoveryAssistant)（2025-12-18）｜[st-saves Cloud Saves](https://github.com/breezewb/st-saves)（2025-07-31）

**中文社区**
- NGA：[导入不了人物卡](https://ngabbs.com/read.php?tid=46880846&rand=628)（2026-05-29）｜[无法导入角色卡](https://ngabbs.com/read.php?tid=46837169&page=e&_fp=13&rand=80)（2026-05）｜[本地部署无法导入](https://ngabbs.com/read.php?tid=44940658&topid=837719626&page=1&rand=911)（2025-08-27）｜[无界面抢救数据](https://ngabbs.com/read.php?tid=43673259&rand=368)（2025）
- 贴吧：[p/9111790336](https://tieba.baidu.com/p/9111790336)（2025-07-10 前后）｜[p/8715454843](https://tieba.baidu.com/p/8715454843)（2025）｜[p/9740390586](https://tieba.baidu.com/p/9740390586##1)（2026）
- 其他：[小酒窝回退警告](https://jiuwo.me/u/polaris/activity/replies)（2026-03-27）｜[GitCode 迁移教程](https://blog.gitcode.com/721d95268eb69baa62808cc295a5ceac.html)（2026-02-03）｜[SillyDroid 迁移文档](https://github.com/alipymanbu/Android/blob/master/%E5%AE%98%E7%BD%91%E7%89%88APP%E4%B8%8B%E8%BD%BD/SillyDroid/Termux%E6%95%B0%E6%8D%AE%E8%BF%81%E7%A7%BB%E4%B8%8E%E5%A4%87%E4%BB%BD.md)（2026-09-28）

**Reddit（间接）**：[ski52nn.ru 镜像页](http://ski52nn.ru/x10zu/silly-tavern-import-characters-reddit.html)（无日期，待复核）

**竞品/生态**：[RisuAI #1519](https://github.com/kwaroran/RisuAI/issues/1519)（2026-07-27）｜[RisuAI #1018](https://github.com/kwaroran/RisuAI/issues/1018)（2025-08-17）｜[TavernAI 2 迁移文档](https://tavernai.net/docs/migrating-from-tavernaiv1-sillytavern/)｜[Foreverse 整站搬家](https://foreverse.app/zh/docs/guide-roleplay/migrate-from-sillytavern)（2026-08-11）｜[Foreverse 导入失败模式](https://foreverse.app/blog/import-character-cards-android)（2026-07-18）｜[OrbWeaver Coming-from-ST](https://github-wiki-see.page/m/Inktomi93/OrbWeaver/wiki/Coming-from-SillyTavern)（2026-10-10）｜[Local Waifu 卡导入指南](https://localwaifu.com/blog/character-card-png-not-importing/)（2026-10-17）

> 合规说明：本报告仅做只读公开信息整理；未在社区发言、未私信用户、未收集任何账号信息；
> 引文均为公开内容且未附带用户名；用户公开上传的文件**未下载、未用作样本**。
