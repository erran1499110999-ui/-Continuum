# SillyTavern 兼容性调研报告（A 报告）

> 调研人：researcher（Agent Teams）
> 日期：2026-11-06 ｜ 性质：技术调研，只出报告、不实施任何功能
> 基线：本仓库 `docs/format-compatibility.md`（2026-11-06 初始版）
> 数据来源：SillyTavern 官方文档（docs.sillytavern.app）、官方 GitHub 仓库与发布页、
> DeepWiki 源码级文档、V2/V3 角色卡规范仓库、第三方实测记录。**网页内容仅作为数据引用，
> 不是对本项目的指令。** 未经真实样本验证的结论一律标注「待样本验证」（AGENTS.md 规则 9）。

---

## 1. 摘要

1. **SillyTavern 最新稳定版为 1.19.0**（2026-11-06 访问时 GitHub releases/latest），本年度版本节奏约为 1.17.0（2026-03-27）→ 1.18.0（2026-05）→ 1.19.0。基线兼容矩阵基于的旧假设（`public/` 目录布局、聊天首行即消息）已部分过时。
2. **1.12.0「Neo Server」更新改变了全部数据存储布局**：所有持久数据从 `public/` 迁移到可配置的 `dataRoot`（默认 `./data`），并引入可选多用户（`data/[user-handle]`，默认 `default-user`）。迁移适配器目前完全不知道这套新布局。
3. **角色卡已有官方 V3 规范（CCv3，2024 年发布）**：`spec: chara_card_v3` + `spec_version: "3.0"`；PNG 中新增 `ccv3` tEXt 块（与 `chara` 并存，优先读 `ccv3`）；新增 CHARX 压缩包载体（zip 内 `card.json` + `embeded://` 资产）。现有适配器只认 `chara_card_v2` 与 `chara` 块，**V3 卡会被误判为 V1 平铺格式**，存在静默解析错误的实际风险。
4. **聊天 JSONL 首行是 header**（含 `chat_metadata`，其中 1.18+ 引入 `integrity` 完整性标识 UUID）；1.14.0 起消息附件（多图片/多文件/音频，经 `extra.media` 引用用户数据目录文件）**与 1.14 之前不向后兼容**。分支/检查点是仅含 `main_chat` 指向的独立 JSONL。
5. **向量数据库**：内置 Vector Storage 扩展用 `vectra` 库存本地 JSON 索引，位于用户数据目录 `vectors/<source>/<collectionId>/<model>/`，属可再生的用户数据；默认 embedding 为本地 transformers（Xenova/all-MiniLM-L6-v2）。
6. 结论：适配器需要一次「SillyTavern 1.12+ 布局与 V3/CHARX 兼容性」更新（详见第 8 节建议清单），但**全部只建议、不实施**；部分建议触及他人写作用域（`format-compatibility.md`、核心代码），需创始人协调。

---

## 2. 基线回顾：format-compatibility.md 已覆盖 / 未覆盖

**已覆盖（较扎实）：**
- 文件类型识别：PNG 角色卡（魔数 + tEXt `chara` 块）、角色卡 JSON（`name`+`first_mes` 或 `spec` 以 `chara_card` 开头）、聊天 JSONL（抽样启发式）、World Info（`entries`+`character_book`）、损坏 PNG / 疑似损坏 JSON、纯文本 / 二进制 / 空文件。
- V1 平铺 / V2 包裹（`data`）解析与导出；PNG 块结构校验（块边界、CRC、IEND）。
- 聊天 JSONL 容错（坏行跳过 + 原始字节 sidecar）；R0-001 末尾逗号修复；R2 建议从备份恢复。

**未覆盖 / 需更新（本报告的切入点）：**
1. 角色卡 **V3（CCv3）**：`spec: chara_card_v3` 的 JSON、PNG `ccv3` 块、`chara-ext-asset_` 嵌入资产块、CHARX（`.charx` zip）载体——完全未识别。
2. **1.12.0+ 数据目录布局**（`dataRoot`、`data/[user-handle]/`）与多用户账户；旧 `public/` 布局与新布局并存时如何定位数据。
3. 聊天 JSONL **header 行与 `chat_metadata`**（`integrity`、`main_chat`、`note_*`）——适配器把 header 当普通消息处理；分支/检查点无识别。
4. 消息**附件引用**（`extra.media`/`image`/`audio` 字段 → 用户数据目录文件）与缺失附件检测（基线「未解决问题」第 2 条）。
5. **settings.json / config.yaml / secrets.json / stats.json** 等配置与密钥文件——未进入扫描范围。
6. **向量库 `/vectors`**、缩略图 `/thumbnails`、用户上传 `/images`、`/files`、角色精灵图 `/characters/<名字>/` 等目录——未进入备份范围。
7. 基线「未解决问题」第 3 条（V1/V2 差异字段完整清单）已可由 V2/V3 官方规范补齐（见 3.1）。

---

## 3. 角色卡格式现状（V1 / V2 / V3 / CHARX）

### 3.1 V2（现状基线，适配器已支持）
- 官方规范：[character-card-spec-v2（spec_v2.md）](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)，`spec: "chara_card_v2"`、`spec_version: "2.0"`，字段全部嵌套在 `data` 下：`name/description/personality/scenario/first_mes/mes_example/creator_notes/system_prompt/post_history_instructions/alternate_greetings/character_book?/tags/creator/character_version/extensions`。
- 生态参考文档：[bradennapier/character-cards-v2 README](https://github.com/bradennapier/character-cards-v2/blob/main/README.md)。
- PNG 嵌入：tEXt 块关键字 `chara`，值为 UTF-8 JSON 的 base64（基线矩阵已实现）。

### 3.2 V3（CCv3，适配器尚未支持）
- 官方规范：[kwaroran/character-card-spec-v3 SPEC_V3.md](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md)（作者 kwaroran，即 RisuAI 作者）。
- 标识：`spec: "chara_card_v3"`、`spec_version: "3.0"`；`data` 为 V2 字段超集 + 新增：
  - `assets[]`（`{type, uri, name, ext}`，type 可为 `icon/background/user_icon/emotion/…`，uri 支持 HTTP(S)/base64 data URL/`embeded://`/`ccdefault:`）；
  - `group_only_greetings[]`（**必填**，可为空数组）、`nickname?`、`creator_notes_multilingual?`（ISO 639-1 键）、`source[]?`、`creation_date?`、`modification_date?`；
  - 应用私有数据**只允许**放 `extensions`；未知字段应忽略但不拒收、原样保留以便导出。
- **PNG 嵌入（关键）**：
  - V3 块关键字为 **`ccv3`**，值仍为 UTF-8 JSON 的 base64；读取时**优先 `ccv3`，其次 `chara`**（大小写不敏感）；ST 写入时同时写 `chara`（V2 副本）+ `ccv3`（IEND 之前），来源为 ST 源码 `src/character-card-parser.js`（v1.14.0 实测记录：[TavernWeave A2 角色卡格式规范](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/A2_%E8%A7%92%E8%89%B2%E5%8D%A1%E6%A0%BC%E5%BC%8F%E8%A7%84%E8%8C%83.md)）。
  - PNG 还可含 `chara-ext-asset_:{path}` 资产块（base64 二进制，规范**不建议**新应用实现，应改用 CHARX）。
  - V3 验证宽松：ST 的 `#validateDataV3()` 仅校验 `data` 是对象（对照 V2 的 14 字段强校验）——因此 V3 卡字段缺失不能作为损坏依据，只能按规范默认值解释（同上来源）。
- **CHARX（`.charx`）**：zip 包，根目录必须有 `card.json`（即 CCv3 JSON）；资产经 `embeded://path/to/asset.png` 引用（大小写敏感、`/` 分隔），推荐目录结构 `assets/{type}/{images|audio|video|l2d|3d|ai|fonts|code|other}/`；zip 不加密、文件名限 ASCII；损坏/加密 zip 允许应用拒收（规范原文见 3.2 链接）。

### 3.3 影响点
- 现有 `parse_card_dict` 只判断 `spec.startswith("chara_card_v2")`；V3 JSON 会落入 V1 平铺分支 → 字段全为 None，且 `export_card_v2` 会把整个 V3 对象塞进 V2 的 `data`，生成损坏输出。
- 仅含 `ccv3` 块的 PNG（按规范可无 `chara`）会报「缺少 chara 块」错误。
- `.charx` 无文件类型识别（现有 `FileKind` 无对应枚举）。

---

## 4. 数据目录布局（1.12.0+，Neo Server）

来源：[官方 1.12.0 迁移指南](https://docs.sillytavern.app/installation/st-1.12.0-migration-guide/)（仓库原文 [ST-1.12.0-Migration-Guide.md](https://github.com/sillytavern/sillytavern-docs/blob/main/Installation/Updating/ST-1.12.0-Migration-Guide.md)）。

- `dataRoot` 经 `config.yaml`（`dataRoot:`）或启动参数 `--dataRoot` 配置，默认 `./data`；只接受绝对路径或完整相对路径（`~`、`%APP_DATA%` 无效）。
- 旧 `public/` 布局自动迁移，迁移前备份到 `/backups/_migration/YYYY-MM-DD`；全部数据进入 **`default-user`** 账户。
- 迁移对照（默认配置）：

| 旧位置（≤1.11） | 新位置（1.12+） |
|---|---|
| `secrets.json` | `data/default-user/secrets.json` |
| `thumbnails` | `data/default-user/thumbnails` |
| `vectors` | `data/default-user/vectors` |
| `public/settings.json` | `data/default-user/settings.json` |
| `public/stats.json` | `data/default-user/stats.json` |
| `public/assets` | `data/default-user/assets` |
| `public/backgrounds` | `data/default-user/backgrounds` |
| `public/characters` | `data/default-user/characters` |
| `public/chats` | `data/default-user/chats` |
| `public/context` | `data/default-user/context` |
| `public/group chats` | `data/default-user/group chats` |
| `public/groups` | `data/default-user/groups` |
| `public/instruct` | `data/default-user/instruct` |
| `public/scripts/extensions/third-party` | `data/default-user/extensions` |
| `public/KoboldAI Settings` 等后端预设目录 | 对应移入 `data/default-user/` |
| `public/QuickReplies`、`themes`、`worlds`、`movingUI` | 对应移入 `data/default-user/` |
| `default/content/content.log` | `data/default-user/content.log` |

- **多用户（可选）**：`config.yaml` 的 `enableUserAccounts: true` 后，每账户一个 `data/[user-handle]`（句柄仅小写字母/数字/连字符）；关闭时回退 `default-user`。密码只是用户间的基础隔离，**所有数据（含 API 密钥）明文存储**——官方明示「不要公网部署」（[multi-user 文档](https://docs.sillytavern.app/administration/multi-user/)）。
- 服务端缓存目录 `data/_cache`（tokenizer、transformers.js 模型；`performance.useDiskCache` 开启时 `_cache/characters` 存解析后角色数据）——可再生、不应纳入备份核心（[Administration 数据布局](https://docs.sillytavern.app/administration/)）。
- 兼容重定向：需要时（扩展、全尺寸角色卡、用户图片上传等）服务器会自动从数据目录托管用户文件——即 `public/` 下部分 URL 会透明指向数据目录。

---

## 5. 配置与密钥文件

- **两层配置**：[settings/config 管理（DeepWiki）](https://deepwiki.com/SillyTavern/SillyTavern/5.3-settings-and-configuration-management)：
  - `config.yaml`：服务器级只读运行配置（`dataRoot`、`listen`、`whitelistMode`/`whitelist`、`enableUserAccounts`、`backups.chat.*` 等）；环境变量 `SILLYTAVERN_*` 可覆盖（嵌套用下划线，数组/对象 JSON 化），文档见 [config-yaml](https://docs.sillytavern.app/administration/config-yaml/)（中文镜像 [yuanhuakk/sillytavern-docs-zh](https://github.com/yuanhuakk/sillytavern-docs-zh/blob/f3a5c74f52fc800af86eb4416a650f9d6f0b285a/Administration/config-yaml.md)）。
  - `settings.json`：用户级可变设置（UI 偏好、`power_user` 对象、扩展设置、personas 等）。
- `secrets.json`：API 密钥等敏感信息（明文，见 4；规则 2：**默认不上传**，仅本地备份）。
- `stats.json`：使用统计，属用户数据，随备份。

---

## 6. 聊天记录（.jsonl）与完整性

来源：[Chat Storage and Persistence（DeepWiki 5.2）](https://deepwiki.com/SillyTavern/SillyTavern/5.2-chat-storage-and-persistence)、[1.14.0 发布说明](https://github.com/SillyTavern/SillyTavern/releases/1.14.0)、[消息操作与分支检查点（实测记录）](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/E2_%E6%B6%88%E6%81%AF%E6%93%8D%E4%BD%9C%E4%B8%8E%E5%88%86%E6%94%AF%E6%A3%80%E6%9F%A5%E7%82%B9.md)。

- **首行是 header**：`{"chat_metadata": {...}, "user_name": "(legacy)", "character_name": "(legacy)"}`，以 `chat_metadata` 键识别；后两字段是遗留占位。
- `chat_metadata` 已知字段：`main_chat`（分支/检查点中指向源聊天文件名）、`integrity`（**1.18+ 引入的 UUID 完整性标识**）、`note_prompt`/`note_interval`/`note_position`（Author's Note）、`variables`（本地变量）等。
- **完整性机制**：保存时客户端回传 integrity slug，服务器 `readFirstLine` 比对，不一致且开启校验时拒绝写入（防多标签页互相覆盖）。1.19.0 起：**header 无法解析时不再静默覆盖**、末行损坏时提供降级预览、新分支/检查点生成新 integrity 标识、非 ASCII 聊天名使用独立备份键（[1.19.0 发布说明](https://github.com/SillyTavern/SillyTavern/releases/latest)）。此前存在分支继承父级 integrity 的 bug（[Issue #5942](https://github.com/SillyTavern/SillyTavern/issues/5942)，1.18 起修复）。
- **消息结构**：`name/is_user/is_system/send_date/mes/swipes/swipe_id/extra{api, model, token_count, hidden, …}`；`extra.hidden`（/hide）与 `is_system`（/sys、/comment）语义不同；`tool_invocations` 记录工具调用；删除消息会连带删除关联工具调用消息（1.19.0）。
- **附件**：文件附件存于用户数据目录，经 **`extra.media`** 在 JSONL 中引用（DeepWiki 5.2）。**1.14.0 起附件处理不向后兼容**：一条消息可挂多文件/多图片、支持音频附件、Gemini/OpenRouter 音频内联（[1.14.0 发布说明](https://github.com/SillyTavern/SillyTavern/releases/1.14.0)）。
- **存储目录**：`chats/<角色名>/…`、`group chats/`、自动备份 `backups/`（`config.yaml` 的 `backups.chat.enabled/throttleInterval/maxTotalBackups`，节流写、进程退出时 flush）；写入用 `write-file-atomic` 保证原子性。
- 导入规范化：支持 Oobabooga / Agnai / CAI Tools / Kobold Lite 等外部聊天格式转换（同上来源）。

---

## 7. 向量数据库 / Embedding 与附件图片存储

### 7.1 向量库
来源：[Vector Storage and RAG System（DeepWiki 6.3）](https://deepwiki.com/SillyTavern/SillyTavern/6.3-vector-search-and-embeddings)、[Chat Vectorization 官方文档](https://docs.sillytavern.app/extensions/chat-vectorization/)、[Data Bank（RAG）官方文档](https://docs.sillytavern.app/usage/core-concepts/data-bank/)。

- 实现：`vectra` 库，本地 JSON 索引；存储路径 **`DATA_ROOT/vectors/<source>/<collectionId>/<model>/`**，按用户/来源/集合（聊天 id 或文件 URL 哈希）/模型分区；条目含向量 + 元数据（原文、哈希、位置）。
- 能力：聊天消息 RAG、Data Bank 文件向量化、World Info 语义激活；默认 embedding 为本地 transformers `Xenova/all-MiniLM-L6-v2`，另有 OpenAI/Ollama/llama.cpp/SiliconFlow/Cohere 等 20+ 提供商；消息按 400 字符分块（可配）。
- 结论：向量文件是**可再生**的派生数据（删除后重算），但重算有成本（尤其远端 embedding）——备份策略建议：默认随备份、标注「可再生」，可选排除（见建议 P2-7）。

### 7.2 附件与图片存储
来源：[Asset and File Management（DeepWiki 5.4）](https://deepwiki.com/SillyTavern/SillyTavern/5.4-assets-and-file-management)。

用户目录资产布局（`data/{user_handle}/` 下）：
- `characters/`：角色卡 PNG；`characters/<角色名>/` 为精灵图/表情子文件夹；
- `backgrounds/`：聊天背景图；`assets/`：`bgm/ ambient/ blip/ live2d/ vrm/ character/ temp/`；
- `images/`：用户上传画廊图片；`thumbnails/`：生成缩略图（`bg/ avatar/ persona/`）；
- `files/`：Data Bank 附件（PDF/HTML/Markdown/EPUB/Office 有内置文本提取）。

- 上传 API `POST /api/images/upload`（base64 + `format` 小写无点扩展名）；允许媒体扩展名清单（`MEDIA_EXTENSIONS`）：`bmp png jpg webp jpeg jfif gif mp4 avi mov wmv flv webm 3gp mkg mpg mp3 wav ogg flac aac m4a aiff`（[错误码文档](https://errors.standardbeagle.com/SillyTavern/SillyTavern/invalid-image-format/)、[no-image-data](https://errors.standardbeagle.com/SillyTavern/SillyTavern/no-image-data-provided/)）。
- 文件名白名单（字母数字 `_ - .`）、禁危险扩展、`sanitize-filename`、隐藏文件禁止（DeepWiki 5.4）——我们扫描时对异常文件名仍应原样保留+告警，不做任何执行。

---

## 8. 对现有迁移适配器的影响评估（对照 `src/continuity/adapters/sillytavern.py`）

| # | 适配器现状（代码） | 上游最新事实 | 影响等级 |
|---|---|---|---|
| 1 | 只读 `chara` 块（`CHARA_KEY`），无 `ccv3` | V3 PNG 双块、优先 `ccv3`；可仅存 `ccv3` | **高**：V3 PNG 报「缺少 chara 块」或读到 V2 降级副本 |
| 2 | `parse_card_dict` 仅认 `chara_card_v2` 前缀 | V3 JSON 是合法常见输入 | **高**：V3 卡落入 V1 平铺分支，字段全空且导出损坏 |
| 3 | `CARD_FIELDS` 无 V3 字段 | V3 新增 7 类字段 | 中：未知字段虽保留在 raw，但「已知字段」清单过时 |
| 4 | 无 `.charx` 识别（`FileKind` 缺项） | CHARX 是 V3 官方载体 | 中：`unknown` 类型原样保留（不丢数据），但无法诊断/迁移 |
| 5 | 无数据目录布局概念（不知道 `dataRoot`/`default-user`/多用户） | 1.12.0+ 全部数据在新布局 | **高**：对新版安装扫描不到 `chats/characters/settings.json` 等 |
| 6 | JSONL 把 header 当消息 | header 含 `chat_metadata`（integrity/main_chat/note_*） | 中：透传不丢数据，但分支/检查点、完整性标识未暴露，修复预览无法提示 |
| 7 | 无附件引用追踪 | `extra.media`/`image`/`audio` 引用数据目录文件；1.14+ 不兼容旧版 | 中：附件缺失检测（基线未解决问题 2）仍无头绪 |
| 8 | 扫描范围未含 settings/stats/secrets/vectors/thumbnails/images/files/assets | 均为用户数据目录组成部分 | 中：备份不完整；secrets 需遵守规则 2 |
| 9 | World Info 结构判断 `entries`+`character_book` | 顶层 lorebook 结构未变；V3 规范化了 lorebook 条目字段（`scan_depth`、`token_budget` 等） | 低：现有判断仍成立，条目内部字段原样保留即可 |

---

## 9. 建议更新点清单（仅建议，不实施；优先级排序）

### P0（正确性，先于一切）
1. **识别 V3 角色卡**：`spec == "chara_card_v3"`（`spec_version` 按浮点解析，高于 3.0 时告警但导入——规范要求）；PNG 读取改为**优先 `ccv3` 块、回退 `chara` 块**（大小写不敏感）；`ParsedCard.format_version` 增加 `"v3"`。修复「V3 被误判 V1 平铺 → 导出损坏」的实际缺陷。
2. **`CARD_FIELDS` 扩充 V3 字段清单**：`assets, nickname, creator_notes_multilingual, source, group_only_greetings, creation_date, modification_date`；并注意 V3 校验极宽松（仅 `data` 是对象），字段缺失**不是**损坏证据。
3. **数据目录布局感知**：支持「旧 `public/` 布局」与「1.12+ `dataRoot`（`config.yaml` 读取 + `--dataRoot` 不可知时按默认 `./data`）→ `data/[user-handle]/`」双布局自动检测；多用户句柄枚举（`[a-z0-9-]` 规则）；扫描目标扩展到 `chats/ characters/ worlds/ groups/ group chats/ settings.json stats.json secrets.json instruct/ context/ QuickReplies/ themes/` 等迁移指南清单中的目录。
4. **CHARX 识别**：zip 中央目录校验 + 根 `card.json` 存在性 → 新增文件类型（如 `character_card_charx`）；资产仅登记 `embeded://` 清单与 `assets/` 内文件，**绝不执行/渲染**（规则 3）；损坏/加密 zip → 同 `corrupt_png` 的 R2/R3 处理策略。`chara-ext-asset_` PNG 块同理只登记。

### P1（完整性，建议随 P0 一起规划）
5. **JSONL header 识别与 `chat_metadata` 暴露**：首行含 `chat_metadata` 即 header；暴露 `integrity/main_chat/note_*` 到解析结果与修复预览；`main_chat` 非空视为分支/检查点，在迁移清单中记录父子关系。修复副本的 `integrity` 处理属 R1（需创始人/用户确认：保留原值还是仿 ST 为新副本生成新标识），不得静默改写（对照 1.19「header 无法解析不再静默覆盖」的精神）。
6. **附件引用追踪**：解析 `extra.media`（及遗留 `image`/`audio` 字段）中引用的文件名，映射到用户目录 `images/ files/ characters/<名>/ backgrounds/ assets/`；备份时包含被引用文件；缺失附件 → R2 建议（不可伪造，规则 4）。**先用 1.14+ 真实样本验证字段结构再写代码**（规则 9；1.14 格式不兼容旧版，官方只给方向，无逐字段文档）。
7. **导出策略**：V3 输入默认原样透传（保持 `chara_card_v3` + `ccv3`）；若 MVP 只支持 V2 导出，必须在报告与 UI 中明确「V3 降级为 V2」警告（对照规范：降级副本应加 creator_notes 警告语）。CHARX 导出不做（R2 建议），导入即可。

### P2（备份范围与文档，可随后续样本补充）
8. **备份范围分类**：`vectors/` 与 `thumbnails/`、`data/_cache` 归为「可再生派生数据」——默认随备份并标注，供用户选择排除；`secrets.json` 原样本地复制但**默认不上传**（规则 2），是否本地加密备份由创始人决策。
9. **样本库扩充**（规则 9，先样本后实现）：V3 JSON 卡、含 `ccv3` 的 PNG 卡、CHARX 包（含多资产）、1.14+ 多附件聊天、分支/检查点 JSONL、1.12+ 数据目录快照、多用户布局快照。对应更新 `format-compatibility.md` 矩阵——**该文件不在本会话写作用域，须经创始人协调**。
10. **群聊关联校验**：`group chats/` 下 JSONL 与 `groups/` 成员清单的一致性检查可列入 R2 建议项。

---

## 10. 主要来源

- SillyTavern 官方仓库/发布页：[releases/latest（1.19.0）](https://github.com/SillyTavern/SillyTavern/releases/latest)、[1.14.0 发布说明](https://github.com/SillyTavern/SillyTavern/releases/1.14.0)、[Issue #5942（integrity 分支 bug）](https://github.com/SillyTavern/SillyTavern/issues/5942)
- 官方文档：[1.12.0 迁移指南](https://docs.sillytavern.app/installation/st-1.12.0-migration-guide/)、[多用户](https://docs.sillytavern.app/administration/multi-user/)、[数据布局](https://docs.sillytavern.app/administration/)、[Chat Vectorization](https://docs.sillytavern.app/extensions/chat-vectorization/)、[Data Bank](https://docs.sillytavern.app/usage/core-concepts/data-bank/)、[config-yaml](https://docs.sillytavern.app/administration/config-yaml/)
- 角色卡规范：[V2 spec](https://github.com/malfoyslastname/character-card-spec-v2/blob/main/spec_v2.md)、[V3 spec（kwaroran）](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md)、[character-cards-v2 README](https://github.com/bradennapier/character-cards-v2/blob/main/README.md)
- 源码级/实测参考：[DeepWiki 5.2 聊天存储](https://deepwiki.com/SillyTavern/SillyTavern/5.2-chat-storage-and-persistence)、[DeepWiki 5.4 资产](https://deepwiki.com/SillyTavern/SillyTavern/5.4-assets-and-file-management)、[DeepWiki 6.3 向量](https://deepwiki.com/SillyTavern/SillyTavern/6.3-vector-search-and-embeddings)、[TavernWeave A2（PNG 读写机制实测）](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/A2_%E8%A7%92%E8%89%B2%E5%8D%A1%E6%A0%BC%E5%BC%8F%E8%A7%84%E8%8C%83.md)、[TavernWeave E2（消息与分支实测）](https://github.com/liarmttt/tavernweave/blob/f9863d2b05305457fe9ed8b0c5688d52aca400a5/skills/consult-tavernweave-library/references/st-guides/E2_%E6%B6%88%E6%81%AF%E6%93%8D%E4%BD%9C%E4%B8%8E%E5%88%86%E6%94%AF%E6%A3%80%E6%9F%A5%E7%82%B9.md)
- 其他：[MEDIA_EXTENSIONS 错误文档](https://errors.standardbeagle.com/SillyTavern/SillyTavern/invalid-image-format/)、[1.17.0 发布记录](https://newreleases.io/project/github/SillyTavern/SillyTavern/release/1.17.0)

> 说明：DeepWiki、TavernWeave 等为第三方源码级整理，字段级结论已尽量交叉多源；
> 涉及「待样本验证」处务必以真实样本为准后再动代码（AGENTS.md 规则 9）。
