# W1+W2 严格复审 — 三轮独立审核报告（创始人强化标准）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定，不沿用此前结论）
> 审核时间：2026-11-06 23:44–24:00
> 审核范围：commit 059e4ee（W1）与 440c723（W2）即 `src/continuity/webui/` 全部 11 个文件 + `tests/test_webui_{server,jobs,validation,api_scan}.py` 4 个测试文件
> 依据：AGENTS.md（最新版，含「团队协作与审核规则」严格模式）、docs/TEAM-COORDINATION.md（第三轮写作用域）
> 方法：第 1 轮逐行审查 + 真实测试；第 2 轮**真实执行攻击路径**（非代码推断，全部留有运行证据）；第 3 轮回归 + 差距清单 + 发布核查。每轮与上一轮结论比较，问题均附「文件:行 + 具体改法」。
> 审核人写作用域：仅本文件与 .tmp 下两个一次性审计脚本（gitignored）；未修改任何源码/测试/文档；未 commit。

---

## 第 1 轮「功能与真实测试 + 逐行审查」

### 1.1 全套 pytest 真实运行（AGENTS.md 固化命令实际执行）

```powershell
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = 'D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'
$env:TMP = 'D:\项目1agent角色平台\.tmp'; $env:TEMP = $env:TMP
& $py -m pytest -v
```

**真实输出（23:44 运行）**：**collected 182 → 181 passed, 1 skipped, 1 warning in 18.77s，退出码 0**
与 AGENTS.md「测试基线：181 passed + 1 skipped（182 collected，真实运行）」完全一致 ✓。
1 skip = 符号链接环境跳过；1 warning = anyio 第三方弃用。webui 相关 78 例（server 20 + jobs 6 + validation 36 + api_scan 15 + 端口新 3 = 78？以实际文件计：api_scan 15、jobs 6、server 20、validation 36 = 77 + 基线其余 105 = 182 ✓）。

### 1.2 逐行审查发现（按文件，全部附具体修改建议）

| # | 位置 | 严重级 | 问题与具体修改建议 |
|---|------|--------|--------------------|
| A1 | `src/continuity/webui/server.py:66-68` | 低 | `JobManager()` 在 `ThreadingHTTPServer(...)` bind **之前**构造：端口被占时 bind 抛 OSError，但工作线程已启动且无人 stop。**改法**：把 `self.jobs = JobManager()` 移到 httpd bind 成功之后；或在 `__init__` 的失败路径补 `self.jobs.stop()`。 |
| A2 | `server.py:80-85` | 低（理论） | `_serving=True` 与 `serve_forever()` 进入循环之间存在微秒级窗口，此时调用 `shutdown()` 仍会短暂阻塞在 `httpd.shutdown()`。**改法**：`serve_forever` 用 try/finally 包裹并置位标志（该回归已有测试 `test_shutdown_without_serve_does_not_hang`，窗口不可实际触发，可仅记录）。 |
| A3 | `server.py:88-95`（协议层，全文件） | **中** | HTTP/1.1 keep-alive + **无任何 socket 超时**：空闲/慢连接永久占用线程（第 2 轮实测证实，见 B13）。**改法**：`_Handler` 设 `timeout = 30`（或强制 `Connection: close`；或覆写 `handle_timeout` 静默关连接）。建议 W3 开工前修复。 |
| A4 | `server.py:198-214 _read_body` | 低 | 多 Content-Length、CL 与实发不符——第 2 轮实测均被 400/断连防御（B8/B9/B10），风险已闭合。**可选改法**：`get_all("Content-Length")` 多值时直接拒绝，防御纵深。 |
| A5 | `server.py:225-244 _handle_scan` + 计划 3 节 | **中（计划一致性）** | 计划文档写「用户提交第二个任务时返回 409 提示排队/等待」，实现为**无限排队**（第 2 轮实测 202×3，见 B12）。**改法（二选一）**：保留排队则更新 webui-plan.md 第 3 节；或实现 409（队列非空时拒绝）。推荐保留排队并补队列上限（见 A7）。 |
| A6 | `src/continuity/webui/jobs.py:120-121, 38-50` | 低 | 任务状态字段（state/started_at）在 worker 线程**锁外**写入；读侧 `to_dict()` 在锁内读多个字段，可能读到中间态快照（state=running 且 started_at=None）。**改法**：worker 中状态变更移入 `with self._lock`。 |
| A7 | `jobs.py:74-82` | **中** | `_jobs` 与队列**无上限**：恶意/误操作可无限提交堆积任务（内存 + 串行执行拖延）。**改法**：`submit` 前检查队列长度上限（如 64），超限抛专用异常由 server 映射 429/409。 |
| A8 | `server.py`（socketserver 层） | 低 | 客户端粗暴断连时 socketserver 向 stderr 打印**完整 traceback**（第 2 轮实测大量出现）——日志噪音、可被刷屏。**改法**：覆写 `ThreadingHTTPServer.handle_error`，对 ConnectionReset/Aborted/BrokenPipe 静默（debug 级）。 |
| A9 | `static/app.js:11-17, 68-84` | 低 | `api()`/`pollJob` 的 fetch **无 .catch**：服务器关闭时产生 unhandled promise rejection，界面无提示。**改法**：`api()` 末尾补 `.catch(() => ({error: "无法连接服务器"}))`。 |
| A10 | `README.md:114-117` | **中（发布）** | README 正文写「179 collected = 178 passed + 1 skipped」，与 440c723 commit message「181 passed + 1 skipped」及真实基线（182=181+1）**自相矛盾**（双语更新时数字未同步）。**改法**：更新为「182 collected = 181 passed + 1 skipped」。 |
| A11 | `views.py:16`（scan 响应 `root`）、错误信息 | 低 | 绝对路径进入响应/错误（本地单用户、与 CLI 一致；计划 R5 已有 W7 折叠对策）。不改，记录。 |

其余逐行结论：token 生成/compare_digest、Host 白名单、CSP/nosniff/DENY、静态 resolve 二次校验、MIME 白名单、`_read_body` 上限+断连、202/400/403/404/503 状态码、jobs 串行/异常透传/停止收口、validation 形状校验、views 枚举转 value、history JSONL 只存元数据、前端全 textContent——**均正确，无新问题**。

### 1.3 与上一轮（W2 宽松审核）结论差异比较

- 上轮「通过、无退回项」基于行为核查；本轮逐行审查**新增发现 A1/A2/A6/A7/A8/A9/A10 共 7 项**（上轮未覆盖的边界/竞态/资源/文档一致性），确认 A3/A5 为上轮已观察项的**实锤升级**（实测证据见第 2 轮）。
- 440c723 相对 W2 审核时的净增量（默认端口 8777、`_serving` 修复 + 3 例回归测试）逐行核对**正确**；`test_shutdown_without_serve_does_not_hang` 是对真实 bug 的有效回归锁定 ✓。

**第 1 轮结论：功能与真实测试通过（181+1 全过）；逐行审查发现 11 项问题（2 中 + 9 低），其中 A3/A5/A7/A10 列为退回修复项（见第 4 节）。**

---

## 第 2 轮「安全与十规则审计 — 真实执行攻击路径」

全部攻击对**真实运行**的 WebUIServer（127.0.0.1 随机端口、真实线程）执行，脚本 `.tmp/reaudit_attack.py` / `.tmp/reaudit_attack2.py`（一次性，gitignored）。证据为实际运行输出。

| # | 攻击路径 | 实测结果 | 判定 |
|---|----------|----------|------|
| B1 | 无 token GET /api/health | **403** TokenError | 防御 ✓ |
| B2 | 错 token | **403** TokenError | 防御 ✓ |
| B3 | Host: evil.example | **400** SecurityError | 防御 ✓ |
| B4 | Host: 127.0.0.1:9999 | **200**（白名单任意端口，设计如此） | 记录（可接受） |
| B5 | 无 Host（HTTP/1.0 风格） | **400** | 防御 ✓ |
| B6 | 静态穿越 8 变体（`..%5c..%5c`、`....//`、`//`、`./`、`%2e%2e`×2、`%00`、绝对路径 `C:/...`） | 全部 **404** | 防御 ✓ |
| B7 | 超大请求体 70000 字节 + 同连接复用 | **400** 且连接被关（复用抛 ConnectionAborted） | 防御 ✓（断连逻辑真实生效） |
| B8 | 畸形 Content-Length（abc / -5 / 缺失 / 99999999999） | 全部 **400** | 防御 ✓ |
| B9 | 请求走私尝试（CL=5 实发 100B + 拼接第二条合法请求） | 多余字节被解析为坏请求 → **400**，第二条**未执行** | 防御 ✓ |
| B10 | 双 Content-Length 头 | **400**（标准库拒绝） | 防御 ✓ |
| B11 | 并发 10 线程同时提交扫描 | 全部 **202**，最终全部 **succeeded** | 线程安全 ✓ |
| B12 | 同源重复提交 ×3 | **202×3** 排队执行——**与计划文档「409」不一致**（A5 实锤） | 计划差异 ⚠ |
| B13 | slowloris：10 个慢连接（声明 CL=100 不发 body）占线 | 正常请求 health=200 仅 **2ms**（不受阻塞）；但服务器线程数=14，**10 个慢连接各占 1 线程且无读超时**——资源可被耗尽（A3 实锤） | 资源面 ⚠ |
| B14 | Transfer-Encoding: chunked（无 CL） | **400** | 防御 ✓ |
| B15 | GET /static/index.html（token 注入绕过） | **404**，响应体无 `__CONTINUITY_TOKEN__` 占位符 | 防御 ✓ |
| B16 | 客户端粗暴断连（反复 RST） | 服务器存活，但 socketserver 向 stderr 打印**完整 traceback 数十条**（A8 实锤：日志刷屏面） | 日志噪音 ⚠ |

### 十条规则逐条（对照攻击证据）

| 规则 | 判定 | 证据 |
|------|------|------|
| 1 源只读/新目录输出 | ✓ | scan 无任何写；源零写入快照测试；require_new_output_dir 预检（W3+ 复用） |
| 2 默认不上传 | ✓ | src 零出站 grep 0 + B3/B4 访问控制；README 双语承诺 |
| 3 不执行导入内容 | ✓ | 前端全 textContent（grep eval/innerHTML 唯一命中为注释）；CSP default-src 'none'；PNG/JSON 解析不执行 |
| 4 R0/R1/R2/R3 分级不伪造 | ✓ | UI 如实展示引擎结论；R1 明示未实现；无越级按钮 |
| 5 动作有日志与差异 | ✓ | job log_tail（统计行，无路径/内容）+ history 骨架；diff 展示 W5 计划内 |
| 6 不删测试/不降断言 | ✓ | 182 collected 全保持；旧测试零 diff；无 assert True |
| 7 先计划阶段停等 | ✓ | W1/W2 均已 commit 并经创始人验收；未越权实现 W3+ 功能 |
| 8 无 NFT/代币/钱包/云端 | ✓ | grep 0 命中（复跑） |
| 9 格式不确定不猜测 | ✓ | validation 仅形状/安全校验，语义全交引擎（docstring 明言） |
| 10 未运行不标通过 | ✓ | 本轮真实运行 182 例 + 15 项攻击实测 |

### 与第 1 轮结论差异比较

- 第 1 轮将 A3/A5 列为「观察项」，本轮以 B13/B12 真实攻击证据**升级为实锤问题**；A8 为第 1 轮未预见的**新增发现**（攻击执行中暴露）。
- 防御面（B1–B11、B14–B15）全部经受真实攻击，无绕过、无回退。

**第 2 轮结论：安全与十规则审计通过（无高危漏洞）；新增实锤 3 项（A3 资源耗尽面、A5 计划 409 不一致、A8 日志刷屏面），列入退回修复项。**

---

## 第 3 轮「回归与发布审查」

### 3.1 全量回归

- 182 collected = 181 passed + 1 skipped（真实运行，与 AGENTS.md/commit message 一致）✓
- 无删除/无降低/无硬编码：旧测试零 diff；440c723 新增 3 例（shutdown 回归、默认端口签名、help 文案）为真实断言 ✓
- 写作用域：git 核对 developer 变更全部在 `src/continuity/webui/` + 约定测试文件；工作区当前仅 `M AGENTS.md`、`M docs/TEAM-COORDINATION.md`（lead/外部会话未提交的规则更新，正常）✓

### 3.2 与企划书提示词 8 主流程差距清单（选源→扫描→查看问题→预览修复→选目标→生成→验证→导出报告）

| 步骤 | 现状（W1+W2 复审后） | 差距程度 | 对应阶段 |
|------|----------------------|----------|----------|
| 1 选源 | 扫描页文本输入框（手输路径）| 部分实现：无目录浏览/最近使用（可用性项）| W7 打磨 |
| 2 扫描 | 完整实现（端点+队列+UI+等价测试）| **已实现** | W2 ✅ |
| 3 查看问题 | findings/重复/符号链接展示（textContent 安全渲染）| **已实现**（diff 查看器属修复阶段）| W2 ✅ / W5 |
| 4 预览修复 | 未实现（R0/R2/R3 展示 + diff 查看器计划中）| 未实现，差 W5 | W5 |
| 5 选目标 | 未实现（输出目录输入；validation 预检函数已就绪可复用）| 未实现，差 W3 起 | W3–W6 |
| 6 生成（备份/恢复/修复副本/迁移产物）| 未实现（引擎与 CLI 已就绪，仅缺 Web 端点）| 未实现，差 W3/W4/W5/W6 | W3–W6 |
| 7 验证 | 未实现（引擎 verify/迁移验证已就绪）| 未实现，差 W3/W6 | W3/W6 |
| 8 导出报告 | 未实现（引擎 JSON 报告落盘已有；独立 HTML 报告另线未开工）| 未实现，差 W7+（HTML 报告线待立项）| W7+ |

**差距结论**：8 步中 2 步完整实现、1 步部分实现、5 步未实现——与 W3–W7 阶段划分完全对应，**W1+W2 阶段目标无差距**（阶段验收要点全部达成）；主流程整体差距属计划内待开发。

### 3.3 发布准备核查

| 项 | 结果 |
|----|------|
| README 中英双语 | ✓ 全文双语（标题/承诺/快速开始/CLI/WebUI/测试/进度/目录/限制/边界声明） |
| README 测试数字 | ✗ **过时**（写 179/178，实际 182/181+1；与 440c723 commit message 矛盾）→ A10 退回修正 |
| 默认端口 8777 | ✓ 创始人裁决已落地（server/__main__/README/测试四处同步；8765 被 baidupinyin 占用有实测） |
| 端口冲突优雅降级 | ✓ 实测（占用 8766 → 友好报错 + 退出码 2） |
| GitHub 推送 | ✓ AGENTS.md 记录已推送（凭据走环境变量，未入源码/日志——grep 无凭据痕迹） |
| 变更日志 | ⚠ CHANGELOG.md 尚无 W1/W2 条目（产品级变更记录留待创始人排期，记录） |

### 与第 2 轮结论差异比较

- 第 3 轮新增：README 数字矛盾（A10 升级为退回项）、CHANGELOG 未记 W1/W2（记录项）、主流程差距量化表（8 步 2 完成/1 部分/5 未实现）。
- 第 2 轮安全结论不变：无高危漏洞，3 项实锤问题延续至退回清单。

---

## 4. 三轮总结论与退回修复清单

| 轮次 | 结论 |
|------|------|
| 第 1 轮 功能与真实测试 + 逐行审查 | 通过（181+1 全过）；发现 11 项问题 |
| 第 2 轮 安全与十规则审计（真实攻击执行） | 通过（无高危漏洞）；实锤 3 项 |
| 第 3 轮 回归与发布审查 | 通过（主流程差距均属计划内 W3–W7） |

### 需退回 developer 修复的问题清单（修复后复审，再交创始人）

| # | 严重级 | 问题 | 具体修改建议（文件:行 + 改法） |
|---|--------|------|-------------------------------|
| A3 | 中 | 空闲/慢连接永久占线程（slowloris 面，实测 threads=14） | `server.py:88` `_Handler` 增加 `timeout = 30`（或强制 Connection: close / 覆写 handle_timeout）——W3 开工前修 |
| A5 | 中 | 重复提交无限排队，与计划「409」矛盾 | `server.py:225-244`：队列非空时返回 409（或改计划文档为排队语义）；实测 202×3 需变为有界行为 |
| A7 | 中 | 任务队列与 _jobs 无上限，可堆积耗尽资源 | `jobs.py:74-82` `submit` 增加队列上限（如 64），超限抛异常并由 `_handle_scan` 映射 429/409 |
| A8 | 低 | 客户端断连打印完整 traceback（刷屏面） | 覆写 `ThreadingHTTPServer.handle_error`：对 ConnectionReset/Aborted/BrokenPipe 静默为 debug 日志 |
| A10 | 中（发布） | README 测试数字过时且与 commit message 矛盾 | `README.md:114-117` 更新为「182 collected = 181 passed + 1 skipped」 |

### 改进建议（非阻塞，建议随 W3 一并处理）

A1（JobManager 构造顺序）、A2（_serving 窗口，理论）、A4（CL 多值纵深防御）、A6（jobs 状态锁内写）、A9（app.js fetch catch）、A11（绝对路径展示，W7 折叠计划已有）、CHANGELOG 补记 W1/W2。

**一句话结论**：W1+W2 功能、安全、回归三轮全部通过、无高危漏洞，但严格模式发现 5 项需退回修复（2 个中危资源/一致性 + 3 个低/发布项），建议 developer 按上述「文件:行 + 改法」修复并补 2–3 个回归测试（队列上限、断连静默、超时）后复审，通过即可交创始人验收与 W3 开工。

---

## 5. 修复复审（developer 修复后复检，2026-11-06 深夜追加）

### 5.1 全套 pytest 真实运行（AGENTS.md 固化命令）

**真实输出：collected 187 → 186 passed, 1 skipped, 1 warning in 22.70s，退出码 0**
与 developer 自称「187 collected = 186 passed + 1 skipped」一致 ✓。
构成：api_scan 16（+1）、jobs 8（+2）、server 22（+2）、validation 36、其余基线 105 不变 → 净增 5 例 ✓。

### 5.2 五项退回修复逐项验证（读代码 + 真实执行证据）

| # | 修复内容 | 代码证据 | 真实执行证据 | 结论 |
|---|----------|----------|--------------|------|
| A3 | 连接超时 30s | `server.py:77` 参数 `connection_timeout: float = 30.0`；`setup()`（:118-121）`self.connection.settimeout(...)`；TimeoutError 列入 `_route` 静默（:152） | 独立实证 F2：`connection_timeout=1.0` 服务器空闲连接 **1.01s 被关闭**（recv=b""），随后 health 200 服务存活；默认值 30.0 已核对 | ✅ 落地 |
| A5 | 忙碌 409 | `jobs.py:22-25` `JobQueueFullError`；`submit`（:94-95）任一 job 在 queued/running 即抛；`server.py:269-272` 映射 **409 JobsBusy** | 独立实证 F1：任务 running 时第二次 POST → **409 JobsBusy**；任务结束后再提交 → **202** 且 job 最终 **succeeded** | ✅ 落地 |
| A7 | 完成保留上限 64 | `jobs.py:21` `MAX_FINISHED_JOBS = 64`；`_prune_locked`（:150-158）worker finally 持锁修剪，按 finished_at 保最近 64 | `test_finished_jobs_pruned_to_cap` 真实提交 70 任务 → 字典 ≤64 ✓ | ✅ 落地 |
| A8 | 断连静默 | `_QuietThreadingHTTPServer.handle_error`（:57-67）只记一条 debug；500 分支由 `logger.exception` 改 `logger.error("%r")` 不再打 traceback | 独立实证 F3：真实 RST 断连（SO_LINGER 1,0）后 **stderr 0 字节、无 Traceback**，服务器存活 200（对照：修复前同场景实测刷出数十条完整 traceback） | ✅ 落地 |
| A10 | README 数字 | `README.md:114-117` 改为「187 collected = 186 passed + 1 skipped」中英双语同步 | 与本次真实运行 187/186+1 一致 ✓ | ✅ 落地 |
| — | plan 文档同步 | `webui-plan.md` 第 3/4.2/5 节补充 409（JobsBusy）语义、30s 超时、断连静默表述 | 与实现一致 ✓ | ✅ 落地 |

### 5.3 回归核对

- 既有防御测试（token/Host/穿越 8 变体/超大 70k 体断连/畸形 CL/双 CL/chunked/静态 index 绕过/并发/错误路径）全部包含在全量 187 例中且**全部通过**，无回退 ✓
- **测试变动如实标注**：原 `test_serial_execution_and_order`（锁定「无限排队」旧语义）被替换为 `test_second_submit_rejected_while_active`（锁定新 409 语义）+ 新增 `test_submit_after_completion_ok`——**替换 1 例 + 净增 5 例**。该替换是行为语义按计划文档（409）变更的**必要修改**，新测试断言强度不低于旧测试，不构成「删除测试/降低断言」；但严格意义上「原 182 基线无删减」的说法应表述为「1 例按新语义替换、其余全保留、净增 5」。
- 新增 5 例均为真实断言：真实 HTTP 409 往返、真实 70 任务修剪、真实空闲 socket 超时关闭（0.5s 专用 fixture）、真实 RST + capsys 断言 stderr 无 Traceback、完成后可再提交 ✓

### 5.4 遗留项（非阻塞，上轮已标注为改进建议，建议随 W3 处理）

- A1（`server.py`：JobManager 构造先于 httpd bind，端口占用时工作线程未显式 stop）
- A2（`_serving` 理论窗口）、A4（Content-Length 多值纵深防御）、A6（jobs 状态锁内写）、A9（app.js fetch 无 catch）
- CHANGELOG 尚无 W1/W2 条目（待创始人排期）

### 5.5 复审结论

**修复复审通过：5 项退回全部落地并各有真实执行证据，无回归、无新问题。**
可以提交创始人验收，并由创始人执行 Git commit（连同 docs/webui-plan.md、README.md 与三个测试文件的修复改动）。

