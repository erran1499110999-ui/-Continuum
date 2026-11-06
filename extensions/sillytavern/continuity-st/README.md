# Continuity 体检（Continuity Checkup）— SillyTavern Extension

> **CN**：Continuity 体检：酒馆内的一键内存体检。深度检查、备份、恢复与迁移请打开本地 Web UI——数据不出你的电脑。
> **EN**: "Continuity Checkup: a one-click, read-only health peek inside the tavern. For deep scans,
> backups and migration open the local Web UI — your data never leaves your machine."

**Status · 状态**：P4 ready for release · P4 上市就绪（P1 骨架 / P2 内存态体检 / P3 唤起与入口 / P4 打磨与收录准备 均已完成）。

---

## Installation · 安装

**EN**
1. Copy this folder (`continuity-st/`) into your SillyTavern extensions directory:
   `data/<user-handle>/extensions/continuity-st/`
   (or the global path `public/scripts/extensions/third-party/continuity-st/`).
2. Open **Extensions** in SillyTavern, find 「Continuity 体检」 and tick it to enable.
3. (Optional) open the extension's settings drawer to change the local Web UI port or hint display.

**中文**
1. 将本文件夹（`continuity-st/`）放入 SillyTavern 扩展目录：
   `data/<用户句柄>/extensions/continuity-st/`
   （或全局路径 `public/scripts/extensions/third-party/continuity-st/`）。
2. 打开 SillyTavern 的「扩展」面板，勾选启用「Continuity 体检」。
3. （可选）在扩展设置抽屉中修改本地 Web UI 端口与提示显示。

## Usage · 使用说明

| Feature · 功能 | How · 用法 |
|---|---|
| 一键体检（内存态，只读）· In-memory health check | Click the badge (bottom-right) → 「开始体检（内存态）」· 点击右下角徽标 →「开始体检（内存态）」 |
| 打开本地 Web UI · Launch local Web UI | Panel button opens `http://127.0.0.1:<port>/` in a new tab (default port 8777). If the page doesn't open, run `python -m continuity.webui` first. · 面板按钮在新标签打开 `http://127.0.0.1:<端口>/`（默认 8777）。若页面未打开，请先运行 `python -m continuity.webui`。 |
| Slash command | Type `/continuity` in the chat input to open the panel and run a check · 在聊天输入框输入 `/continuity` 打开面板并执行一次体检 |
| Settings · 设置 | Web UI port (default 8777) + hint display toggle, persisted via SillyTavern's extension settings · Web UI 端口（默认 8777）与提示显示开关，经 SillyTavern 扩展设置持久化 |

**Health checks (memory-only, read-only) · 体检项（内存态、只读）**：H1 integrity 缺失提示 ·
H2 疑似被重置的聊天 · H3 同名不同内容角色卡 · H4 当前卡关键字段缺失 · H5 消息结构异常。
All findings are **hints**, never repair verdicts — R0/R1/R2/R3 judgments come only from the Python engine
in the local Web UI. 全部为「内存态初步提示」，绝不产出修复等级判定——R0/R1/R2/R3 结论只由本地 Web UI 的 Python 引擎给出。

## Privacy Statement · 隐私声明

**EN**：This extension is read-only and in-memory: it never writes files, never collects, stores or
uploads anything, never touches API keys, and never makes network requests to any host other than
`127.0.0.1` (your own machine). No telemetry, no ads, no cloud.

**中文**：本扩展只读、仅内存：绝不写文件，不收集、不存储、不上传任何数据，绝不接触 API 密钥；
除 `127.0.0.1`（本机）外绝不向任何地址发起网络请求。无遥测、无广告、无云端。

## Compatibility · 兼容性声明

- Requires SillyTavern ≥ **1.12.0** (`minimum_client_version` in manifest). If the extension reports
  missing capabilities, please upgrade SillyTavern first. 要求 SillyTavern ≥ **1.12.0**（manifest 的
  `minimum_client_version`）。如插件提示能力缺失，请先升级 SillyTavern。
- Built only on `SillyTavern.getContext()` + browser-native APIs, with capability detection and
  graceful fallbacks; no dependency on staging events or internal modules, verified against the
  latest release. 只依赖 `SillyTavern.getContext()` 与浏览器原生 API，全部能力检测 + 降级提示；
  不依赖任何 staging 事件或内部模块，并随最新 release 复验。
- This is a **thin shell**（薄壳）：the plugin is an entry point, not the engine — deep scans,
  backups, restore, repair and migration live in the local Web UI (Continuity Studio).
  插件是入口不是引擎——深度体检、备份、恢复、修复与迁移都在本地 Web UI（Continuity Studio）完成。

## Official-listing compliance · 官方收录要求自查

Per `docs/st-launch-plan.md` §1 (SillyTavern official "Writing Extensions" requirements):

| Official requirement · 官方要求 | Implemented · 落实 |
|---|---|
| Open source + free license · 开源 + 自由许可证 | **MIT**（manifest 与本文档双写） |
| Compatible with latest release · 兼容最新 release | capability detection + minimum_client_version + per-release smoke plan · 能力检测 + 版本门槛 + 每 release 冒烟计划 |
| Complete README · README 完整 | This bilingual README（安装/使用/功能/隐私/兼容）· 本双语文档 |
| No server-plugin dependency · 不依赖 server 插件 | Pure UI extension · 纯 UI 扩展 |
| Official best practices · 官方最佳实践 | getContext() only, textContent rendering, zero keys in extensionSettings · 只用 getContext()、textContent 渲染、设置零密钥 |

## License · 许可证

MIT

---

Continuity Studio · Local-first · 数据不出你的电脑
