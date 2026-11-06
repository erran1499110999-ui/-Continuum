# P1 验收清单 — ST 插件骨架（developer 交付三轮独立审核，创始人严格模式）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定）
> 审核时间：2026-11-07 00:20–00:40
> 审核范围：`extensions/sillytavern/continuity-st/`（5 文件）+ `tests/test_st_plugin_static.py`（36 例）+ `docs/st-plugin-plan.md`、`docs/webui-plan.md` 更新
> 依据：AGENTS.md（最新版）、docs/TEAM-COORDINATION.md（含 2026-11-07 凌晨创始人新指令）、docs/st-plugin-plan.md 第 4 节 P1 验收要点
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查」

### 1.1 全套 pytest 真实运行（AGENTS.md 固化命令实际执行）

**真实输出（00:20 运行）**：**collected 223 → 222 passed, 1 skipped, 1 warning in 22.45s，退出码 0**
与预期一致：187 基线全保持（含 W1/W2 复审修复基线）+ `test_st_plugin_static.py` **36 例全过** ✓。
1 skip = 符号链接环境跳过；1 warning = anyio 第三方弃用。

### 1.2 36 例静态测试逐类审查（是否真实有效，非空转断言）

| 类别 | 例数 | 审查结论 | 证据 |
|------|------|----------|------|
| 目录/文件集合（存在性、无垃圾/隐藏文件） | 2 | 真实：真实路径断言 + 文件集合并集断言 | L31-41 |
| manifest schema（合法 JSON、9 必填字段矩阵、语义版本、1.12.0、MIT、js/css 文件真实存在） | 14 | 真实：逐字段 + 正则 + `is_file()` | L46-80 |
| JS 安全 lint（×2 文件：eval/innerHTML/document.write/外部 URL/localStorage/密钥字样/网络 API/import） | 16 | 真实：对剥注释后源码逐模式断言（有效性经第 2 轮投毒反证实证） | L83-165 |
| index.js 契约（getContext/APP_READY/use strict/VERSION） | 1 | 真实 | L168-173 |
| checks.js 占位（P2/use strict/无副作用声明） | 1 | 真实 | L178-182 |
| 双语 README 占位（TODO-P4/双语章节/127.0.0.1/MIT/1.12.0/display_name 一致） | 2 | 真实 | L187-200 |

无 `assert True`、无空转、无 mock——**36 例全部为真实静态契约断言**。
逐行审查发现一个**理论盲点**（`_strip_comments` 不处理字符串字面量，L85-100），第 2 轮以投毒反证**实锤**（见 B4）。

### 1.3 manifest.json 与创始人确认默认值逐字段核对

| 字段 | 创始人确认值 | 实测 | 结论 |
|------|-------------|------|------|
| display_name | 「Continuity 体检」 | `"Continuity 体检"`（UTF-8 精确一致） | ✓ |
| minimum_client_version | 1.12.0 | `"1.12.0"`（语义版本） | ✓ |
| license | MIT | `"MIT"` | ✓ |
| js / css 引用文件真实存在 | — | `index.js`、`style.css` 均 `is_file()` ✓ | ✓ |
| 其余字段 | — | `manifest_version:1`、`loading_order:100`、`requires:[]`、`optional:false`、`author`、`version:0.1.0`（semver）、`homePage`（GitHub）——全部 ST manifest v1 标准字段，**无任何权限类字段** | ✓ |

### 1.4 与上一轮（W1/W2 复审）比较

- 无代码交集：P1 为全新目录 + 全新测试文件，未触碰任何既有文件（git 核对见第 3 轮）✓
- 新发现问题：lint 注释剥除盲点（本报告 B4）——上轮无此对象，属新发现。

**第 1 轮结论：功能与真实测试通过（222+1 全过）；manifest 与创始人默认值完全一致；36 例真实有效，但 lint 注释剥除存在盲点（待第 2 轮实证）。**

---

## 第 2 轮「安全与十规则审计 — 真实执行攻击面检查」

全部为**独立真实执行**（不依赖 pytest 断言）：直接扫描插件源码 + 投毒反证实证。

| # | 攻击面/检查 | 真实执行结果 | 判定 |
|---|-------------|--------------|------|
| B1 | JS 投毒面独立扫描（index.js + checks.js：eval/innerHTML/document.write/localStorage/fetch/XMLHttpRequest/WebSocket/EventSource/import/window.open/sessionStorage/staging/密钥字样/fs·require·node:·process） | 实际代码**零命中**；命中项（innerHTML/localStorage/import/node:test）全部位于**注释自述约束**（与 pytest 剥注释检测结果一致） | ✓ 干净 |
| B2 | 外部 URL 扫描 | 两 JS 文件 `https?://` 匹配 **0 个**（P1 无唤起代码，符合范围；127.0.0.1 白名单规则已由测试锁定） | ✓ |
| B3 | 写路径扫描（writeText/FileSystem/createObjectURL/Blob/download/saveToFile/writeFile/fs./extensionSettings/saveSettings） | **0 命中**（extensionSettings 仅注释提及） | ✓ 零写路径 |
| B4 | **投毒反证实证**（把投毒样本喂给静态检查函数，验证检出能力） | ① `fetch("https://evil.example/x")` → **检出** ✓；② `const u = "https://api.evil.example"` → **检出** ✓；③ `http://127.0.0.1:8777` → 白名单放行 ✓；④ **`const u = "http://evil.example/x"` → 未检出（漏检）**——`_strip_comments` 把字符串内 `//` 当行注释剥掉，输出只剩 `const u = "http:` | ⚠ **实锤盲点** |
| B5 | manifest 权限字段 | 12 个字段全部为 ST manifest v1 标准字段，无 `permissions` 类多余字段 | ✓ |
| B6 | README 双语隐私声明 | 双语占位合规：只读内存/绝不写文件/绝不上传/绝不接触 API 密钥/除 127.0.0.1 外零网络；**无上传承诺、无 NFT/代币/钱包/云端表述** | ✓ |
| B7 | CSS 外部资源 | `@import/url(/https?://` 0 命中，无外部字体/CDN | ✓ |

**B4 盲点详析（退回项 P1-1）**：`tests/test_st_plugin_static.py:85-100` 的 `_strip_comments` 不处理字符串字面量——字符串中以 `http://` 开头的 URL 会触发 `//` 误剥，**且该字符串之后直到行尾的真实代码一并被吞掉**（例：`const u = "http://x"; fetch("https://evil")` 被剥成 `const u = "http:`，后续 fetch 也漏检）。P1 的核心交付就是「静态契约防投毒」，契约本身可被绕过即未达目的。**具体改法（二选一）**：
- 方案 A（推荐，最彻底）：把 `_strip_comments` 改为**状态机**（跟踪字符串/模板串/转义状态，仅剥真实注释），一处修复惠及全部 lint；
- 方案 B（最小改动）：`test_js_no_external_urls`、`test_js_no_key_literals`、`test_js_no_network_apis` 改为对**未剥注释的完整源码**断言（注释里出现 URL/密钥字样同样该报——收紧不放松）；eval/innerHTML 类保留剥注释（当前源码注释提及约束字样，避免误报）。
并建议补 2 个回归测试：字符串内 URL 检出、字符串内 `//` 后跟 fetch 的检出。

### 十条规则逐条对照（结合攻击面证据）

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓ | 插件零写路径（B3）；不写 ST 数据 |
| 2 默认不上传 | ✓ | 零网络 API（B1）、零外部 URL（B2）、README 双语承诺（B6） |
| 3 不执行导入内容 | ✓ | 无 eval/innerHTML/document.write（B1），UI 全 textContent |
| 4 R0–R3 不伪造 | ✓ | checks.js 声明「绝不产出 R 级修复判定，R 级结论只由 Python 引擎给出」；P1 无判定逻辑 |
| 5 动作有日志与差异 | ✓（N/A） | P1 骨架无迁移/修复动作；控制台 debug 加载日志 |
| 6 不删测试/不降断言 | ✓ | 基线 187 全保持；36 例新增全真实断言 |
| 7 先计划阶段停等 | ✓ | st-plugin-plan.md 先行、P1 停等验收；未越权实现 P2/P3（checks.js 占位、无 slash/唤起代码） |
| 8 无 NFT/代币/钱包/云端 | ✓ | 全插件目录 grep 0 命中（B6） |
| 9 格式不确定不猜测 | ✓ | 计划明言 H 系列话术保守（提示/疑似/建议），R 级结论归引擎 |
| 10 未运行不标通过 | ✓ | 本轮真实运行 223 例 + 全部攻击面真实执行 |

### 与第 1 轮结论比较

- 第 1 轮标注的「理论盲点」经 B4 投毒反证**升级为实锤退回项**（P1-1）；
- 其余攻击面（B1–B3、B5–B7）全部真实执行通过，与第 1 轮静态结论一致，无新增问题。

**第 2 轮结论：安全与十规则审计通过（插件源码零投毒面、零写路径、零网络）；发现 1 项契约测试盲点（P1-1），列为退回项。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归数字核对

- 223 collected = 222 passed + 1 skipped（真实运行，与预期一致）：187 基线（含 W1/W2 复审修复后基线 cba1d16）**无删减** + 36 例新增全过 ✓
- 无删除/无降低/无硬编码：既有测试文件零 diff；36 例为真实静态断言（第 1 轮逐类审查 + 第 2 轮反证实证）

### 3.2 git 写作用域核对（只读命令）

- developer 名下：`?? extensions/`（新目录 5 文件）、`?? tests/test_st_plugin_static.py`（新文件）、`M docs/webui-plan.md`、`?? docs/st-plugin-plan.md`（计划更新）——**全部符合其写作用域，零修改任何既有源码/测试** ✓
- 其余 `??`（PROGRESS.md、product-plan.md、resource-map.md、ui-design-direction.md、marketing-copy.md）与 `M docs/TEAM-COORDINATION.md` 属 lead/researcher 正常产物 ✓
- 无 commit 记录（等三轮审核结论，符合约定）✓

### 3.3 对照 docs/st-plugin-plan.md 第 4 节 P1 验收要点逐项

| 计划 P1 验收要点 | 实测 |
|------------------|------|
| pytest 真实运行 | 223 collected = 222 passed + 1 skipped，22.45s，退出码 0 ✓ |
| manifest 全字段校验通过 | 9 必填字段矩阵 + semver + 1.12.0 + MIT + js/css 存在性，14 例全过 ✓ |
| 静态 lint 全过 | 36 例全过 ✓（但 lint 自身有注释剥除盲点，见退回项 P1-1） |

### 3.4 与阶段目标差距清单（P2–P4 未做属预期）

| 阶段 | 内容 | 现状 | 差距 |
|------|------|------|------|
| P2 | checks.js 纯函数 H1–H6 + 面板渲染 + node:test 单测 | checks.js 为占位（P2 标注）| **未做（预期内）**；前置门「沙箱 Node 可用性实测」（计划 5.1）待 P2 开工验证 |
| P3 | 唤起按钮（127.0.0.1:8777）+ `/continuity` slash + 设置页 | 无（P1 范围外）| **未做（预期内）** |
| P4 | 双语 README 完善 + 版本门槛 UX + 收录准备 + 三轮审核 | README 为 TODO-P4 占位（双语骨架已就位）| **未做（预期内）**，占位符合 P4 节奏 ✓ |

### 3.5 发布准备核查

- README 双语占位：安装/隐私声明双语骨架 + TODO-P4 标记清晰 ✓（符合 P4 节奏，主 README 插件一节待 P4 创始人协调）
- 无 NFT/代币/钱包/云端表述 ✓；隐私声明无上传承诺 ✓
- GitHub 推送：P1 验收通过后按阶段推送（当前未 commit，符合约定）

### 与第 2 轮结论比较

- 第 3 轮新增：差距清单量化（P2–P4 均为预期内未做 + Node 前置门待验证）、发布核查；
- 第 2 轮退回项 P1-1 延续至最终结论，无新增退回项。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 | 通过（222+1 全过；manifest 与创始人默认值完全一致；36 例真实有效） |
| 第 2 轮 安全与十规则审计（真实执行攻击面 + 投毒反证） | 通过（源码零投毒面/零写路径/零网络）；发现退回项 P1-1 |
| 第 3 轮 回归与发布审查 | 通过（基线无删减；P1 验收要点全达成；P2–P4 差距属预期） |

### 退回修复清单（修复后复审，再交创始人）

| # | 严重级 | 问题 | 具体修改建议（文件:行 + 改法） |
|---|--------|------|-------------------------------|
| P1-1 | 中 | 静态契约测试的注释剥除不处理字符串字面量，字符串内 `http://` URL 及其后代码被误剥漏检——契约测试可被有意投毒绕过 | `tests/test_st_plugin_static.py:85-100`：方案 A 将 `_strip_comments` 改为字符串/模板串状态机（推荐）；或方案 B URL/密钥/网络 API 三项检查改用未剥注释完整源码。并补 2 个回归测试（字符串内 URL 检出、字符串内 `//` 后跟 fetch 检出） |

### 改进建议（非阻塞）

- `index.js:55`：`document.body.appendChild` 若在 body 就绪前执行会抛错——ST 插件系统在 APP_READY 后 body 必已存在，P4 可加 `document.body` 存在性防御；
- 徽标 `z-index:9999` 固定右下可能遮挡 ST UI（P4 打磨项）；
- `homePage` 指向 GitHub 属 manifest 元数据（非网络请求），符合规范。

**一句话验收建议**：P1 骨架功能、安全、回归三轮基本通过，但静态契约测试存在可被字符串 URL 绕过的盲点（P1-1，中危）——建议 developer 按「文件:行+改法」修复 `_strip_comments` 并补 2 个回归测试后复审；修复确认后即可交创始人验收并 commit。

---

## 5. 修复复审（developer 修复 P1-1 后复检，2026-11-07 凌晨追加）

### 5.1 全套 pytest 真实运行（AGENTS.md 固化命令）

**真实输出：225 collected = 224 passed + 1 skipped, 1 warning in 22.52s，退出码 0**
与 developer 自称一致；223 基线（含原 36 例插件静态测试，语义不变）全保持 + 新增 2 例回归全过 ✓。

### 5.2 状态机实现逐行审查（`tests/test_st_plugin_static.py:85-203`）

- 状态集：code / line / block / single / double / template / interp / interp-brace，覆盖 `''`、`""`、`` ` ` ``、模板插值 `${...}`、插值内嵌套花括号与嵌套字符串/注释、转义（`\"`、`\'`、`` \` ``）——实现与 QA P1-1 方案 A 一致 ✓
- line 状态保留换行符（防跨行 token 粘连）✓；未闭合字符串/模板保守保留（不漏检）✓；正则字面量中的 `\/` 不会误触发注释剥离（JS 语义下正则内 `/` 必须转义）✓
- 已知局限（记录，不阻塞）：插值内对象字面量字符串含裸 `}`（如 `${ {x: "}"} }`）时花括号配对会提前弹出一层，但因字符串内容仍被保留，不影响 URL/API 检出能力，仅中间状态短暂偏移。

### 5.3 独立投毒反证（6 组，真实执行，不依赖 pytest 断言）

| # | 样本 | 期望 | 实测 |
|---|------|------|------|
| R1 | `const u = "http://evil.example/x"` | 字符串内 URL 检出 | **PASS**（剥后完整保留并检出） |
| R2a | `const s = "a//b"; fetch("https://evil.example/x")` | 字符串内 `//` 不吞后续 fetch，外部 URL 检出 | **PASS** |
| R2b | `const s = "a//b";` | 纯字符串不误报外部 URL | **PASS** |
| R3 | `` const t = `http://${x}/y` `` | 模板串内容保留且 URL 检出 | **PASS** |
| R4 | `// fetch("https://evil.example/x")` | 真注释仍被剥、不误报 | **PASS**（剥后仅剩代码） |
| R5 | `const s = "esc \" http://no.example";` | 转义引号后 URL 仍检出 | **PASS** |
| R6 | `` `x${ 1 + 2 }// comment\n y` `` | 插值内注释剥除、其余保留 | **PASS** |

上一轮同场景样本（`const u = "http://evil.example/x"`）当时漏检，本轮全部检出——**盲点修复实锤生效**。

### 5.4 回归核对

- 新增 2 例回归测试（`test_strip_comments_keeps_url_in_string_detected`、`test_strip_comments_string_slash_not_swallow_following_code`，L273-287）为真实断言，精确锁定两种漏检路径 ✓
- 原 36 例插件静态测试**语义未变、全部通过**（lint 16 例的 `js_source` fixture 改用新状态机，断言内容未动；其余 20 例原样）✓
- 全量 225 例无删除、无降低、无硬编码 ✓

### 5.5 复审结论

**修复复审通过：P1-1 已按方案 A 修复并经 6 组独立反证实证有效，无回归、无新退回项。**
P1 可以提交创始人验收，并由创始人执行 Git commit（extensions/ 新目录 + tests/test_st_plugin_static.py + docs/webui-plan.md + docs/st-plugin-plan.md）。
