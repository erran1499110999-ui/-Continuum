# P5 验收清单 — 插件可行性闭环联合交付（developer + frontend-developer，创始人严格模式）

> 审核方：qa-reviewer（与两开发者严格分离，独立判定）
> 审核时间：2026-11-07 02:20–02:45
> 审核范围：后端 `src/continuity/webui/{api.py,server.py}`（ping/backup/emergency-backup/restore 四端点）+ 插件 `extensions/sillytavern/continuity-st/index.js`（ping 探测 + 深链三按钮）+ 前端 `static/{app.js,index.html,style.css}`（hash 路由 + 三引导页）+ 测试 `tests/test_webui_api_backup.py`（22 例新增）+ `tests/test_webui_frontend_static.py`（+15 例）
> 依据：AGENTS.md（最新版）、docs/plugin-viability-plan.md、TEAM-COORDINATION.md 三方写作用域
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查 + 注释审查」

### 1.1 真实运行

| 运行 | 结果 |
|------|------|
| node:test（沙箱替代方式） | **24/24 通过**（QA 亲自复跑） |
| 全套 pytest（AGENTS.md 固化命令） | **401 collected = 400 passed + 1 skipped, 1 warning, 33.56s，退出码 0**——364 基线保持 + developer 22 例（test_webui_api_backup.py）+ frontend 15 例新契约 ✓ |

### 1.2 后端四端点逐行审查（api.py + server.py）

| 审查项 | 实现 | 判定 |
|--------|------|------|
| ping 零指纹 | `ping()` 仅返回 `{"status":"ok"}`；docstring 明确「绝不携带版本号/工具名等指纹」——实现与注释一致 | ✓ |
| 引擎复用而非重写 | `backup_worker`→`create_backup`、`restore_worker`→`restore_backup`、`emergency_backup_worker`→`create_backup`+`verify_bundle`——薄壳不重写逻辑，注释明示引擎保证 | ✓ |
| emergency 的 verify 联动 | 备份完成后立即 `verify_bundle` 自检（「急救要的是『现在就能恢复』」），结果含 verify{ok/checked/mismatches/missing/extra_files/warnings} | ✓ |
| restore 原子性 | 复用引擎「预校验 + 临时目录 + 原子发布」；worker 注释明确 dest 必须不存在、失败清理临时结果 | ✓ |
| validation 预检 | `_handle_backup`：require_source_dir + require_new_output_dir(bundle, source)；`_handle_emergency_backup`：source + output 同规则；`_handle_restore`：require_source_dir(bundle) + require_new_output_dir(dest, source=bundle) | ✓ |
| 统一提交映射 | `_submit_job` 统一 409（JobsBusy）/503（JobsError）/202（重构自 _handle_scan 内联逻辑，行为等价） | ✓ |
| ping 免 token 前置 | `/api/ping` 在 `_token_ok()` 之前分发；注释「Host 白名单与安全头仍在 _route 中先行生效；不加 CORS 头」——与实现一致 | ✓ |

### 1.3 插件 P5 逐行审查（index.js）

| 审查项 | 实现 | 判定 |
|--------|------|------|
| ping 探测 | `new Image()` 加载 `http://127.0.0.1:<port>/api/ping`——注释说明选择 Image() 而非 fetch（不需读响应体/不需 CORS）与实现一致 | ✓ |
| 深链三按钮 | emergency→`#emergency?auto=1`、backup→`#backup?auto=1`、**restore→`#restore`（无 auto=1）**；注释「恢复目标目录必须由用户人工确认」与实现一致 | ✓ |

### 1.4 前端 P5 逐行审查（app.js hash 路由）

| 审查项 | 实现 | 判定 |
|--------|------|------|
| hash 路由 | `HASH_PAGES = {emergency, backup, restore}`；`routeFromHash` + `hashchange` 监听 + 初始化调用；兼容 `#emergency` 与 `#w=emergency&auto=1` 两种写法 | ✓ |
| auto 白名单 | `auto` 正则解析 `auto=1`；**`if (auto && name !== "restore")`**——restore 明确排除；L487「restore 分支刻意不存在：任何情况下都不自动执行恢复」 | ✓ |
| 空目录不提交 | 自动开始仅当「所有必填目录都已填写」才提交（L464 注释与实现一致） | ✓ |
| 三引导页 | wireGuide("emergency"/"backup"/"restore") + 各自 endpoint/字段（emergency{source,output}、backup{source,bundle}、restore{bundle,dest}）| ✓ |

### 1.5 注释审查（新增中文注释与实现一致）

- api.py 各 worker docstring（引擎复用/verify 联动/原子性）与实现逐一比对一致 ✓
- server.py ping 免 token 注释（Host 先行/无 CORS）与 _route 顺序一致 ✓
- app.js 头部 P5 说明（深链三页/端点清单/auto 白名单）与实现一致 ✓
- 插件深链注释（auto=1 语义 Q13）与代码一致 ✓
- **无错误/过时/误导注释。**

### 1.6 与上一轮（P4）比较

- P4 的 51 例插件契约全部保留；本轮新增 37 例（后端 22 + 前端 15）全部真实断言（ping 零指纹、三端点全流程含真实备份/恢复/verify、深链路由、auto 白名单、restore 无自动）✓
- 无新增问题。

**第 1 轮结论：功能与真实测试通过（401=400+1、node 24/24 均 QA 复跑）；三方代码逐行正确；注释全一致。**

---

## 第 2 轮「安全与十规则审计 — 真实执行」

| # | 检查项 | 真实执行结果 | 判定 |
|---|--------|--------------|------|
| B1 | ping 响应体严格零指纹 | 独立实证：`GET /api/ping` → 200，body **精确等于 `{"status": "ok"}`**（无 version/工具名） | ✓ |
| B2 | Host 白名单仍拦截 ping | 实证：`ping` + `Host: evil.example` → **400**（_route 先行生效） | ✓ |
| B3 | 三 POST 端点无 token 403 | 实证：backup/emergency-backup/restore 无 token 全部 **403 TokenError** | ✓ |
| B4 | restore 深链无 auto=1（双侧契约） | 插件 L209 `hash = "#restore"`（无参数）+ 前端 L487/L502 双重排除（`auto && name !== "restore"`） | ✓ |
| B5 | auto 白名单仅 emergency/backup | 前端白名单判定 + 伪造 `#restore?auto=1` 被 restore 排除逻辑拒绝（反证 P3） | ✓ |
| B6 | 前端结果渲染 textContent | app.js 渲染沿用 textContent 纪律（无 innerHTML/eval，改版时已锁定契约） | ✓ |
| B7 | 零新外部资源 | 插件唯一外部 URL 仍为 127.0.0.1（ping + 深链均拼端口）；前端无新外源 | ✓ |
| B8 | 投毒反证 3 组 | ① 插件深链投毒为外部域 → 检出；② 注入密钥字段 `name="token"` → 检出；③ 伪造 `#restore?auto=1` → restore 排除逻辑拒绝自动开始 | ✓ 全 PASS |

### 十条规则逐条

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓ | backup/emergency 复用引擎（源只读 + bundle 必须新目录）；restore dest 必须不存在 |
| 2 默认不上传 | ✓ | 零新外部资源（B7）；ping 零指纹不泄露 |
| 3 不执行导入内容 | ✓ | textContent 渲染（B6） |
| 4 R0–R3 只归引擎 | ✓ | 深链流程不产生任何判定，全部交引擎 |
| 5 动作日志与差异 | ✓ | 三 worker 均有统计 log；emergency 附 verify 自检报告 |
| 6 不删测试/注释强制 | ✓ | 364 基线保持 + 37 例新增；注释一致（1.5） |
| 7 先计划阶段停等 | ✓ | plugin-viability-plan 先行；停等审核 |
| 8 无 NFT/代币/钱包/云端 | ✓ | grep 0 命中 |
| 9 格式不确定不猜测 | ✓ | ping 零指纹；前端只透传引擎结论 |
| 10 未运行不标通过 | ✓ | 401 例 + node 24/24 + 攻击实证均 QA 本轮真实执行 |

### 与第 1 轮结论比较

- 第 1 轮静态结论经 6 项真实攻击实证 + 3 组投毒反证全部确认；无新增漏洞、无退回项。

**第 2 轮结论：安全与十规则审计通过（ping 零指纹实证、Host/token 拦截、restore 永不自动双侧锁定）。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归核对

- 401 collected = 400 passed + 1 skipped（真实运行）：364 基线无删减 + 37 例新增 ✓；node 24/24 ✓
- 无删除/无降低/无硬编码：37 例均为真实断言（含真实备份包创建、真实恢复哈希校验、真实 verify 篡改反例——测试文件通读确认）

### 3.2 git 写作用域核对（三方，只读命令）

- developer 名下：`M src/continuity/webui/{api.py,server.py}`、`M extensions/sillytavern/continuity-st/{index.js,style.css}`、`M tests/test_st_plugin_static.py`、`?? tests/test_webui_api_backup.py` ✓
- frontend-developer 名下：`M static/{app.js,index.html,style.css}`、`M tests/test_webui_frontend_static.py`、`M docs/frontend-redesign-delivery.md` ✓
- researcher/lead 名下：business-feed/live-resource-feed/skeptical-review/plugin-viability-plan/product-useless-diagnosis ✓
- **三方均无越界**（无互相触碰、无动他人文件）✓；无 commit（等三轮结论）✓

### 3.3 联调一致性（插件深链 ↔ 前端路由 ↔ 后端端点三方契约）

| 链路 | 插件 | 前端 | 后端 | 一致性 |
|------|------|------|------|------|
| emergency | `#emergency?auto=1` | 路由 emergency + 自动提交（目录已填） | `/api/jobs/emergency-backup` {source,output} | ✓ 三方参数全一致 |
| backup | `#backup?auto=1` | 路由 backup + 自动提交（目录已填） | `/api/jobs/backup` {source,bundle} | ✓ |
| restore | `#restore`（无 auto） | 路由 restore + **永不自动** | `/api/jobs/restore` {bundle,dest} | ✓ |
| 探测 | `Image()` → `/api/ping` | — | `/api/ping` 免 token 零指纹 | ✓ |

### 3.4 差距清单

| # | 差距 | 属性 |
|---|------|------|
| G1 | 真机验收（插件三按钮在真实 ST 中触发深链、ping 探测、恢复人工确认流程） | 待创始人（沙箱无浏览器/ST） |
| G2 | 市场验证四条件数据（沿用 validation-verdict 结论，投放仍冻结） | 待创始人 |

### 3.5 发布准备核查

- ping 端点零指纹（防端口探测泄露软件版本）✓；restore 永不自动（防误覆盖，与规则 1 精神一致）✓；emergency 带可恢复性自检 ✓

### 与第 2 轮结论比较

- 第 3 轮新增：三方联调一致性逐参数核对（全一致）、三方写作用域核对（无越界）、G1/G2 差距；无新增退回项。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 + 注释审查 | 通过（401=400+1、node 24/24；三方代码正确；注释全一致） |
| 第 2 轮 安全与十规则审计（真实执行 + 投毒反证 3 组） | 通过（ping 零指纹实证、restore 永不自动双侧锁定） |
| 第 3 轮 回归与发布审查 | 通过（基线无删减、三方无越界、联调参数三方一致） |

### 退回项：**无**

### 观察/建议（非阻塞）

- G1 真机项请创始人按 plugin-viability-plan 验收清单执行（三按钮触发/探测/恢复确认流程）；
- G2 市场验证四条件维持（validation-verdict 结论不变，投放继续冻结）。

**一句话验收建议**：P5 联合交付三轮全部通过、无退回项——四端点引擎复用与预检正确、ping 零指纹实证、restore 永不自动双侧契约锁定、三方深链参数一致；可交创始人验收（真机 G1），通过后 commit。
