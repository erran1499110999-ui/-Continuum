# 真实失败案例库（failure-case-library）

> 编制：researcher（Agent Teams）｜ 日期：2026-11-06
> 数据来源：公开社区（GitHub 官方仓库 Issues/PR、NGA、百度贴吧、小酒窝论坛、第三方镜像），
> 全部案例已收录于 [docs/research-community.md](./research-community.md)，本库为其结构化版。
> 用途：供 qa-reviewer 设计回归测试、外部开发者会话做 V3/CHARX/1.12+ 兼容性更新参考。
>
> **重要声明（AGENTS.md 规则 9）**：
> 1. 案例中用户公开贴出的文件**未经授权**，只作「场景参考」，**绝不直接下载用作测试样本**；
>    测试样本必须为**经用户授权的脱敏样本**或**合成样本（synthetic）**。
> 2. 「机制」一栏严格区分【官方确认】（维护者在 PR/Issue 中确认或已合入修复）与
>    【用户报告】（仅报告者描述，未官方确认）；不猜测字段与根因。
> 3. 用户名一律不引用，仅以来源编号指代。
> 4. 本库只建议、不实施任何代码或测试改动。

---

## 0. 概览

- 收录 ST（SillyTavern）相关案例 **20 条** + 竞品（RisuAI）参照案例 2 条 + 待复核（Reddit 镜像）1 组。
- 优先级口径：**P0**＝存在静默数据破坏路径或官方确认缺陷，建议首轮回归覆盖；
  **P1**＝高频/高情感强度，或恢复保真问题；**P2**＝用户误操作、指引缺失、生态参照。
- 产品能力标签：体检（scan/diagnose）、备份（backup）、修复（repair R0/R1/R2/R3）、迁移（migrate）。

---

## 1. P0 案例（静默数据破坏 / 官方确认缺陷）

### CASE-01 同角色多聊天切换导致聊天被重置为「header + 开场白」
- 来源/日期：[SillyTavern#6032](https://github.com/SillyTavern/SillyTavern/issues/6032)，2026-09-13，open
- 现象（原话）：*"In several earlier occurrences, a populated chat was ultimately replaced with only its metadata/header and a newly instantiated character greeting."*（受影响文件只剩 2 条有效记录）
- 机制：**【用户报告，未官方确认】** 同角色聊天共享 `this_chid`，切换时保存目标文件名与内存中的 integrity UUID 临时错配；integrity 只做「身份」校验、不做「版本」校验，部分路径被跳过校验后覆盖写入。
- 可复现步骤（报告者提供）：同一角色建多个独立聊天 → 在聊天 A/B 间频繁切换 → 间歇性出现 B 的保存携带 A 的 integrity UUID；未点 OVERWRITE 时被拦截，早期若干次已发生破坏性写入。
- 产品能力建议：**体检**（扫描同一角色目录下多个 chat JSONL 的 `chat_metadata.integrity`，发现重复/异常 slug 告警）；**备份**（对外部工具而言，先备份再操作是唯一保险）；**修复**（对「只剩 header+开场白」的文件判 R2：不可伪造历史，提示从 `backups/` 或外部备份恢复）。
- 优先级：**P0**

### CASE-02 v1.16.0 integrity 不匹配时无确认弹窗直接重置聊天
- 来源/日期：[SillyTavern#5454](https://github.com/SillyTavern/SillyTavern/issues/5454)，2026-04-14
- 现象（原话）：*"Chat files are being reset without user confirmation when integrity check fails. Previous versions showed a confirmation dialog."*
- 机制：**【用户报告】** 1.16.0 行为回归；服务端日志 `File does not have integrity metadata matching …`。
- 产品能力建议：**体检**（把「header 无法解析 / integrity 缺失」列为高危发现，而不是当作普通旧格式）；**备份**（升级 ST 前体检 + 全量备份，对应企划书场景 A）。
- 优先级：**P0**

### CASE-03 聊天首行损坏（截断/BOM/编码）时被静默覆盖
- 来源/日期：[SillyTavern PR#5458](https://github.com/SillyTavern/SillyTavern/pull/5458)，2026-04-15（closed）
- 现象：聊天文件首行无法解析（损坏、Termux BOM、截断）时，`tryParse()` 返回 undefined → 完整性校验被跳过 → 文件被**无确认覆盖**。
- 机制：**【官方确认】** PR 自述该数据丢失路径并修复（首行不可解析时改为触发 OVERWRITE 确认）。
- 产品能力建议：**体检**（JSONL 首行必须是合法 header：对损坏首行判 P0 级发现，绝不静默放行）；**修复**（截断首行 → R2 仅建议从备份恢复；BOM 剥离 → R0 候选，需样本验证）。
- 优先级：**P0**

### CASE-04 确认 OVERWRITE 后旧版本永不落快照
- 来源/日期：[SillyTavern PR#5980](https://github.com/SillyTavern/SillyTavern/pull/5980)，2026-08-24
- 现象：用户确认 OVERWRITE（in-flight 冲突）后，磁盘上的旧文件**没有进入任何备份**，永久丢失。
- 机制：**【官方确认】** 原实现「先写新数据、后备份新数据」，覆盖前的旧字节从不落盘；修复为覆盖前先快照到 `backups/`。
- 产品能力建议：**备份**（本产品任何写操作前强制快照——已符合 AGENTS.md 规则 1/5）；**体检**（识别 `backups/` 目录缺失/过旧，提示用户）。
- 优先级：**P0**

### CASE-05 自动备份出现数周级时间空洞
- 来源/日期：[SillyTavern#5796](https://github.com/SillyTavern/SillyTavern/issues/5796)，2026-06-25，open
- 现象（原话）：*"all backup files between May 25th, May 31st, and early June are completely missing"*；误删后无备份可恢复。*"Losing months of creative writing due to this backup fracture has been deeply upsetting."*
- 机制：**【部分官方确认】** 与备份键冲突 + 保留策略相关：PR#5944 确认「busy chats silently evict the backups of quiet ones」；本案例报告者另有 Termux 环境因素，未完全归因。
- 产品能力建议：**备份**（本产品独立于 ST 内置备份，覆盖 `data/` 全量 + manifest 哈希）；**体检**（对 ST 内置 `backups/` 目录做「连续性检查」：按角色统计备份时间跨度，空洞告警——直接呼应本案例）。
- 优先级：**P0**

### CASE-06 中文角色名备份文件名冲突 → 共享备份配额、静默挤掉
- 来源/日期：[SillyTavern#5780](https://github.com/SillyTavern/SillyTavern/issues/5780)，2026-06-17，【官方 Confirmed】，2026-09-14 关闭（PR#5944 修复）
- 现象（原话）：*"雷电将军 → ______、测试角色 → ______，Both become 'chat______' prefix… all Chinese characters share one combined backup quota"*
- 机制：**【官方确认】** 备份文件名把非字母数字字符全替换为下划线，CJK 名碰撞；`numberOfBackups` 按 sanitized 前缀计配额。
- 产品能力建议：**体检**（扫描 `backups/` 文件名碰撞 + 每角色备份数，中文环境高价值）；**迁移**（迁移清单中的聊天名保持原始 Unicode，不套用 ST 的 sanitize 逻辑）。
- 优先级：**P0**

### CASE-07 同名角色卡导入随机覆盖旧卡（内容被替换）
- 来源/日期：[SillyTavern#5756](https://github.com/SillyTavern/SillyTavern/issues/5756)，2026-06-09
- 现象（原话）：*"When importing character cards with duplicate names, it randomly overwrites one of the existing old cards… This causes the old card to be completely lost (only the cover image remains)."*（用户持 8000+ 卡，每次批量导入后发现卡内容被替换）
- 机制：**【用户报告，未官方确认】** 按名字键控的角色存储同名冲突。
- 产品能力建议：**体检**（重复角色检测——企划书 3.2 已列「重复角色」；扩展到「同名不同内容哈希」比对）；**备份**（批量导入前先备份 `characters/`）。
- 优先级：**P0**

### CASE-08 settings.json 损坏 → 界面白屏、无容错
- 来源/日期：[SillyTavern#4166](https://github.com/SillyTavern/SillyTavern/issues/4166)，2025-06-15，closed 2025-12
- 现象：清理连接配置（改 IP/重命名/删除）时并发写坏 settings JSON，`getSettings()` 里 `JSON.parse` 直接抛错，页面齿轮永转、白屏。
- 机制：**【用户报告】** 无 JSON 解析容错；修复版增加处理（closed）。
- 产品能力建议：**体检**（settings.json 合法性校验 + 字段级告警，不执行其内容）；**修复**（末尾逗号 → 现有 R0-001；更深损坏 → R2 从备份恢复）。
- 优先级：**P0**

### CASE-09 聊天中角色定义被另一角色覆盖、聊天挂错角色
- 来源/日期：[SillyTavern#3667](https://github.com/SillyTavern/SillyTavern/issues/3667)，2025-03-12，closed 2025-04（✅ Done）
- 现象（原话）：*"suddenly I got changed to the character [B]… when I come to the first character is lost the all of the chat of the first character go to second character"*
- 机制：**【官方已处理】** 维护者接手并合入修复（Done 标签）；具体根因在 issue 讨论中，未逐字段公开。
- 产品能力建议：**体检**（聊天目录归属校验：`chats/<角色名>/` 下 JSONL 的 header/message 中角色名与目录名不一致时告警）；**迁移**（迁移清单按文件名+内容双键校验归属）。
- 优先级：**P0**

---

## 2. P1 案例（高频 / 恢复保真 / 升级降级断裂）

### CASE-10 误删聊天且内置备份无法找回
- 来源/日期：[SillyTavern#5797](https://github.com/SillyTavern/SillyTavern/issues/5797)，2026-06-25，open（Feature Request）
- 现象（原话）：*"I once accidentally deleted my most precious chat log while cleaning up chats, because the deletion popup didn't show clearly which file was being deleted. I'm heartbroken."*；内置备份亦未找回。
- 机制：UI 不展示被删对象元数据、无双重确认；叠加 CASE-05/06 的备份缺口。
- 产品能力建议：**备份**（独立快照 + 版本化）；**体检**（`backups/` 可恢复性自检：最近备份时间、文件可解析性）。
- 优先级：**P1**

### CASE-11 备份导入后聊天不保真（只能续到开头）
- 来源/日期：[SillyTavern#3895](https://github.com/SillyTavern/SillyTavern/issues/3895)，2025-04-20
- 现象（原话）：*"Import the chat jsonl - Attempt to chat from where to last left off, but it won't work. The prompt sent will only include the beginning of the chat history."*
- 机制：**【用户报告】** 导出→删除→再导入往返后历史定位失效；具体根因未确认（可能涉及 chat_metadata/索引字段）。
- 产品能力建议：**迁移**（往返保真测试必须覆盖：导入导出后逐行比对消息数/顺序/时间戳/metadata——企划书提示词 7 已要求）；**体检**（导入后校验消息计数与最后消息）。
- 优先级：**P1**

### CASE-12 中文聊天名备份 ENOENT + 手机端备份列表 >1 分钟
- 来源/日期：[SillyTavern#4936](https://github.com/SillyTavern/SillyTavern/issues/4936)，2025-12-31，open
- 现象：中文聊天名备份文件报 `ENOENT`；官方备份列表在 Android(Termux) 加载 >1 分钟甚至挂死。
- 机制：**【用户报告】** 文件名过度 sanitize + 列表渲染全量解析 2MB+ JSON。
- 附带价值：报告者给出可行优化方向（读尾部 100KB、按 metadata 显示角色名、按日期范围过滤）——本产品 UI 的备份列表设计可参考。
- 产品能力建议：**体检/备份 UI**（大文件只读尾部 + 元数据索引；中文文件名不做 sanitize）。
- 优先级：**P1**

### CASE-13 降级版本 → 配置/聊天不兼容、白屏
- 来源/日期：[小酒窝论坛回复](https://jiuwo.me/u/polaris/activity/replies)，2026-03-27
- 现象（原话）：*"版本回退并非无损操作！新版本的配置文件（config.yaml）和聊天记录可能与旧版本不兼容。直接降级可能导致数据不兼容，出现酒馆白屏打不开等问题。回退之前一定要先备份，先备份，先备份"*
- 机制：**【社区经验，未官方确认】** 跨版本 schema 不向后兼容。
- 产品能力建议：**备份**（升级/降级前强制体检+备份，企划书场景 A）；**迁移**（迁移报告标注源版本；对未知版本字段原样保留不猜测）。
- 优先级：**P1**

### CASE-14 酒馆报错白屏后，无界面抢救数据全靠手工
- 来源/日期：[NGA tid=43673259](https://ngabbs.com/read.php?tid=43673259&rand=368)，2025（月份未显示）
- 现象（原话）：*"我的酒馆因为不明原因声称缺少档案…旧的酒馆变成可以开但是一片空白"*；社区一步步教复制 `data` 文件夹、先开新酒馆再粘贴、手动批量导入；最终结论：*"理论上所有用户数据都在data文件夹里面，里面没东西就是没了。"*
- 机制：**【用户报告】** 界面不可用时没有官方独立数据抢救工具。
- 产品能力建议：**体检+备份**（本产品完全独立于 ST 界面运行，正是此场景的解法——「ST 挂了也能救数据」应写入产品文案）；**迁移**（`data/` 结构探测：缺失 `chats/`/`characters/` 等目录时输出结构级提示）。
- 优先级：**P1**

### CASE-15 1.12 目录大迁移后民间教程仍在「手动搬文件夹」
- 来源/日期：[GitCode 教程](https://blog.gitcode.com/721d95268eb69baa62808cc295a5ceac.html)，2026-02-03
- 现象：教程列出必须备份目录清单并警告 *"不要复制整个public文件夹！"*，给出 <1.12.0 → ≥1.20.0 的手动迁移路径。
- 机制：**【生态事实】** 1.12.0 布局变更（详见 [research-sillytavern.md](./research-sillytavern.md) 第 4 节）导致用户自行拷贝时出错风险高。
- 产品能力建议：**迁移**（自动识别新旧布局并生成迁移对照，替代手工教程）；**体检**（检测「新布局里残留旧 public/ 结构」的混合状态）。
- 优先级：**P1**

### CASE-16 官方迁移指南之外的升级路径也明示「可能丢数据」
- 来源/日期：[ST 1.9.0 迁移指南](https://github.com/sillytavern/sillytavern-docs/blob/ed5423d809c6b10b8c1e9ef4a0c8ddc7f2ef7f3d/Installation/Updating/migration-guide-1-09.md)（现行文档，访问日 2026-11-06）
- 现象（官方原话）：*"You may lose your data in the process, so don't ignore this warning."*（分支切换/升级前必须先完整备份）
- 机制：**【官方声明】** 升级流程自身承认数据丢失风险。
- 产品能力建议：**备份**（升级前体检 + 完整备份 + 升级后差异对比，正是企划书场景 A 的产品化）；本案例可作为产品文案的官方背书引用。
- 优先级：**P1**

---

## 3. P2 案例（误操作 / 指引缺失 / 生态参照）

### CASE-17 下载到「只有图没有角色数据」的文件
- 来源/日期：[NGA tid=46880846](https://ngabbs.com/read.php?tid=46880846&rand=628)，2026-05-29
- 现象（原话）：*"json格式损坏…把文件名改为.json，丢给AI帮你检查"*、*"我也是研究了好一会才明白怎么把那个图片给下载下来"*（社区多人复现：右键保存的是无元数据的封面图/缩略图）
- 机制：**【用户报告/生态事实】** 分发渠道（社区/频道）图片被二次压缩或保存路径错误，PNG 中 tEXt `chara`/`ccv3` 块丢失。
- 产品能力建议：**体检**（PNG 无角色卡元数据 → 明确提示「这是纯图片，不是角色卡」——现有 `FileKind.PNG` 已能识别，需在产品话术中强化）；**修复**（R2：提示从原链接重新下载，绝不伪造）。
- 优先级：**P2**

### CASE-18 多张卡导入全部报「文件损坏」
- 来源/日期：[NGA tid=46837169](https://ngabbs.com/read.php?tid=46837169&page=e&_fp=13&rand=80)，2026-05
- 现象（原话）：*"导入角色卡的时候无论是png还是js格式都说文件损坏，换了好几个还不行"*；社区建议「新建卡自测导入」「发给 AI 检查 JSON」。
- 机制：**【用户报告】** 未定位；可能是下载错误文件或真实损坏，缺诊断手段。
- 产品能力建议：**体检**（角色卡批量健康检查：PNG 块存在性 + JSON 结构 + 字段完整性，输出可读报告——直接替代「发给 AI 检查」的手工路径）。
- 优先级：**P2**

### CASE-19 Discord CDN 超时 → 链接导入失败、本地导入报 invalid/corrupted
- 来源/日期：[NGA tid=44940658](https://ngabbs.com/read.php?tid=44940658&topid=837719626&page=1&rand=911)，2025-08-27
- 现象（原话）：*"FetchError: request to https://cdn.discordapp.com/… failed reason: connect ETIMEDOUT"*；本地下载的 PNG 也报 *"Could not import character The file is likely invalid or corrupted"*。
- 机制：**【用户报告】** 网络原因与文件原因被同一句错误提示掩盖，用户无法区分。
- 产品能力建议：**体检**（本地文件级诊断可区分「文件本身损坏」vs「下载不完整」vs「无元数据」——本产品只处理本地文件，天然规避网络环节）。
- 优先级：**P2**

### CASE-20 Discord 等渠道剥离 PNG 元数据（分发侧破坏）
- 来源/日期：Reddit 镜像页转述（[ski52nn.ru 镜像](http://ski52nn.ru/x10zu/silly-tavern-import-characters-reddit.html)，无日期，**待复核**）
- 现象（转述）：*"in the past few weeks Discord removed the metadata functionality, stripping it from all new and previously uploaded PNGs"*
- 机制：**【待复核的社区说法】** 分发渠道对 PNG 再编码导致 tEXt 块丢失。
- 产品能力建议：**体检**（同 CASE-17：无元数据 PNG 的明确诊断）；**迁移**（若用户只有「图 + 手抄设定」，R2 建议人工重建，绝不编造）。
- 优先级：**P2（待复核）**

### CASE-21 世界书（lorebook）导入/生效困惑
- 来源/日期：[贴吧 p/8715454843](https://tieba.baidu.com/p/8715454843)，2025
- 现象（原话）：*"世界书不生效怎么办啊？"*、*"下载了一个json档之后请问该怎么使用"*（云端版与本地版界面不一致加剧困惑）
- 机制：**【用户报告】** 使用/配置门槛，非数据损坏。
- 产品能力建议：**体检**（lorebook 结构检查：`entries`/`character_book` 存在性、条目键缺失告警——现有 `looks_like_world_info` 可扩展）；**迁移**（原样保留全部字段，见现有实现）。
- 优先级：**P2**

### CASE-22 复杂配置（世界书+正则）靠散落教程与自研脚本维护
- 来源/日期：[贴吧 p/9111790336](https://tieba.baidu.com/p/9111790336)，2025-07 前后；[贴吧 p/9740390586](https://tieba.baidu.com/p/9740390586##1)，2026
- 现象：部署脚本作者把备份/导出（角色卡、聊天记录、预设、背景图）做成脚本并在评论区手写教程；deepseek吧用户为玩酒馆卡自研「读卡器+知识库」方案，并指出酒馆靠世界观和正则解决记忆丢失。
- 机制：**【生态事实】** 备份与配置知识高度分散。
- 产品能力建议：**体检/备份**（一键覆盖全部数据类别，替代散落脚本）；产品内容（迁移前检查清单、健康报告）正好命中企划书 4.4 的「可被搜索到的工具内容」策略。
- 优先级：**P2**

---

## 4. 竞品参照案例（RisuAI，第二客户端适配器规划用）

### CASE-23 重掷/swipe 变体在继续聊天或删除后续消息后丢失
- 来源/日期：[kwaroran/RisuAI#1519](https://github.com/kwaroran/RisuAI/issues/1519)，2026-07-27
- 现象：assistant 消息的多个 reroll 变体未持久化；继续对话或删除后续消息后无法再访问。
- 机制：**【用户报告】** 变体存储/索引策略问题。
- 对项目的启示：未来 RisuAI 适配器需把 `swipes` 视为一等数据做完整迁移与往返保真测试（提示词 7 的 message 顺序/数量检查同源）。
- 优先级：P2（第二客户端阶段）

### CASE-24 降级后自动保存失效，重启即丢修改
- 来源/日期：[kwaroran/RisuAI#1018](https://github.com/kwaroran/RisuAI/issues/1018)，2025-08-17
- 现象：从 v166.3.0 降到 v166.0.1 后自动保存失效，关闭重开即丢失 prompts/modules/卡片/聊天修改。
- 机制：**【用户报告】** 跨版本降级的不兼容。
- 对项目的启示：跨版本「降级」场景的兼容矩阵与警告（同 CASE-13）。
- 优先级：P2（第二客户端阶段）

---

## 5. 样本回归测试设计输入（只建议，不实施）

> 以下按案例给出**合成样本**设计要点，供 `tests/` 与 `samples/synthetic/` 规划；
> 所有样本一律人工构造/脚本生成，**不使用**任何案例中的真实用户文件（规则 9）。

| 案例 | 合成样本要点 | 建议断言方向 |
|---|---|---|
| CASE-01/02 | 同一角色目录下两个 chat JSONL，header `integrity` 相同或缺失；再构造「header+单条开场白」的退化文件 | 检测 integrity 重复/缺失 → 高危告警；退化文件识别为「疑似被重置」→ R2 |
| CASE-03 | JSONL 首行三种损坏：UTF-8 BOM 前缀、截断半个 JSON、乱码行 | 首行不可解析必须报 P0 级发现；BOM 剥离是否入 R0 需真实样本确认后再定 |
| CASE-04 | `backups/` 目录存在但为空/过旧（时间戳早于主文件 mtime 很久） | 「备份连续性」检查：空洞告警 |
| CASE-05/06 | 中文角色名（如「雷电将军」「测试角色」）多聊天；`backups/` 内含 `chat______*` 碰撞文件名 | 碰撞检测 + 每角色备份计数；迁移清单保持原始 Unicode 名 |
| CASE-07 | `characters/` 下两张同名卡（同 `data.name`、不同内容哈希） | 重复角色检测（企划书 3.2 已有）→ 内容差异报告 |
| CASE-08 | settings.json：合法 / 末尾多余逗号 / 截断 / 嵌套过深 | R0-001 修复；截断 → R2；深度上限告警 |
| CASE-09 | `chats/<角色A>/` 内 JSONL 的 header `character_name` 或消息 `name` 指向角色 B | 归属不一致告警（迁移清单双键校验） |
| CASE-10/11 | 完整长聊天（如 200 条消息）导出→再导入 | 往返保真：消息数/顺序/时间戳/metadata 逐项比对（提示词 7） |
| CASE-12 | 2MB+ 大 JSONL | 尾部读取路径：只解析末尾 100KB 时仍能取到最后一条消息；性能上限（max_chat_lines/字节）生效 |
| CASE-13/16 | 旧版无 `integrity` 字段的 header（legacy 格式） | 旧格式必须「告警但不误伤」：不得当作损坏 |
| CASE-14 | `data/` 缺少 `chats/` 或 `characters/` 目录 | 结构级提示：指出缺什么、从哪恢复 |
| CASE-15 | 混合布局：新 `data/` 与残留旧 `public/` 并存 | 双布局检测逻辑（research-sillytavern.md P0-3） |
| CASE-17/19/20 | 无 tEXt 块的纯图片 PNG（封面图）；`chara` 块损坏的 PNG；仅 `ccv3` 块的 PNG | 类型判定：纯图片→PNG 提示；块损坏→corrupt_png；仅 ccv3→必须支持 V3 读取（P0-1） |
| CASE-18 | 批量目录内混合：好卡 + 损坏卡 + 纯图片 | 批量健康报告逐文件结论 |
| CASE-21 | 无 `entries`/`character_book` 的 JSON；条目缺 `keys` 的 lorebook | lorebook 结构检查与告警分级 |
| CASE-23/24 | （第二客户端阶段）含 swipes 的 RisuAI 导出样本 | swipes 完整性迁移（留档，暂不实施） |

**新增检测规则候选（供外部会话/qa 评审，不实施）**：
- `integrity` 重复/缺失检测（CASE-01/02/13）；
- 「疑似被重置」聊天识别：行数=2 且首行 header、次行为该角色 first_mes（CASE-01）；
- 备份连续性与文件名碰撞检查（CASE-04/05/06/12）；
- 聊天-角色归属校验（CASE-09）。

---

## 6. 主要来源

见 [docs/research-community.md](./research-community.md) 第 9 节完整来源列表（本库与之一致）。
本库新增引用：[ST 1.9.0 迁移指南](https://github.com/sillytavern/sillytavern-docs/blob/ed5423d809c6b10b8c1e9ef4a0c8ddc7f2ef7f3d/Installation/Updating/migration-guide-1-09.md)。

> 合规重申：本库为公开信息的结构化整理；未下载任何用户文件；测试样本须经授权或合成；
> 本库不构成对任何第三方软件缺陷的指控，仅作为产品测试场景参考。
