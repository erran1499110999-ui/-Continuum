# AGENTS.md — Continuity Studio 项目规则（对 AI 开发代理的约束）

> 依据《AI 角色连续性平台商业企划书 v1.0（2026-11-06）》第 10–11 章建立。
> 本文件是项目内最高优先级的行为规则；任何任务开始前先阅读本文件。

## 项目目标
本地优先的 AI 角色备份、诊断、修复与迁移工具（工作名 Continuity Studio）。
首个适配客户端：SillyTavern。当前阶段：MVP 0/1（扫描、备份/恢复、修复预览、迁移）。

## 不可违反的规则
1. 原始输入文件只读；任何修复都输出到新目录。
2. 默认不上传用户角色卡、聊天记录、图片、附件或密钥。
3. 不执行导入文件中的脚本、宏、HTML 或扩展代码。
4. 不伪造无法恢复的数据；区分 R0 确定性修复 / R1 推断修复（须确认）/ R2 仅建议 / R3 隔离。
5. 每个迁移/修复动作必须有日志与差异报告。
6. 不删除测试、不降低断言、不用硬编码结果伪装成功。
7. 先计划，再修改；每个阶段完成后停止等待验收。
8. 不擅自添加 NFT、代币、钱包或云端上传功能。
9. 遇到格式不确定时先建立样本和兼容性报告，不猜测字段含义。
10. 任何未实际运行的测试都不得标记为通过。

## 每轮开发循环
1. 阅读本规则与当前任务；
2. 列出计划与将修改的文件，经创始人确认后执行；
3. 只开发一个阶段任务，不同时开发多个大模块；
4. 真实运行测试；输出变更清单、测试结果、已知风险与下一步；
5. 创始人检查；通过后 Git commit，不通过则修复（不得删除测试）。

## 当前状态（2026-11-06）
- 已完成（企划书第 2–8 周全部开发任务 + 三轮外部审查整改 0.1.1/0.1.2/0.1.3）：项目骨架、
  统一数据模型、只读扫描器、备份/恢复引擎、修复预览引擎（R0 自动修复 / R2 建议 / R3 隔离
  + diff 报告）、SillyTavern 迁移适配器与迁移验证报告、CLI、pytest 测试套件（104 例）。
- 进行中：等待创始人验收（阶段一至三 + 0.1.1/0.1.2/0.1.3 审查整改），验收通过后由创始人执行 Git commit。
- 下一步计划：本地 Web UI（提示词 8）→ 可用性测试（第 9–10 周）。

## 环境说明（受限沙箱下的实际运行方式，2026-11-06 验证）
- Python 3.14.5（系统安装，位于 `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe`；
  PATH 中的 `python` 会解析到 WindowsApps 存根而失败，命令中必须使用上述绝对路径）。
- Pydantic 2.13.4（系统已装）；pytest 9.2.0（工作区 `.deps2`，纯 wheel 解压安装，
  新增依赖请复用 `tools/fetch_wheels.py` 并同步 `.gitignore`）。
- 测试运行方式（pyproject 已内置 --basetemp 与 no:cacheprovider）：
  ```powershell
  $py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
  $env:PYTHONPATH = 'D:\项目1agent角色平台\src;D:\项目1agent角色平台\.deps2'
  $env:TMP = 'D:\项目1agent角色平台\.tmp'; $env:TEMP = $env:TMP
  & $py -m pytest
  ```
- 沙箱限制与对策（均已在 pyproject/conftest 固化，勿删）：
  - `mkdir(mode=0o700)` 的目录会被系统上锁（连创建进程都无法访问）→ conftest.py 把 os.mkdir 的 0o700 改写为 0o755；
  - 中文叶子目录名无法列出 → pytest basetemp 固定为 ASCII 路径（--basetemp）；
  - cacheprovider 的原子缓存写入被拒 → 已禁用（-p no:cacheprovider）；
  - pip 在沙箱内无法解包 wheel（临时目录写入被拒）→ 依赖用 `tools/fetch_wheels.py` 直接下载并解压。
- 注意：完全权限模式下安装/创建的产物（如旧 `.deps`）在受限模式下不可访问，需用完全权限清理。
- 依赖安装需逐项经创始人审查；API Key 使用环境变量，不写入源码或日志。
