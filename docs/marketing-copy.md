# 推广与文案（marketing-copy）

> 编制：researcher（Agent Teams，兼推广文案）｜ 日期：2026-11-07
> 用途：产品一句话定位、名称与口号候选、广告词与文案模板（中英双语）、推广渠道与节奏、
> 合规红线。全部为建议稿，最终口径由创始人确认。
> 遵守：企划书 4.4（社区规则、不刷屏）、规则 2（默认不上传）、规则 8（无 NFT/代币/钱包/云上传）。

---

## 1. 产品一句话定位（中英）

- 中文：「**本地优先的 SillyTavern 数据救生员**——备份、体检、修复、迁移，角色与聊天数据永不离开你的电脑。」
- English: "**A local-first rescue kit for SillyTavern** — back up, diagnose, repair, and migrate your characters and chats. Your data never leaves your machine."
- 电梯版（30 秒口播）：「酒馆（SillyTavern）升级、换机、误删、文件损坏——你的角色卡和几万条聊天记录怎么办？Continuity Studio 在你电脑上本地运行：先体检，再备份，修复只生成副本绝不覆盖原文件。全程不联网、不上传。」

---

## 2. 名称与口号候选（供创始人挑选）

### 2.1 产品名候选
| 候选 | 语言 | 说明 |
|---|---|---|
| **Continuity Studio**（沿用） | EN/CN | 与项目历史一致，GitHub 仓库名已定；「连续性」点题 |
| 中文并列名：**「角色续命站」** | CN | 记忆点强，贴合「救数据」心智；偏口语 |
| 中文并列名：**「酒馆保险箱」** | CN | 对 ST 用户（酒馆圈）一眼懂；但绑定单一客户端 |
| 中文并列名：**「角色档案局」** | CN | 专业感，覆盖备份/版本/迁移；偏正式 |

> 建议：对外主名 **Continuity Studio**，中文圈传播名用「酒馆保险箱」（ST 社区）或「角色档案局」（通用），落地页可并列展示。

### 2.2 口号候选
| 中文 | English |
|---|---|
| 你的角色，永远不离开这台电脑 | Your characters never leave this machine |
| 数据不出门，角色不断线 | Local by design. Continuous by default. |
| 先体检，再动手；只生成副本，从不覆盖 | Diagnose first. Repair to a copy. Never overwrite. |
| 酒馆升级不怕，换机迁移不慌 | Tavern updates without the fear of losing it all |
| 不承诺魔法，只做可验证的修复 | No magic. Just verifiable repairs. |

> 推荐组合：主口号「**数据不出门，角色不断线**」（CN）/「**Local by design. Continuous by default.**」（EN）；副口号「不承诺魔法，只做可验证的修复」用于信任页。

---

## 3. 广告词与文案模板

### 3.1 README 首屏（中英双语建议稿）
- H1（CN）：**Continuity Studio —— 本地优先的角色数据救生员**
- H1（EN）：**Continuity Studio — a local-first rescue kit for your AI roleplay data**
- 副标题（CN）：备份、体检、修复、迁移 SillyTavern 角色卡 / 聊天记录 / 世界书。**全程本地运行，默认不上传任何数据。**
- 副标题（EN）：Back up, diagnose, repair, and migrate SillyTavern characters, chats, and lorebooks. **Runs entirely on your machine. Nothing is uploaded by default.**
- 三个信任点（首屏三列）：
  1. 「只读扫描 + 修复输出到新目录，绝不覆盖原文件」（Read-only scans; repairs go to a new folder. Never overwrite.）
  2. 「每个动作都有日志与差异报告，可解释、可回滚」（Every action is logged with a diff report — explainable and reversible.）
  3. 「R0/R1/R2 修复分级：能修什么、要你确认什么、修不了什么，写清楚」（Explicit repair tiers: automatic / needs confirmation / suggestion-only.）

### 3.2 落地页文案（首页结构建议）
1. Hero：口号 + 一句话定位 + 主按钮「下载免费版 / 查看源码」+ 副按钮「看看它怎么救数据（3 分钟演示）」。
2. 场景区（对应企划书 4.2 四场景）：
   - 「升级前体检」：升级 ST 前跑一遍，生成完整备份；升级后异常？恢复到新目录，逐项对比差异。
   - 「分享前检查」：把卡和世界书分享给朋友前，检查引用、缺失资源和敏感字段，生成兼容包。
   - 「换客户端迁移」：字段映射清单 + 不兼容项列表 + 需人工确认项。
   - 「创作者版本对比」：新版本与旧版本逐字段对比，防止人格定义/开场白/示例对话意外丢失。
3. 信任区（合规红线落地）：
   - 「默认不上传。没有账号，没有云端，没有遥测。」（No accounts. No cloud. No telemetry.）
   - 「修复不是魔法：没有来源的数据无法重建，系统会明确告诉你『这只能靠备份』。」（We can't conjure lost memories — the app tells you exactly what needs a backup.）
4. CTA 区：免费版 / 开源仓库 / 社区案例页。

### 3.3 社区发帖文案模板（三篇，价值优先、不刷屏）

**模板 A｜Reddit r/SillyTavernAI（价值帖：迁移检查清单）**
- 标题（EN）：*Before you update SillyTavern: a 5-minute pre-update checklist (chats, cards, lorebooks)*
- 正文要点：① 你的数据现在在哪（1.12+ 是 `data/`，旧版是 `public/`）——升级前先确认；② 官方聊天自动备份的两个已知坑（CJK 名字备份键冲突、备份空洞）与自查方法；③ 一个免费本地工具可以一键做这些（附 GitHub 链接）；④ 声明：工具作者、本地运行、不上传数据、欢迎反馈。**先读版规、不带追踪链接、只发一次。**

**模板 B｜Discord 酒馆相关频道（求助帖回应式，不主动开新推销帖）**
- 当有人问「怎么备份/怎么找回误删聊天」时回复：先给**不依赖任何工具的手工步骤**（复制 `data/` 目录、从 `backups/` 找回、先开新酒馆再粘贴——社区已有共识），最后一句附工具链接：「如果你觉得手工太麻烦，这个本地工具能一键做，开源、不上传数据。」

**模板 C｜百度贴吧 / NGA（中文，案例科普帖）**
- 标题：「酒馆白屏/换机/误删怎么办：一个不需要打开酒馆界面的本地工具」
- 正文要点：① 你的角色卡和聊天记录实际存在哪个文件夹；② 界面打不开也能救（工具独立于酒馆运行）；③ 修复只生成副本绝不覆盖；④ 免费、开源、中文界面。**遵守贴吧吧规，不刷楼，不私信轰炸。**

**模板 D｜GitHub（发布公告 / README）**
- Release notes 风格：What's new → 谁需要它 → 已知限制（V3/CHARX 进度、不支持的客户端）→ 反馈渠道。

---

## 4. 推广渠道与节奏（结合企划书 4.4 与社区调研）

| 阶段 | 渠道 | 动作 | 规则红线 |
|---|---|---|---|
| 现在–第 8 周 | GitHub | 仓库 README 双语、发布「兼容性报告」「迁移前检查清单」文档（可被搜索的工具内容） | 不夸大、标注已知限制 |
| 第 9–10 周（可用性测试） | Discord（需创始人凭据）、贴吧/NGA | 求助帖价值回复 + 案例科普帖；邀请 5–10 名测试用户 | 先读版规；不刷屏（4.4）；凭据仅环境变量只读 |
| 第 9–10 周 | Reddit（需登录凭据或授权） | r/SillyTavernAI 发布检查清单帖 + 演示 | 版规自查、不重复发 |
| 第 11–12 周（收费验证前） | 全渠道 | 「真实失败案例修复集」内容（基于案例库，匿名化） | 不虚构案例、用户授权后才用真实文件 |
| 全程 | 官网/落地页 | 风格按 ui-design-direction 双轨 | 合规红线见第 5 节 |

---

## 5. 合规红线（所有对外文案必须遵守）

1. **不夸大修复能力**：禁止「数据恢复魔法」「100% 找回」类表述；一律使用「可验证的结构修复」「缺失内容只能从备份恢复」（企划书 1.2 与规则 4）。
2. **修复分级必须可见**：凡提到修复，必须出现 R0（自动）/R1（需确认）/R2（仅建议）的语义说明，不做模糊承诺。
3. **不承诺人格一致**：跨客户端/跨模型迁移不保证「同一个灵魂」（企划书 1.2「不是 AI 灵魂转移」）。
4. **隐私表述准确**：说「默认不上传」而非「绝对不联网」（依赖更新等场景存在）；不声称「端到端加密」等未实现能力。
5. **不虚构**：不编造用户数、下载量、收入、市场规模、融资表述；案例须真实且匿名化/经授权（规则 10 精神）。
6. **规则 8**：所有文案与推广材料不含 NFT、代币、钱包、加密货币支付、云端上传引导。
7. **内容中性**：产品处理的是文件，不托管角色内容；对外文案避免成人内容暗示，社区发布遵守各平台内容分级与版规。
8. **社区礼仪**：先读版规、先贡献价值（检查清单/开源工具）再提及产品；不私信轰炸、不刷屏（企划书 4.4 原话）；Discord/Reddit 等需登录的渠道待创始人凭据后才操作。

---

## 6. 来源与联动

- 企划书 4.4（早期增长）、1.2（不要把产品定义成什么）、12 章（验证门槛）
- [research-community.md](./research-community.md)（渠道可达性与真实痛点语料）
- [failure-case-library.md](./failure-case-library.md)（案例科普素材，须匿名化+授权）
- [ui-design-direction.md](./ui-design-direction.md)（落地页风格）、[product-plan.md](./product-plan.md)（节奏）
- AGENTS.md 规则 2/4/8/10、TEAM-COORDINATION.md 创始人指令（双语产品描述）
