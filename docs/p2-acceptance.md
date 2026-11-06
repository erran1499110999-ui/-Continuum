# P2 验收清单 — ST 插件内存态体检（developer 交付三轮独立审核，创始人严格模式）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定）
> 审核时间：2026-11-07 00:50–01:10
> 审核范围：`extensions/sillytavern/continuity-st/{checks.js,index.js,style.css,package.json}` + `extensions/sillytavern/tests/checks.test.mjs` + `tests/test_st_plugin_static.py`（44 例）+ webui/src 与 3 个 webui 测试文件的注释补写
> 依据：AGENTS.md（最新版，含「代码注释强制」第 6 条）、docs/TEAM-COORDINATION.md、docs/st-plugin-plan.md 第 4 节 P2 行、docs/failure-case-library.md、docs/research-st-plugin.md、docs/research-sillytavern.md
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查 + 注释审查」

### 1.1 node:test 24 例亲自复跑（规则 10：执行方式差异如实记录）

| 执行方式 | 实测结果 |
|----------|----------|
| A. 官方 `node --test extensions/sillytavern/tests/checks.test.mjs` | **EPERM（spawn 被拒）**——Node 24 的 test runner 以子进程跑测试文件，沙箱禁止 spawn。developer 说明属实 ✓ |
| B. 直接执行 `node extensions/sillytavern/tests/checks.test.mjs`（单进程） | **真实运行 24 例全过**：`tests 24 / pass 24 / fail 0 / skipped 0 / 11.6ms`——node:test 的 `test()` 在直接执行时于进程内自动运行，**同一套 node:test 用例、同断言**（非替换为 print 脚本），规则 10 满足（QA 亲自复跑）✓ |

执行方式差异如实记录：官方 runner 受沙箱 EPERM 限制；替代方式「直接执行文件入口」实测为**真实 node:test 执行**（TAP 输出 24/24），非伪造。

### 1.2 全套 pytest 真实运行（AGENTS.md 固化命令）

**真实输出：collected 231 → 230 passed, 1 skipped, 1 warning in 22.56s，退出码 0**
与预期一致：225 基线全保持（webui 注释补写零行为变化，见 3.2）+ 插件静态契约 38→**44 例**（collect-only 实测 44）全过 ✓。

### 1.3 checks.js 逐行审查（判定逻辑 vs 案例库依据与边界）

| 检查 | 逻辑核对 | 边界核对（对照案例库/测试） | 结论 |
|------|----------|------------------------------|------|
| buildSnapshot | 只读快照；chat/characters/characterId 类型保护；metadata 兼容 `chatMetadata`/`chat_metadata` 双字段名；currentCard 浅拷贝 | 快照隔离测试（改源对象不影响快照顶层字段）✓ | ✓ |
| H1 checkIntegrity | `integrity` 非空字符串才放行；缺失/空 → hint | 旧格式无 metadata 不误伤（测试断言 detail 含「不一定是损坏」）✓ | ✓ |
| H2 checkResetChat | 消息数 ≤2 且末条 `is_user===false` 且 `mes===first_mes` | **>2 条不触发 ✓；末条非 first_mes 不误报 ✓**（两边界均有测试） | ✓ |
| H3 checkDuplicateNames | 按 name 分组、JSON.stringify 整卡签名、同名且签名不同才报 | 同名相同内容不报 ✓；不同名不报 ✓ | ✓ |
| H4 checkCardFields | `!(f in card)`/空串/null/undefined 判缺失；只报字段名 | 隐私测试（detail 不含卡内容）✓；无当前卡不报 ✓ | ✓ |
| H5 checkMessageStructure | 非对象/缺 mes/非布尔 is_user 各计 1 | 非对象消息不崩溃 ✓ | ✓ |
| runChecks | H1–H5 顺序、findings 空数组、level 恒 "hint" | 多重问题 id 集合断言 ✓ | ✓ |

### 1.4 注释正确性审查（新流程：错误/过时/误导注释=退回项）

| 位置 | 注释内容 | 核对结果 | 判定 |
|------|----------|----------|------|
| checks.js:33 | 「ST 内存对象为 chatMetadata，聊天文件落盘字段为 chat_metadata」 | research-st-plugin.md:24 证实 getContext 暴露 **chatMetadata**；research-sillytavern.md:115-116 证实 JSONL 落盘 **chat_metadata** | ✓ 正确 |
| checks.js H1–H5 案例编号（CASE-02/13/16、01/03、07、18/21、11） | 逐个核对 failure-case-library.md | 全部真实存在且语义匹配（CASE-07=同名卡导入覆盖 L72）| ✓ 正确 |
| checks.js:35 「复制一份」 | 实为**浅拷贝**（Object.assign） | H 检查仅用顶层标量字段，行为安全；措辞欠精确 | ⚠ 观察项 C2 |
| index.js 全文注释（P2 定位/约束/渲染/薄壳原则） | 与代码逐一比对 | 一致 ✓ | ✓ |
| checks.js:12 + checks.test.mjs:4-5 | 只写「node --test」官方运行方式 | **未记录沙箱 EPERM 事实与替代执行方式**（`node <file>`），与团队实际验证方式不一致——后续开发者按注释跑官方命令会失败且不知替代方案 | ⚠ **退回项 C1**（注释过时/不完整） |

### 1.5 静态契约 44 例与新增 6 例

新增：`test_js_imports_only_relative_local_modules`（×2 文件：仅 `./` 相对、禁 `..`、限 `.js`）、`test_js_no_st_script_imports`（×2）、`test_js_no_r_level_judgments_in_code`（×2）、`test_index_js_has_check_panel`、`test_package_json_declares_module`——全部真实断言；`test_checks_js_placeholder` → `test_checks_js_exports` 为**语义升级替换**（占位→7 个导出契约），非删测试 ✓。

### 1.6 与上一轮（P1/P1-1）比较

- P1/P1-1 的 36+2 例全部保留（含 P1-1 状态机与 2 回归）；新增 6 例聚焦 P2 新攻击面（import 白名单、R 级禁令）✓
- 新发现：C1（执行方式注释不完整）、C2/C3/C4（观察项）——上轮无此对象。

**第 1 轮结论：功能与真实测试通过（node:test 24/24 与 pytest 230+1 均 QA 亲自复跑）；判定逻辑与边界全部正确；注释审查发现退回项 C1 + 观察项 C2/C3/C4。**

---

## 第 2 轮「安全与十规则审计 — 真实执行攻击面检查」

| # | 攻击面/检查 | 真实执行结果 | 判定 |
|---|-------------|--------------|------|
| B1 | 写路径（writeFile/FileSystem/createObjectURL/Blob/download/saveToFile/fs./extensionSettings/saveSettings） | grep **0 命中** | ✓ 零写路径 |
| B2 | 网络 API（fetch/XMLHttpRequest/WebSocket/EventSource） | 仅 `eventSource` 命中为 **ST 事件注册**（`context.eventSource.on(APP_READY)`，非网络请求）；fetch/XHR/WS 0 命中 | ✓ |
| B3 | 密钥字样（api_key/Bearer/secret/access_token） | 0 命中 | ✓ |
| B4 | localStorage/sessionStorage | 0 命中（命中仅为注释自述） | ✓ |
| B5 | import 白名单真实生效 | 唯一 import = `./checks.js`（相对、无 `..`、.js 后缀，满足测试断言）| ✓ |
| B6 | 面板渲染 | index.js 渲染全 `textContent`/`createElement`/节点 API；grep innerHTML 0 命中（注释除外）；测试断言「textContent」存在 | ✓ |
| B7 | 话术与 R 级判定禁令 | 代码 grep R0–R3 **0 命中**；node:test 断言「所有发现 level 恒 hint 且 title+detail 无 R0–R3 字样」真实执行 24/24 通过 | ✓ |
| B8 | 只读性 | node:test「runChecks 前后 context JSON 相等」真实执行通过 | ✓ |
| B9 | 外部 URL | JS 源码 0 外部 URL（127.0.0.1:8777 文案为本地唤起地址，属白名单） | ✓ |

### 十条规则逐条（结合攻击面证据）

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓ | 插件零写路径（B1）；只读性测试（B8） |
| 2 默认不上传 | ✓ | 零网络 API（B2）、零外部 URL（B9）、README 隐私声明 |
| 3 不执行导入内容 | ✓ | 渲染全 textContent（B6）、无 eval/innerHTML |
| 4 R 级判定只归引擎 | ✓ | 代码零 R 级字样 + 测试断言（B7）；level 恒 hint |
| 5 动作有日志与差异 | ✓（N/A） | 插件无迁移/修复动作；控制台 debug 日志 |
| 6 不删测试/不降断言 | ✓ | 225 基线保持；44 例真实契约；24 例 node:test 真实 |
| 7 先计划阶段停等 | ✓ | st-plugin-plan 先行；P3（唤起/slash）未越权实现 |
| 8 无 NFT/代币/钱包/云端 | ✓ | 全插件目录 grep 0 命中 |
| 9 格式不确定不猜测 | ✓ | 话术「提示/疑似/建议」，字段缺失只报缺失不猜原因（H1/H4 注释与代码一致） |
| 10 未运行不标通过 | ✓ | node:test 与 pytest 均由 QA 本轮亲自真实复跑 |

### 与第 1 轮结论比较

- 第 1 轮静态结论全部经攻击面真实执行复核，无新漏洞；C1 延续为退回项；十规则无违例。

**第 2 轮结论：安全与十规则审计通过（零写路径、零网络、零密钥、import 白名单真实生效、R 级禁令测试锁定）。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归数字核对

- 231 collected = 230 passed + 1 skipped（QA 亲自真实运行，与预期一致）；225 基线无删减（webui 注释补写零行为变化，见 3.2）+ 6 例新增 ✓
- 无删除/无降低/无硬编码：1 例占位测试语义升级替换（placeholder→exports），其余全保留

### 3.2 git 写作用域与「注释改动零行为变化」核对（只读命令）

- developer 名下：`extensions/`（checks/index/style/package + tests/checks.test.mjs）、`tests/test_st_plugin_static.py`、`src/continuity/webui/{api,jobs,server,validation,views}.py`、`tests/test_webui_{api_scan,jobs,server}.py`——全部符合写作用域 ✓
- **webui 5 源文件 diff 逐行核对：全部为注释/docstring 新增/改写，零代码变化** ✓
- **webui 3 测试文件 diff：仅 2 行 docstring 删除/重写，零断言/测试函数变化**（grep 新增行无 assert/def test 匹配）✓
- 其余 ??/M（PROGRESS/product-plan/resource-map/ui-design-direction/marketing-copy/claude-design-study/frontend-design-notes/preview/）属 lead/researcher/frontend-developer，正常 ✓
- 无 commit（等三轮结论，符合约定）✓

### 3.3 对照 st-plugin-plan.md 第 4 节 P2 验收要点逐项

| 计划 P2 验收要点 | 实测 |
|------------------|------|
| 沙箱内 Node 可用性实测（前置门） | **实测 Node v24.15.0 存在**；但官方 `node --test` 被沙箱 EPERM 拒（spawn），替代方式单进程执行真实跑通 24/24（QA 亲自复跑并记录差异） |
| JS 单测真实运行全过 | node:test 24 例：pass 24 / fail 0（QA 复跑）✓ |
| 静态测试全过 | 44 例全过（collect-only 实测 44）✓ |
| 无任何写路径 | grep 零写路径 + 只读性测试 ✓ |

### 3.4 与阶段目标差距清单（P3/P4 未做属预期）

| 阶段 | 内容 | 现状 | 差距 |
|------|------|------|------|
| P3 | 唤起按钮（127.0.0.1:8777 读 extensionSettings）+ `/continuity` slash + 设置页 | 面板 note 文案已预告「P3 提供一键唤起」，无实际唤起代码 | **未做（预期内）** |
| P4 | 双语 README 完善、版本门槛 UX、官方收录准备、创始人真机验收 | README 仍为 TODO-P4 占位 | **未做（预期内）** |

### 3.5 发布准备核查

- package.json：`type: module` + `private: true` ✓（node:test ESM 前置，测试断言锁定）
- 话术克制：全部 hint 级、「疑似/建议/初步提示」字样，无结论性判定 ✓
- 隐私：H4 只报字段名不报内容（测试断言）✓

### 与第 2 轮结论比较

- 第 3 轮新增：执行方式差异的发布级记录、P3/P4 差距清单、package.json 核查；
- C1 延续至最终退回清单；观察项 C2/C3/C4 维持非阻塞。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 + 注释审查 | 通过（node:test 24/24、pytest 230+1 均 QA 复跑）；退回项 C1 |
| 第 2 轮 安全与十规则审计（真实执行攻击面） | 通过（零写/零网络/零密钥/R 级禁令测试锁定） |
| 第 3 轮 回归与发布审查 | 通过（基线无删减、注释改动零行为变化、P2 验收要点全达成） |

### 退回修复清单（修复后复审，再交创始人）

| # | 严重级 | 问题 | 具体修改建议（文件:行 + 改法） |
|---|--------|------|-------------------------------|
| C1 | 低（注释类退回项） | checks.test.mjs:4-5 与 checks.js:12 的运行注释只写官方 `node --test`，未记录沙箱 EPERM 事实与替代执行方式——按 AGENTS.md 第 6 条「过时/误导注释=退回项」，且后续开发者照注释执行会失败 | `extensions/sillytavern/tests/checks.test.mjs:4-5` 与 `extensions/sillytavern/continuity-st/checks.js:12` 补写：「沙箱内 `node --test` 因禁 spawn 报 EPERM；替代：`node extensions/sillytavern/tests/checks.test.mjs` 单进程执行同一套 node:test 用例（Node 24 已实测 24/24）」 |

### 改进建议（非阻塞）

- C2 `checks.js:35`：「复制一份」→ 改为「浅拷贝当前卡数据（H 检查只读顶层标量字段）」；
- C3 `checks.js:159-160`：H5 detail「N 条消息」实为缺陷计数（一条消息两缺陷计 2），建议改「N 处异常」或按消息数统计；
- C4 `checks.js:99`：H3 签名 JSON.stringify 对键顺序敏感，建议 `JSON.stringify(data, Object.keys(data).sort())`（同源对象键序通常一致，风险极低）。

**一句话验收建议**：P2 功能、安全、回归三轮通过、判定逻辑与案例库依据全部正确，仅 1 项轻级注释退回项（C1 执行方式注释）——建议 developer 补写运行注释后复审，通过即可交创始人验收、commit 并按阶段推送 GitHub；真机验收按计划留待 P3/P4。

---

## 5. 修复复审（developer 修复 C1/C2/C3 后复检，2026-11-07 凌晨追加）

### 5.1 三处修复逐项核对（读代码确认）

| # | 修复内容 | 实测 |
|---|----------|------|
| C1 | checks.test.mjs 头部注释补齐两种运行方式（官方 `node --test` + 沙箱替代 `node <file>` + EPERM 原因 + Node v24.15.0 实测 24/24）；checks.js 头部同步补「运行单测的两种方式」段落 | ✓ 描述与 QA 实测行为完全一致（官方方式 EPERM、替代方式单进程 24/24） |
| C2 | 「复制一份」→「当前角色卡数据做浅拷贝（H 系列检查只读顶层标量字段，浅拷贝即足够）」 | ✓ 措辞精确、与 Object.assign 实现一致 |
| C3 | H5 detail「N 条消息…异常」→「存在 N 处结构异常（缺少文本或角色标记异常）」 | ✓ 「处」与缺陷计数语义一致 |

C4（JSON.stringify 键序）按 developer 说明明确不改、留待后续——与上轮「改进建议」定位一致，接受。

### 5.2 真实复跑

- node 单测（沙箱替代方式）：**24/24 通过**（tests 24 / pass 24 / fail 0 / 12.7ms，QA 亲自复跑）
- 全套 pytest：**302 collected = 301 passed + 1 skipped, 22.55s，退出码 0**（C 修复为纯注释/文案改动，无回归；frontend-developer 的 71 例新文件同时在全量中通过，非本复审范围）

### 5.3 复审结论

**修复复审通过：C1/C2/C3 落地准确、无回归、无新退回项。**
P2 可以提交创始人验收，并由创始人执行 Git commit（extensions/ 全部文件 + tests/test_st_plugin_static.py 等 P2 变更）后按阶段推送 GitHub。
