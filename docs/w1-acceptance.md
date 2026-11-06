# W1 验收清单 — WebUI 骨架与基础设施（developer 交付独立审核）

> 审核方：qa-reviewer（与 developer 严格分离，独立判定）
> 审核时间：2026-11-06 22:32（真实运行测试后出具）
> 依据：AGENTS.md（最新版）、docs/TEAM-COORDINATION.md（第二轮写作用域）、docs/webui-plan.md 第 3 节（架构）与第 6 节（W1 验收要点）、方案甲裁决（tests/ 下新增、绝不改旧文件）
> 审核人写作用域：仅本文件；未修改任何源码/测试/其他文档；未 commit。

## 0. W1 验收范围

对照 webui-plan.md 第 6 节 W1 行与第 3 节架构，W1 交付应含：

| 交付项 | 计划要求 | 实测存在 |
|--------|----------|----------|
| webui 包 | `__init__/__main__/server/api/jobs/history/views/validation.py` + `static/index.html + app.js + style.css` | 11 个文件全部存在（`src/continuity/webui/`） |
| 入口 | `python -m continuity.webui`，仅绑定 127.0.0.1，默认端口 8765 | `__main__.py` ✓（--port/--no-browser） |
| W1 实测要点（计划 6 节） | 沙箱内 127.0.0.1 真实监听成功；health 200；无 token 403；静态路径穿越 404；服务器可正常关闭 | 全部真实实测 ✓（见第 2 节） |

## 1. 真实测试执行记录（AGENTS.md 固化命令，实际运行）

```powershell
$py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
$env:PYTHONPATH = 'D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'
$env:TMP = 'D:\项目1agent角色平台\.tmp'; $env:TEMP = $env:TMP
& $py -m pytest -v
```

**真实输出（2026-11-06 22:32 运行，Python 3.14.5 + pytest 9.2.0/.deps2）**：

- **collected 164 items → 163 passed, 1 skipped, 1 warning in 10.84s，退出码 0**
- 明细：test_adapter 14、test_backup_engine 21 通过+1 跳过、test_cli 8、test_filetype 11、test_manifest 15、test_migration 14、test_pngutil 6、test_repair 9、test_scan 6、**test_webui_jobs 6、test_webui_server 17、test_webui_validation 36**
- 基线核对：0.1.3 基线 104 passed + 1 skipped **全部保持** ✓；新增 59 例（6+17+36）**全部通过** ✓；与「164 collected = 163 passed + 1 skipped」完全一致
- 1 skipped 不变（符号链接环境条件跳过）；1 warning 不变（anyio 第三方弃用警告）
- 运行前确认：无并发 pytest 进程占用 basetemp（当时有一个空闲 python 进程 117920，见风险 R2，与本次运行无冲突；webui 测试全部用 port=0 随机端口）

**结论：通过。** W1 计划最大环境风险「沙箱内 127.0.0.1 真实监听」实测成功。

## 2. 计划 W1 验收要点逐项实测

| 验收要点（计划 6 节） | 检查内容与实测结果 | 证据 | 结论 |
|----------------------|--------------------|------|------|
| 真实监听 127.0.0.1 | 测试 fixture 用 `WebUIServer(port=0)` 随机端口 + 真实线程 `serve_forever()`，teardown `shutdown()+join(5)`；服务器正常启动/关闭，端口释放干净（全套 10.84s 无挂起） | `test_webui_server.py:18-29`（fixture） | ✅ |
| health 200 | 真实 HTTP 请求返回 `{"status":"ok"}` | `test_health_ok`（:51-54） | ✅ |
| 无 token 403 | 缺 token 与错 token 均 403 + `kind=TokenError`；服务端用 `secrets.compare_digest` 防时序攻击 | `test_api_without_token_403`、`test_api_wrong_token_403`；`server.py:188-193` | ✅ |
| Host 白名单 | evil.example → 400 SecurityError；127.0.0.2 / localhost.evil / [::1] → 400；localhost:port → 200 | `test_host_whitelist_*`（:80-97）；`validation.py:57-66` | ✅ |
| 静态路径穿越 404 | 4 种变体（`../`、`..%2F`、`%2e%2e%2f`、`sub/../`）全部 404；`resolve()+is_relative_to` 二次校验 + 目录成分/反斜杠一律拒绝 | `test_static_traversal_rejected`（:131-143）；`server.py:161-178` | ✅ |
| 服务器可正常关闭 | fixture teardown 实测 | `test_webui_server.py:27-29` | ✅ |
| 额外：安全头 | CSP `default-src 'none'`+`script-src 'self'`、nosniff、X-Frame-Options DENY、no-referrer、no-store；token 经 meta 注入且占位符被替换 | `test_index_served_with_token_and_csp`（:102-112）；`server.py:42-52, 136-148` | ✅ |
| 额外：静态 index 不可绕过 | `/static/index.html` 直读 404（防泄露未注入 token 的原始页面） | `test_static_index_not_bypassable`（:146-150）；`server.py:167` | ✅ |
| 额外：jobs 串行队列 | 门闩实测第二个任务在第一个结束前保持 queued；状态机 queued→running→succeeded/failed；异常捕获为 failed 不拖垮线程；日志缓冲 log_tail；stop 后拒绝提交 | `test_webui_jobs.py` 6 例（:31-107）；`jobs.py` | ✅ |
| 额外：入参校验 | 路径非空/类型/控制字符（NUL 等）、源目录存在且为目录、输出目录不存在+不得在源内、Host 白名单 5 允许/8 拒绝、JSON 体上限/非对象/空体 | `test_webui_validation.py` 36 例；`validation.py` | ✅ |

## 3. 写作用域与 git 核对（只读命令）

- `git status --short`：developer 交付 = `?? src/continuity/webui/` + `?? tests/test_webui_jobs.py` + `?? tests/test_webui_server.py` + `?? tests/test_webui_validation.py`——**仅新增，零修改任何现有文件** ✓（`M docs/TEAM-COORDINATION.md` 属 lead、`M docs/acceptance-checklist.md` 属本审核人上一轮，正常）
- `__pycache__/` 已被 .gitignore 覆盖，不出现在 status ✓
- 未改动 pyproject.toml / conftest.py / 现有 tests（方案甲「绝不改旧文件」遵守）✓
- 零新增运行时依赖：webui 全部 `import` 均为标准库（http.server/threading/queue/secrets/pathlib/json/urllib.parse/webbrowser/argparse）✓（计划方案 A 落实）

## 4. AGENTS.md 十条规则与安全设计抽查（新代码）

| 检查项 | 实测结果 | 证据 |
|--------|----------|------|
| 仅绑 127.0.0.1 | `ThreadingHTTPServer(("127.0.0.1", port), ...)` 硬编码，无监听其他地址的选项 | `server.py:68`；grep `0.0.0.0` 0 命中 |
| 随机 token 校验 | `secrets.token_urlsafe(32)` 启动生成；/api/* 一律 `compare_digest` 校验 | `server.py:65, 188-198` |
| Host 白名单防 DNS rebinding | 仅 127.0.0.1/localhost（任意端口），IPv6 字面量拒绝 | `validation.py:15, 57-66` |
| CSP / nosniff / 禁嵌入 | `default-src 'none'` + `script-src 'self'`（无 unsafe-inline）+ `frame-ancestors 'none'` + nosniff + X-Frame-Options DENY | `server.py:42-52, 140-145` |
| 静态服务防路径穿越 | 目录成分/反斜杠拒绝、resolve 后 `is_relative_to` 二次校验、MIME 白名单、无任何「读任意文件」端点 | `server.py:161-184` |
| 前端 textContent | 动态内容全部经 `setText()` 走 `el.textContent`；grep `innerHTML/eval/outerHTML/document.write/new Function` 唯一命中为 app.js 第 3 行**注释**（"禁止 innerHTML / eval"），非代码 | `app.js:19-24`；grep 复核 |
| 无网络出站 | grep `urllib.request/socket/requests/httpx/http.client` 在 `src/continuity/webui/*.py` 0 命中；页面明示「不上传任何角色数据」 | grep 0 命中；`index.html:16, 36` |
| 无账户体系 | grep `password/username/login/账户/密码/登录/auth` 0 命中（计划 5 节明确 MVP 不引入账户） | grep 0 命中 |
| 无 NFT/钱包/云端 | grep `NFT/钱包/代币/区块链/wallet/cloud/upload` 0 命中 | grep 0 命中 |
| 源只读/输出新目录（预检） | `require_new_output_dir` 强制输出不存在 + 不得位于源目录之内（与核心引擎规则一致的双重把关） | `validation.py:40-54` |
| 不猜测格式（规则 9） | validation 只做「形状与安全」检查，语义一律交核心引擎（docstring 明言） | `validation.py:3-6` |
| 不删测试（规则 6） | 全套 164 项真实运行，旧 105 项基线全部保持，新增 59 项为纯增量 | 第 1 节输出 |

**结论：安全设计与规则合规全部达标，无违例。**

## 5. 新测试文件真实性抽查（防 mock 伪装）

- `test_webui_server.py`：**真实服务器**（随机端口 + 真实线程 serve_forever）+ `http.client` **真实 HTTP 请求**（可精确控制 Host/原始路径），无任何 mock；17 例
- `test_webui_jobs.py`：**真实 JobManager 工作线程**（无 mock），门闩事件实测串行语义与顺序断言，失败任务真实抛异常验证透传；6 例
- `test_webui_validation.py`：纯函数入参矩阵，真实文件系统（tmp_path）验证目录关系；36 例
- 三个文件全文 grep：无 `assert True`、无占位断言、无 monkeypatch 引擎装成功、无跳过装饰器；断言均为状态码/响应体/状态机/字节级真实断言
- 计划第 8 节测试策略（随机端口 fixture、urllib/http.client、复用 helpers 不改动、禁止 mock 引擎）全部落实 ✓

**结论：新增 59 例均为真实断言测试，通过。**

## 6. 风险与发现

| 编号 | 风险/发现 | 说明与建议 |
|------|-----------|-----------|
| R1 | **计划文档基线数字错误** | `docs/webui-plan.md` 第 5 节（规则 6 行）与第 8 节写「104 例基线 = 103 passed + 1 skipped」，与实测不符：真实基线为 104 passed + 1 skipped = 105 collected；本次全套 163 passed + 1 skipped = 164 collected。计划文档属 developer 写作用域，建议 lead 协调 developer 修正（不影响 W1 代码质量）。 |
| R2 | 疑似遗留空闲 python 进程 | PID 117920（22:29:44 启动，CPU 累计 0.15s，非 pytest）在审核期间持续存在，疑似 developer 手动启动的 WebUI 服务器或遗留进程；未影响测试（测试用 port=0 随机端口），但建议 developer 确认并关闭，避免占默认端口 8765 与资源。 |
| R3 | Host 白名单接受「localhost:任意端口」 | 设计如此（plan 2.2 表已注明），防 DNS rebinding 依赖 hostname 精确匹配，W1 可接受；如需更严可后续校验端口与服务器端口一致（属 W7 打磨项）。 |
| R4 | job 状态为内存快照，不落盘 | 重启后任务记录丢失；历史落盘（history.py）已就位但 W7 才接入，属计划内演进，W1 可接受。 |
| R5 | 全套测试耗时由 1.65s 增至 10.84s | 服务器启停 + 门闩等待所致，正常；无挂起、无端口泄漏（teardown 全部 shutdown+join）。 |
| R6 | 默认端口 8765 未实测占用情况 | `__main__` 默认端口经 OS 随机分配未实测（测试用 port=0）；R2 进程若占用 8765，手动启动会报错并退出码 2（已有处理），可接受。 |

## 7. 验收结论汇总

| 验收项 | 实测结果 | 结论 |
|--------|----------|------|
| W1 交付物齐备（8 py + 3 static，入口 `python -m continuity.webui`） | 与计划第 3/6 节一致 | 通过 |
| 全套 pytest 真实运行 | **164 collected：163 passed + 1 skipped**，1 warning，10.84s，退出码 0；基线 105 项全保持 + 新增 59 例全过 | 通过 |
| 计划 W1 验收要点（真实监听/health 200/无 token 403/路径穿越 404/可关闭） | 逐项实测通过 | 通过 |
| 写作用域合规（仅新增约定文件，零改现有文件，零新增依赖） | git 核对通过 | 通过 |
| 安全设计抽查（127.0.0.1/随机 token/Host 白名单/CSP/textContent/无出站/无账户/无 NFT） | 全部达标 | 通过 |
| 新测试真实性（真实服务器+真实 HTTP+真实线程，无 mock 装成功，无 assert True） | 59 例全部为真实断言 | 通过 |

**验收建议（一句话）**：W1 通过，可 commit——交付符合计划且安全设计与规则合规全部达标，测试真实通过；建议 commit 前由 developer 顺手修正 webui-plan.md 的基线数字（R1）并关闭遗留 python 进程（R2），不阻塞 W1 本身验收。
