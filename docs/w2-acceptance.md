# W2 验收清单 — 扫描模块（developer 交付三轮独立审核）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定）
> 审核时间：2026-11-06 23:17–23:30（三轮审核，真实运行测试）
> 依据：AGENTS.md（最新版）、docs/TEAM-COORDINATION.md（第三轮写作用域 + 创始人三轮审核制新指令）、docs/webui-plan.md 第 6 节 W2 行
> 审核人写作用域：仅本文件；未修改任何源码/测试/其他文档；未 commit。

## 第 1 轮「功能与真实测试」

### 1.1 全套 pytest 真实运行（AGENTS.md 固化命令实际执行）

```powershell
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = 'D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'
$env:TMP = 'D:\项目1agent角色平台\.tmp'; $env:TEMP = $env:TMP
& $py -m pytest -v
```

**真实输出（23:17 运行，Python 3.14.5 + pytest 9.2.0/.deps2）**：

- **collected 179 → 178 passed, 1 skipped, 1 warning in 18.59s，退出码 0**
- 明细：旧 12 文件 163 通过+1 跳过（基线保持 ✓）+ **test_webui_api_scan 15 例全过**
- 与 developer 汇报「178 passed + 1 skipped」完全一致 ✓
- 1 skipped（符号链接环境跳过）、1 warning（anyio 第三方弃用）与基线相同
- 运行前确认无并发 pytest 进程；webui 测试用 port=0 随机端口，无 basetemp/端口冲突

### 1.2 W2 定向 15 例核对（tests/test_webui_api_scan.py）

| 用例 | 断言要点 | 真实性判定 |
|------|----------|-----------|
| test_scan_job_matches_direct_engine_call | `snap["result"] == scan_report_to_json(scan_directory(tree))` **逐字段等价比对**（含枚举转字符串）；log_tail 精确匹配统计行 | ✅ 真实引擎等价断言 |
| test_scan_source_stays_untouched | 扫描前后 `_snapshot_tree`（相对路径→SHA-256）完全相等 | ✅ 真实源零写入断言 |
| test_scan_chinese_filenames | 中文路径样本（角色卡.json/.png）在响应中 | ✅ |
| test_scan_findings_and_duplicates | 坏 JSON（r2 发现）、空文件（info）、重复组与直接引擎调用等价 | ✅ |
| 错误路径 11 例 | 源缺失 400 / 源为文件 400 / 空值 400 / 缺键 400 / 非法 JSON 400 / 非对象 400 / 超限体 400 / 空体 400 / 未知任务 404 / 无令牌 403 / 队列停止 503 | ✅ 全分支 |
| 无 mock | 真实服务器（随机端口真实线程）+ http.client 真实请求 + 真实 scan_directory；全文无 mock 引擎、无 `assert True`、无跳过装饰器 | ✅ |

### 1.3 git 核对（只读命令）

- `git log`：W1 已由创始人 commit（059e4ee，23:09:15）
- `git diff 059e4ee --stat`：7 个文件改动 +357/-14，**全部位于 `src/continuity/webui/` 名下**（api.py、server.py、views.py、validation.py、static/app.js、static/index.html、static/style.css）；新文件 `tests/test_webui_api_scan.py`（未跟踪）；`docs/research-community.md` 属 researcher 写作用域
- **零修改任何现有测试/现有核心源码**（src/continuity 其他子包、tests 旧 12 文件均无 diff）✓
- 备注：developer 汇报「变更 6 个 webui 文件」，git 实测 7 个（少计 views.py）——汇报精度偏差，非代码问题（观察项 O1）

**第 1 轮结论：通过，无退回项。**

## 第 2 轮「安全与十规则审计」（攻击者视角）

| 审计项 | 实测结果 | 证据 |
|--------|----------|------|
| 新端点 token 覆盖 | `/api/jobs/scan` 与 `/api/jobs/<id>` 均在 `_token_ok()` 之后分发；无 token 403 有直接测试 | `server.py:195-198`（前置校验）；`test_scan_requires_token_403` |
| Host 白名单未回退 | `_route` 最前置仍为 `host_is_allowed`（400 SecurityError）；W1 相关测试全保持 | `server.py:105-115`；test_webui_server.py 5 例 |
| 静态穿越未回退 | 静态服务逻辑未动；W1 穿越 4 变体测试全保持 | `server.py:161-184`；test_webui_server.py |
| 64KiB 请求体上限 + 超限断连 | `_read_body`：Content-Length 非法/负数拒绝；`length > MAX_BODY_BYTES` → `close_connection = True` + 400（未读的超限体不污染下一条请求解析） | `server.py:198-214`；`test_scan_oversized_body_400`（70000 字节实测 400） |
| job 日志不含路径/文件内容 | `scan_worker` 唯一 log 行 =「扫描完成: N 个文件，M 项发现」纯统计；log_tail 上限 200/50；测试精确断言 log_tail 内容 | `api.py:29-41`；`jobs.py:38-50, 97-98`；test 断言 L121 |
| src 零出站网络 | grep `urllib.request/socket/requests/httpx/http.client` 于 `src/continuity/webui/*.py` **0 命中**（复跑） | grep 0 |
| 前端无 innerHTML/eval + CSP | 新增 app.js 全部 `textContent`/`createTextNode`；grep `eval/innerHTML/outerHTML/document.write/new Function` 唯一命中为注释；CSP（`script-src 'self'` 无 unsafe-inline）未回退；style.css 无 @import/url( 外部资源 | grep 复核；app.js:69-96 |
| 源只读 | `scan_worker` 仅调用只读 `scan_directory`；源零写入有 SHA-256 快照测试 | `test_scan_source_stays_untouched` |
| 输出目录预检 | W2 无输出目录概念；`require_new_output_dir`（W1 已测 5 例）保持，W3+ 复用 | test_webui_validation.py |
| 错误路径全分支 | 400/403/404/503/202/200 全部有测试；引擎异常（ScanError/OSError）由 JobManager 捕获为 failed 透传 | test_webui_api_scan.py 11 例；`jobs.py:126-129` |
| 无 NFT/钱包/代币/云端/upload | grep 全 src/webui（py+js+html）**0 命中**（复跑） | grep 0 |
| 端口冲突优雅降级 | **实测**：占用 8766 后调用 `main(["--port","8766","--no-browser"])` → 友好错误「无法监听 127.0.0.1:8766（…）」+ **退出码 2** ✓；8765 实测被 `baidupinyin`（PID 24376，0.0.0.0:8765 常驻，2026-10-24 起）占用，bind 8765 被系统拒绝（10013）——印证 developer 汇报属实 | 实测；`__main__.py:29-31`；netstat |

**第 2 轮结论：通过，无退回项。** 观察项：`_read_body` 无 socket 读取超时（慢速发送可占线程；本地单用户 + 超限断连已缓解，建议列入 W7 打磨，O3）。

## 第 3 轮「回归与发布审查」

### 3.1 全量回归数字核对

- 179 collected = 178 passed + 1 skipped = 基线 163 passed + 1 skipped（W1 全保持）+ 新增 15 例 ✓
- 无删除、无降低、无硬编码：旧 12 个测试文件零 diff；新 15 例断言均为真实行为断言（等价比对/快照/异常/状态码）

### 3.2 写作用域与 git 状态核对

- developer 变更全部落在其写作用域（`src/continuity/webui/` + `tests/test_webui_api_scan.py` 新文件）✓
- docs 下仅 `docs/research-community.md`（researcher）为新增，属正常；`docs/TEAM-COORDINATION.md` 第三轮版已随 W1 commit（059e4ee，23:09:15）提交，工作区无漂移 ✓
- 未 commit 状态与 founder 授权一致（等待三轮审核结论）

### 3.3 对照 webui-plan.md 第 6 节 W2 验收要点逐项确认

| 计划 W2 验收要点 | 实测 |
|------------------|------|
| 对合成样本目录真实扫描 | `make_st_sample_tree` 合成样本经真实 HTTP + 真实引擎扫描 ✓（3 例） |
| 响应与直接调用 `scan_directory` 结果一致 | `snap["result"] == scan_report_to_json(scan_directory(tree))` 逐字段等价 ✓（3 例） |
| 源目录零写入 | 前后 SHA-256 快照相等 ✓（1 例） |
| 交付内容（扫描页 + `POST /api/jobs/scan` + 类型统计/findings/重复/符号链接展示） | index.html 扫描页表单/结果区 + app.js 渲染（textContent）+ server.py 端点 + views.py 序列化 全部就位 ✓ |

### 3.4 占位功能排查

- W3–W7 页面（备份/校验/恢复/修复/迁移/历史）仍为「阶段 Wx 开放」占位文案，**未越权实现** ✓
- API 仅 health/version/jobs/scan/jobs/<id>；backup 等端点请求 → 404（无越权）✓
- views.py 仅 ScanReport 序列化，未提前实现其他引擎适配 ✓

### 3.5 风险汇总

| 编号 | 风险/发现 | 等级 | 说明与建议 |
|------|-----------|------|-----------|
| R1 | **默认端口 8765 被 baidupinyin 常驻占用（0.0.0.0:8765，PID 24376）** | 环境项（非代码缺陷） | 已实测确认；入口优雅降级（友好报错 + 退出码 2）实测通过；建议创始人使用 `--port 其他端口`，或裁决是否更换默认端口（改 __main__.py 默认值需 developer 执行，属后续任务） |
| R2 | scan 响应 `root` 字段与错误信息含绝对路径 | 低（本地单用户，与 CLI 行为一致） | 计划 R5 已有 W7 折叠展示对策；隐私合规不受影响（本机单用户，无上传） |
| R3 | `_read_body` 无 socket 读取超时 | 低 | 慢速发送可占线程；ThreadingHTTPServer 每连接一线程 + 超限断连已缓解；建议 W7 加超时 |
| R4 | developer 汇报「6 个 webui 文件」与 git 实测 7 个不符（少计 views.py） | 汇报精度 | 提醒 developer 变更清单以 git 为准 |
| R5 | webui-plan.md 第 5/8 节基线数字「103 passed + 1 skipped」仍为错误值（W1 审核已提，未修正） | 文档 | 建议 developer 顺手修正为「104 passed + 1 skipped = 105 collected」 |
| R6 | 全套测试耗时 18.59s（较 W1 10.84s 增） | 正常 | 新增 15 例含真实服务器/引擎与轮询等待，无挂起泄漏 |

## 4. 三轮结论汇总

| 轮次 | 结论 | 退回项 |
|------|------|--------|
| 第 1 轮 功能与真实测试 | **通过** | 无 |
| 第 2 轮 安全与十规则审计 | **通过** | 无 |
| 第 3 轮 回归与发布审查 | **通过** | 无（附 6 项风险/观察项，均不阻塞） |

**验收建议（一句话）**：W2 通过，可以提交创始人验收并 commit——三轮审核全部通过、无退回项；建议创始人启动时用 `--port` 避开 8765（百度输入法占用），并将默认端口是否更换交由创始人裁决（R1）。
