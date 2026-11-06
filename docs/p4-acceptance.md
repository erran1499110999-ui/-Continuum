# P4 验收清单 — ST 插件打磨与收录准备（上市前最后一轮，创始人严格模式）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定）
> 审核时间：2026-11-07 01:50–02:20
> 审核范围：`extensions/sillytavern/continuity-st/{index.js,README.md,style.css}` + `tests/test_st_plugin_static.py`（48→51 例）+ 主 `README.md` 插件章节 + `docs/st-launch-plan.md` §1
> 依据：AGENTS.md（最新版）、docs/st-launch-plan.md §1 官方收录要求、docs/st-plugin-plan.md 第 4 节 P4 行
> 审核人写作用域：仅本文件；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查 + 注释审查」

### 1.1 真实运行

| 运行 | 结果 |
|------|------|
| node:test（沙箱替代方式） | **24/24 通过**（QA 亲自复跑） |
| 全套 pytest（AGENTS.md 固化命令） | **364 collected = 363 passed + 1 skipped, 1 warning, 22.72s，退出码 0**——361 基线保持 + 3 例新契约全过 ✓ |

### 1.2 P4 新代码逐行审查

| 审查项 | 实现 | 判定 |
|--------|------|------|
| detectVersionHints | 仅**能力检测**：① extensionSettings 对象缺失 → 「可能过低（建议 ≥1.12.0），使用默认配置」；② slash 注册能力（三路 parser）缺失 → 「请使用面板按钮」。**全文无版本号字符串比较**（注释「版本格式会变，比较易误判」与实现一致）；提示为「建议升级」级，非阻断 | ✓ |
| onAppReady 接入 | hints → console.warn 逐条 +（showHints 开启时）`intro.textContent = hints.join("；") + "。" + intro.textContent` 前缀注入（textContent 安全） | ✓ |
| 插件 README 完整双语 | 首屏双语核心文案（与 launch-plan 模板一致）、安装三步双语、使用功能表、H1–H5 说明、hint 话术 + R 级只归引擎、隐私声明（不收集/不存储/不上传/无遥测无广告无云端）、兼容声明（≥1.12.0 + 能力检测 + 无 staging 依赖 + 薄壳定位）、收录自查表、MIT | ✓ |
| 样式暖调化 | style.css grep：**零外部资源（@import/url(/http 0 命中）、零装饰动画（@keyframes/animation/blob/particle/noise 0 命中）** | ✓ |

### 1.3 注释审查（新增注释与实现一致）

- index.js L77-78「版本门槛提示（只用能力检测，绝不做版本号字符串比较）」、L82「设置持久化能力：1.12+ 扩展体系的基础」、L315 同义注释——与 detectVersionHints 实现逐一一致 ✓
- 插件 README 声明与代码行为一致（「不依赖 staging 事件」——grep `staging` 0 命中；「零密钥」——settings.html 无密钥字段）✓
- **无错误/过时/误导注释。**

### 1.4 对照 st-launch-plan.md §1 官方收录要求五条逐条核实

| 官方要求 | 落实 | 实测 |
|----------|------|------|
| ① 开源 + 自由许可证 | MIT | manifest `"license":"MIT"` + 插件 README「MIT」+ 主 README 双写 ✓ |
| ② 兼容最新 release | capability detection + minimum_client_version + 每 release 冒烟计划 | `minimum_client_version: "1.12.0"` + detectVersionHints + README 兼容声明 ✓ |
| ③ README 完整（安装/使用/功能） | 双语完整版 | 81 行：安装/使用/功能表/隐私/兼容/自查表 ✓ |
| ④ 不依赖 server 插件 | 纯 UI 扩展 | 无任何 server 插件引用，README 明示 ✓ |
| ⑤ 最佳实践（只用 getContext、禁存密钥、转义） | 已落实 | 全文仅 getContext + 浏览器原生 API；settings.html 零密钥；渲染全 textContent ✓ |

### 1.5 静态契约新增 3 例（48→51）

- `test_readme_full_bilingual`（TODO-P4 占位全部移除、双语章节齐全、隐私声明、MIT、1.12.0）——真实断言
- `test_js_no_staging_dependency`（staging 字样 0 命中，×js_source 文件）——真实
- `test_index_js_version_hints`（detectVersionHints 存在 + 无版本号字符串比较）——真实

### 1.6 与上一轮（P3）比较

- P3 的 48 例全部保留；新增 3 例聚焦 P4 上市面（README 完整性、staging 零依赖、版本提示纯能力检测）✓
- 无新增问题。

**第 1 轮结论：功能与真实测试通过（node 24/24、pytest 363+1 均 QA 复跑）；P4 代码正确；注释一致；收录五条全部核实达标。**

---

## 第 2 轮「安全与十规则审计 — 真实执行 + 投毒反证」

| # | 检查项 | 真实执行结果 | 判定 |
|---|--------|--------------|------|
| B1 | README/代码无夸大承诺 | R0–R3 字样在代码 0 命中（契约锁定）；README 明示「内存态初步提示，绝不产出修复等级判定」；「不收集/不存储/不上传」声明与实现（零网络/零写）一致 | ✓ |
| B2 | style.css 无外部资源/无装饰动画 | grep @import/url(/http/@keyframes/animation/blob/particle/noise **全 0 命中** | ✓ |
| B3 | 无 staging 依赖 | grep `staging` 0 命中 + 契约测试断言 | ✓ |
| B4 | 密钥字段零命中 | settings.html/index.js grep api_key/apikey/password/secret/Bearer 0 命中（命中仅注释自述） | ✓ |
| B5 | 唯一外部 URL 127.0.0.1 | 全文仅 L170 `"http://127.0.0.1:" + settings.port + "/"` | ✓ |
| B6 | **投毒反证 4 组** | ① R 级判定文案注入 → 检出；② 字符串内外部 URL（可执行位置）→ 检出；③ settings.html 注入 `name="apikey"` → 检出；④ 合法 hint 话术 + 127.0.0.1 样本不误报（注释内 URL 剥除为 P1-1 已确认的正确行为，作对照组） | ✓ 全 PASS |

### 十条规则逐条

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录 | ✓ | 插件零写路径（P2/P3 已锁定，P4 无新增写） |
| 2 默认不上传 | ✓ | 唯一域 127.0.0.1（B5）、零网络 API、README 隐私声明 |
| 3 不执行导入内容 | ✓ | 无 eval/innerHTML，textContent 渲染 |
| 4 R0–R3 只归引擎 | ✓ | 代码零 R 级字样（B1）+ 契约锁定 |
| 5 动作日志与差异 | ✓（N/A） | 控制台 debug/warn 提示 |
| 6 不删测试/注释强制 | ✓ | 48 例保留 + 3 新增；注释一致（1.3） |
| 7 先计划阶段停等 | ✓ | P4 为计划最后一轮；停等审核 |
| 8 无 NFT/代币/钱包/云端 | ✓ | 全插件 grep 0 命中；README「无广告、无遥测」 |
| 9 格式不确定不猜测 | ✓ | 版本提示只用能力检测不猜版本号 |
| 10 未运行不标通过 | ✓ | node/pytest 均 QA 本轮真实复跑 |

### 与第 1 轮结论比较

- 第 1 轮静态结论经投毒反证确认有效（含一次反证样本设计修正：注释内 URL 不执行、剥除正确；字符串内 URL 检出——契约判定真实有效）；无新增漏洞。

**第 2 轮结论：安全与十规则审计通过（无夸大承诺、零外部资源、零 staging、零密钥、契约可拦截投毒）。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归核对

- 364 collected = 363 passed + 1 skipped（真实运行）：361 基线无删减 + 3 例新增 ✓；node 24/24 ✓
- 无删除/无降低/无硬编码：3 例新契约真实断言（1.5）

### 3.2 git 写作用域核对（只读命令）

- developer 名下：`M README.md`（主 README 插件章节）、`M extensions/sillytavern/continuity-st/{README.md,index.js,style.css}`、`M tests/test_st_plugin_static.py`——**符合预期（extensions\ + 静态测试 + 主 README 插件章节），未越界** ✓
- 无 commit（等三轮结论 + 创始人真机验收，符合约定）✓

### 3.3 主 README 与插件 README 双语一致性、内链有效

- 主 README L105-124 插件章节：双语（安装/功能/薄壳定位/入口指引）✓
- 内链 `[extensions/sillytavern/continuity-st/README.md](extensions/sillytavern/continuity-st/README.md)` 目标文件**存在** ✓；插件 README 引用 `docs/st-launch-plan.md` §1 存在 ✓
- 两处 README 的核心文案（「酒馆内的一键内存体检…数据不出你的电脑」）与 launch-plan 模板一致 ✓

### 3.4 对照计划第 4 节 P4 验收要点

| 计划 P4 验收要点 | 实测 |
|------------------|------|
| 中英双语 README（安装/使用/隐私声明） | ✓ 81 行完整版（1.2） |
| 版本门槛提示 UX | ✓ detectVersionHints（纯能力检测 + 非阻断提示） |
| staging 防御（不依赖 staging 事件） | ✓ grep 0 + 契约断言 |
| docs 指引更新（主 README 插件一节） | ✓ 主 README L105-124 |
| QA 严格三轮审核 | ✓ 本报告 |
| 创始人真实验收步骤（计划 6.2）/ GitHub 按阶段推送 | **待创始人执行（见差距清单）** |

### 3.5 差距清单

| # | 差距 | 属性 |
|---|------|------|
| G1 | 真机 slash API 形状（P3 遗留） | 待创始人真机验收（launch-plan §4.2 五步 + §4.3 审计） |
| G2 | 设置表单字段绑定真机确认 | 同上 |
| G3 | 弹窗策略/浏览器拦截真机确认 | 同上 |
| G4 | 官方内容库收录申请（申请制、审核等待期） | 上市后 T4（launch-plan §3） |
| G5 | 每 ST release 兼容性复验与更新公告 | 持续任务（launch-plan §3 T4） |

### 3.6 发布准备核查

- 许可证 MIT 双写 ✓；README 无 TODO 占位 ✓；隐私声明双语 ✓；无广告/无遥测声明与实现一致 ✓
- 分发前置（GitHub Release + Install from URL）就绪（文件夹结构规范：manifest/settings.html/index.js/checks.js/style.css/README/package.json 齐备）✓

### 与第 2 轮结论比较

- 第 3 轮新增：双语一致性/内链核对（全有效）、P4 要点逐项、G1–G5 差距；无新增退回项。

---

## 4. 三轮总结论与退回清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 + 注释审查 | 通过（node 24/24、pytest 363+1；收录五条全达标） |
| 第 2 轮 安全与十规则审计（真实执行 + 投毒反证 4 组） | 通过（无夸大、零外部、零 staging、零密钥） |
| 第 3 轮 回归与发布审查 | 通过（基线无删减、写作用域合规、双语内链有效） |

### 退回项：**无**

### 观察/建议（非阻塞）

- G1–G3 真机项按 launch-plan §4.2/4.3 由创始人执行（五步验收 + 零出站审计 + 无写路径快照对比 + 合成三样本），证据留档后可复用本报告结论。

**一句话验收建议**：P4 三轮全部通过、无退回项、官方收录五条要求逐条达标——**可以交创始人真机验收**（launch-plan §4 五步 + 审计），通过后即可 commit、GitHub Release 上市（T1），官方内容库申请按 T4 节奏；真机验收中如发现 slash 形状/设置绑定问题（G1–G2）按惯例退回修复。
