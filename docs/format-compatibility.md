# 格式兼容矩阵（初始版，2026-11-06）

> 原则（AGENTS.md 规则 9）：只依据可验证的结构特征判断，不猜测字段含义；
> 未知字段一律原样保留。本矩阵随真实样本积累持续更新。

## 文件类型识别（scanners/filetype.py）

| 文件类型 | 识别依据 | 识别结果 | 置信度 | 说明 |
|---|---|---|---|---|
| PNG 角色卡 | PNG 魔数 + tEXt `chara` 块 | character_card_png | 高（块存在即可验证） | 适配器已实现块内容解析（base64 JSON，V1/V2） |
| 损坏/截断 PNG | PNG 魔数但块边界、CRC 或 IEND 校验失败 | corrupt_png + 警告 | 高（结构校验） | 报告 R2 建议从备份恢复；迁移时明确报错，不猜测内容 |
| 角色卡 JSON | 合法 JSON 且含 `name`+`first_mes`，或 `spec` 以 `chara_card` 开头 | character_card_json | 高（结构特征） | V1 平铺 / V2 包裹均已支持解析与导出 |
| 聊天 JSONL | 抽样前 20 行中多数（≥半数且≥2 行）为合法 JSON | chat_jsonl | 中（启发式） | 容忍个别损坏行；损坏行跳过、告警，原始字节保留至 bad-lines sidecar |
| World Info / Lorebook | 合法 JSON 且含 `entries` 与 `character_book` 对象 | json | 高（结构特征） | 迁移时原样保留全部字段 |
| 其他合法 JSON | 可被 json 解析 | json | 高 | 具体类型待定 |
| 疑似损坏 JSON | 以 `{` 开头但无法解析 | text + 警告 | 高（异常检测） | 修复引擎已实现：末尾多余逗号 → R0-001 自动修复；其余（截断等）→ R2 仅建议，从备份恢复 |
| 纯文本 | UTF-8 可解码 | text | — | 编码检测仅支持 UTF-8 |
| 二进制 | 头部含 NUL 字节 | binary | — | 隔离，不执行 |
| 空文件 | 大小 0 | text + 提示 | 高 | 提示用户确认是否占位 |
| 未知 | 其他 | unknown | — | 原样保留，不猜测 |

## 未解决问题（待样本与研究确认）

1. R1 可推断修复规则（PNG 元数据与同名 JSON 比对等）——需真实样本设计。
2. 聊天 JSONL 中附件（图片/音频）的内嵌引用方式与缺失附件检测。
3. 角色卡 V1/V2 差异字段的完整清单（extensions 等）——需真实样本扩充。
4. RisuAI 等第二个客户端适配器。
5. UTF-16 / GBK 等非 UTF-8 编码文本的识别与转换。
