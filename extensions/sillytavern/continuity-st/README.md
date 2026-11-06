# Continuity 体检（Continuity Check）— SillyTavern Extension

> Status: **P1 skeleton**（骨架版）。Complete bilingual install/usage docs and final privacy
> statement land in **P4**（TODO-P4 标记处为待补内容）。
> 状态：**P1 骨架版**。完整中英双语安装/使用文档与最终隐私声明在 **P4** 补齐（TODO-P4 标记处为待补内容）。

## Installation · 安装（占位，P4 完善 · TODO-P4）

English（placeholder）: copy this folder into your SillyTavern extensions directory
(`data/<user-handle>/extensions/continuity-st/` or `public/scripts/extensions/third-party/continuity-st/`),
then enable it in the Extensions panel. Requires SillyTavern ≥ 1.12.0.

中文（占位）：将本文件夹放入 SillyTavern 扩展目录（`data/<用户句柄>/extensions/continuity-st/`
或 `public/scripts/extensions/third-party/continuity-st/`），在扩展管理面板启用。要求 SillyTavern ≥ 1.12.0。

## Privacy Statement · 隐私声明（占位，P4 完善 · TODO-P4）

English（placeholder）: this extension only reads in-memory data inside your SillyTavern page;
it never writes files, never uploads anything, never touches API keys, and never makes network
requests to hosts other than `127.0.0.1` (your local Continuity Studio Web UI).

中文（占位）：本扩展只读取 SillyTavern 页面内的内存数据；绝不写文件、绝不上传任何内容、绝不接触
API 密钥；除 `127.0.0.1`（本机 Continuity Studio 本地 Web UI）外，绝不向任何地址发起网络请求。

## Features · 功能

| Stage · 阶段 | Feature · 功能 |
|---|---|
| P1（current · 当前） | Skeleton: version badge + empty panel · 骨架：版本徽标 + 空面板 |
| P2 | In-memory health checks (H1–H6) · 内存态一键体检（H1–H6） |
| P3 | Launch local Web UI (127.0.0.1:8777) + `/continuity` slash command · 一键唤起本地 Web UI + slash 命令 |
| P4 | Polish, i18n docs, official-listing readiness · 打磨、双语文档、官方收录准备 |

## License · 许可证

MIT
