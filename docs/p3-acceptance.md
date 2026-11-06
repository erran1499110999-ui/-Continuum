# P3 验收清单 — ST 插件唤起与入口模块（developer 交付三轮独立审核，创始人严格模式）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定）
> 审核时间：2026-11-07 01:46–02:10
> 审核范围：`extensions/sillytavern/continuity-st/{index.js,settings.html,style.css,README.md}` + `tests/test_st_plugin_static.py`（44→48 例）
> 依据：AGENTS.md（最新版）、docs/TEAM-COORDINATION.md、docs/st-plugin-plan.md 第 4 节 P3 行与 6.2 真机验收清单、docs/research-st-plugin.md
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查 + 注释审查」

### 1.1 真实运行

| 运行 | 结果 |
|------|------|
| node:test（沙箱替代方式 `node <file>`） | **24/24 通过**（tests 24 / pass 24 / fail 0，QA 亲自复跑） |
| 全套 pytest（AGENTS.md 固化命令） | **361 collected = 360 passed + 1 skipped, 1 warning, 22.68s，退出码 0**——357 基线保持 + 4 例新增契约全过 ✓ |

### 1.2 index.js P3 新增代码逐行审查（对照计划）

| 审查项 | 实现 | 判定 |
|--------|------|------|
| 按钮端口读取 | `getSettings()`：`extensionSettings["continuity-st"].webuiPort`，校验 `typeof number && Number.isInteger && >0 && <65536`（即 1–65535），越界/缺失回退默认 8777 | ✓ |
| window.open 参数 | `window.open("http://127.0.0.1:"+port+"/", "_blank", "noopener")`——唯一域 127.0.0.1、noopener、无跨域 API 探测（注释声明与实际一致） | ✓ |
| slash 三路检测与回退链 | ① `ctx.SlashCommandParser` → ② `SillyTavern.SlashCommandParser` → ③ `window.SlashCommandParser`；新式 `addCommandObject`（name/callback/helpString/returns/namedArgumentList）优先 → 旧式 `ctx.registerSlashCommand`（6 参数形态）回退 → 都不可用 `console.warn` 降级 | ✓ |
| 提示开关语义 | `showHints = raw.showHints !== false` 默认开启；关闭时**三处一致**：renderFindings 不渲染引导 note（L105）、openWebUI 不写提示（L143）、onAppReady 收起 intro（L284） | ✓ |
| settings 只读约定 | `getSettings` 只读 extensionSettings；写入由 ST 设置表单框架完成（注释与实现一致，无 setItem/写设置代码） | ✓ |
| token 零接触 | 注释声明「token 由服务器注入的页面自取自用，插件零接触、零存储」——全文无读取 meta/continuity-token 代码（grep 0 命中） | ✓ |

### 1.3 settings.html 审查

- 仅两个字段：`showHints`（checkbox，checked 默认）+ `webuiPort`（number，min=1 max=65535 step=1，value=8777）——与 getSettings 读取名/校验范围**完全一致** ✓
- 无密钥字段（api_key/apikey/password/secret/token 0 命中）、无外部资源、无内联脚本 ✓
- 使用 ST 设置框架自带类（inline-drawer），注释「字段经 ST 框架自动绑定」与实际约定一致 ✓

### 1.4 注释审查（新增中文注释与实现一致）

- 头部约束注释（只读/仅 127.0.0.1/不接触密钥/无 localStorage）与实现全部一致 ✓
- L26「默认端口 8777（创始人裁决）」、L27「ST 以扩展文件夹名为键保存设置」、L174「slash 在 STscript 管道中不产出文本只触发面板」、L132「token 零接触」、L283「提示开关关闭时收起说明文案（下次启动生效）」——逐一与代码比对**全部一致，无错误/过时/误导注释** ✓

### 1.5 静态契约新增 4 例（44→48）

| 新测试 | 断言 | 真实性 |
|--------|------|--------|
| test_index_js_open_webui_button | 唤起按钮 + window.open 127.0.0.1 + 无跨域探测 | 真实 |
| test_index_js_slash_command_registration | `/continuity` 双路径（addCommandObject + registerSlashCommand 回退） | 真实 |
| test_index_js_reads_settings_via_extensionsettings | extensionSettings["continuity-st"] + 默认 8777 | 真实 |
| test_settings_html_exists_no_keys_no_external | 设置页存在 + 端口/开关字段 + 无密钥 + 无外部 URL | 真实 |

### 1.6 与上一轮（P2）比较

- P2 的 44 例全部保留（含 P1-1 状态机与 2 回归）；新增 4 例聚焦 P3 攻击面（外部 URL/密钥字段/网络调用）✓
- 无新增问题。

**第 1 轮结论：功能与真实测试通过（node 24/24、pytest 360+1 均 QA 复跑）；P3 代码逐行正确；注释全部一致；静态契约 48 例真实。**

---

## 第 2 轮「安全与十规则审计 — 真实执行 + 投毒反证」

| # | 检查项 | 真实执行结果 | 判定 |
|---|--------|--------------|------|
| B1 | 新代码唯一外部域名 127.0.0.1 | grep 外部 URL 仅 1 处 `"http://127.0.0.1:" + settings.port + "/"`；契约断言 `_no_external_urls` 通过 | ✓ |
| B2 | settings.html 无密钥字段 | grep api_key/apikey/password/secret/token **0 命中**（复跑） | ✓ |
| B3 | 无 eval/innerHTML/localStorage/fetch/XHR/写路径 | grep 全部 0 命中（命中仅注释自述或 ST eventSource 事件注册） | ✓ |
| B4 | window.open 仅 noopener | 全文仅 1 处 window.open，第三参数 `"noopener"` | ✓ |
| B5 | token 零接触 | 无读取 meta/token/continuity-token 代码（grep 0 命中） | ✓ |
| B6 | **投毒反证 4 组**（喂样本给契约判定逻辑） | ① 注入外部域 window.open → **检出**；② settings.html 注入 `name="apiKey"` → **检出**；③ 注入 `fetch(...)` → **检出**；④ 合法 127.0.0.1+noopener 样本不误报 | ✓ 全 PASS |

### 十条规则逐条

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓ | 插件零写路径（设置写入由 ST 框架，插件代码只读） |
| 2 默认不上传 | ✓ | 唯一域 127.0.0.1（B1）、无网络 API（B3） |
| 3 不执行导入内容 | ✓ | 无 eval/innerHTML（B3），渲染全 textContent |
| 4 R0–R3 只归引擎 | ✓ | P2 已锁定（hint 级话术），P3 无判定逻辑 |
| 5 动作日志与差异 | ✓（N/A） | 控制台 debug/warn 降级提示 |
| 6 不删测试/注释强制 | ✓ | 44 例保留 + 4 新增真实；注释一致（1.4） |
| 7 先计划阶段停等 | ✓ | 计划第 4 节 P3 行先行；P4 未越权 |
| 8 无 NFT/代币/钱包/云端 | ✓ | 全插件 grep 0 命中 |
| 9 格式不确定不猜测 | ✓ | 端口越界回退默认、无字段语义猜测 |
| 10 未运行不标通过 | ✓ | node/pytest 均 QA 本轮真实复跑 |

### 与第 1 轮结论比较

- 第 1 轮静态结论经 4 组投毒反证确认有效；无新增漏洞；无退回项。

**第 2 轮结论：安全与十规则审计通过（唯一域 127.0.0.1、noopener、零密钥零 token、契约可拦截投毒）。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归核对

- 361 collected = 360 passed + 1 skipped（真实运行）：357 基线无删减 + 4 例新增 ✓；node 24/24 ✓
- 无删除/无降低/无硬编码：既有测试文件零删除；4 例新契约真实断言（1.5 表）

### 3.2 git 写作用域核对（只读命令）

- developer 名下：`M extensions/sillytavern/continuity-st/{index.js,style.css,README.md}`、`?? settings.html`、`M tests/test_st_plugin_static.py`——**仅 extensions\ + 静态测试文件，未越界**（webui/src/其他 tests 零改动）✓
- 无 commit（等三轮结论，符合约定）✓

### 3.3 对照 st-plugin-plan.md 第 4 节 P3 验收要点

| 计划 P3 验收要点 | 实测 |
|------------------|------|
| 静态测试（slash 注册代码存在、只 127.0.0.1 域名） | ✓ 4 例新契约 + grep 实证 |
| 创始人本机 ST 实测（按钮开新标签、slash 触发体检、控制台零报错） | **沙箱无法执行 → 留待创始人真机验收（计划 6.2，P3/P4 一并）** |

### 3.4 差距清单

| # | 差距 | 属性 |
|---|------|------|
| G1 | 真机 slash API 形状验证（addCommandObject 的 namedArgumentList/returns 字段是否与创始人所用 ST 版本实际 API 完全匹配）——沙箱无 ST，只能静态形状检查 | 预期（计划 6.2 真机验收） |
| G2 | 设置表单字段绑定（name=showHints/webuiPort 与 ST 框架自动绑定行为的真机确认） | 预期（同上） |
| G3 | 弹窗策略（浏览器对 window.open 拦截场景）真机确认 | 预期（同上） |
| G4 | P4（双语 README 完善、版本门槛 UX、收录准备）未做 | 预期 |

### 3.5 发布准备核查

- README P3 阶段表已更新（唤起+slash 行）；设置页说明文案与实现一致 ✓
- 无新依赖、无新资源 ✓

### 与第 2 轮结论比较

- 第 3 轮新增：P3 验收要点静态部分达成/真机部分留待创始人、G1–G4 差距清单；无新增退回项。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 + 注释审查 | 通过（node 24/24、pytest 360+1；注释全一致） |
| 第 2 轮 安全与十规则审计（真实执行 + 投毒反证 4 组） | 通过（唯一域 127.0.0.1、noopener、零密钥零 token） |
| 第 3 轮 回归与发布审查 | 通过（基线无删减、写作用域合规、静态验收要点达成） |

### 退回项：**无**

### 观察/建议（非阻塞）

- G1–G3 真机项请创始人按计划 6.2 在 P3/P4 真机验收中一并执行（slash 形状、设置绑定、弹窗策略、控制台零报错）。

**一句话验收建议**：P3 三轮全部通过、无退回项——唤起与 slash 双路径、端口校验、noopener、提示开关三处一致、token 零接触均经逐行审查与投毒反证；建议交创始人验收，真机验证（G1–G3）按计划并入 P4 真机验收，通过后 commit。
