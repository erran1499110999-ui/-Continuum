# 合成样本（synthetic samples）

由 `make_samples.py` 生成的**合成**测试数据，不含任何真实用户数据。

- `st_card.json` / `st_card.png`：角色卡（V2 结构占位；PNG 带 tEXt `chara` 块）
- `st_chat.jsonl`：聊天记录 JSONL
- `st_worldinfo.json`：World Info / Lorebook 结构占位
- `broken_trailing_comma.json`：损坏样本（末尾多余逗号）
- `unknown.bin`：未知二进制样本

生成：`python samples/synthetic/make_samples.py`（输出目录已加入 .gitignore）。

真实样本（经授权、脱敏）将由创始人收集后加入回归测试库，不放入本仓库。
