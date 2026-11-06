# 外部 ChatGPT 审查提示词与审查包说明（external-review-prompt）

> 编制：qa-reviewer（为创始人准备的外部审查材料）｜ 日期：2026-11-07
> 用途：创始人将本项目交由 ChatGPT（或其他外部 AI）审查评判时的**即用提示词**与**审查包打包清单**。
> 依据：AGENTS.md 规则 2（不上传用户数据）、docs/review-guide.md（外部审查说明，2026-11-07 更新版）。

---

## 一、即用提示词（方案 A：GitHub 链接，推荐）

> 使用前提：仓库 `github.com/erran1499110999-ui/-Continuum` 须为 **public**（ChatGPT 无法读 private 仓库）。
> 直接复制下方全文发给 ChatGPT（联网/浏览模式下）：

```text
你是资深第三方软件审查者。请独立审查这个 GitHub 仓库的全部当前代码与文档（含提交历史）：

https://github.com/erran1499110999-ui/-Continuum

【项目背景】
本地优先的 AI 角色备份、诊断、修复与迁移工具（Continuity Studio），首个适配客户端 SillyTavern。
当前交付：核心 Python 引擎（扫描/备份恢复/修复分级 R0-R3/迁移验证）+ CLI + 本地 Web UI
（127.0.0.1 服务、token 鉴权、scan/backup/emergency-backup/restore 端点）+ SillyTavern 前端扩展插件
（内存态体检 H1-H5、唤起、深链引导）+ 前端改版。测试基线 401 collected = 400 passed + 1 skipped
（pytest）+ 24 例 node:test，均真实运行。

【审查标尺】
先读仓库根目录 AGENTS.md（十项不可违反规则 + 团队规则），以它为准绳逐项对照；
再读 docs/review-guide.md（我方的外部审查说明、测试基线清单、结构速览、已知偏差）。

【审查范围边界】
- 重点：核心引擎（src/continuity/ 下 scanners/backup/repair/adapters/migration/webui）、
  插件（extensions/sillytavern/continuity-st/）、前端（src/continuity/webui/static/ 与 preview/）；
- 不要求复跑全部测试（可抽查关键用例）；不评估内部文档的美化程度，只看事实。

【评分标准】
P0：会导致数据损坏、静默丢失、可远程/跨站利用的安全漏洞——每条必须给出可复现路径；
P1：重要缺陷（规则违反、完整性隐患、高风险边界未处理、测试断言失效）；
P2：改进项（健壮性、可维护性、体验、文档与代码不一致）。

【输出格式（五问清单，逐问回答，不要客套）】
1. 分级发现清单：每条 = [级别][文件:行号] 问题描述 + 证据（引用代码原文）+ 具体修改建议；
2. 十项不可违反规则逐条结论（合规/违规/存疑，附证据）；
3. 测试质量判断：401+24 例基线是否真实有效？有无删除/削弱/空转断言？哪些关键路径缺测试？
4. 产品设计判断（以真实用户视角）：如果我是 SillyTavern 用户，你会安装这个插件并使用本地
   Web UI 吗？为什么？三句话内说清「最劝退你的一点」和「最打动你的一点」；
5. 下一阶段（W3 起 / 插件官方收录）最值得优先解决的风险 TOP 3（按后果严重度排序）。

【明确要求】
- 假设一切有罪，直到证据确凿才放行；发现不了问题就直说「未发现」，不要凑数；
- 引用代码时给出文件路径与行号，便于我方核对；
- 最后用一句话给出总评（可上线 / 有条件上线 / 不建议）。
```

---

## 二、方案 B：打包 zip 上传（无联网读取时的备选）

### 2.1 审查包文件清单

| 目录/文件 | 内容 | 备注 |
|---|---|---|
| `src/` | 全部 Python 源码（引擎 + CLI + webui） | 含 static 前端三件套 |
| `extensions/` | 插件全部文件（含 checks.test.mjs） | — |
| `tests/` | pytest 16 个测试文件 + conftest/helpers | — |
| `preview/` | 风格预览页（v2 演示，非产品运行代码） | — |
| `tools/` | fetch_wheels.py（开发用） | — |
| `samples/synthetic/` | 合成样本生成器与产物 | **纯合成，无真实用户数据** |
| `AGENTS.md` | 十项不可违反规则 + 团队规则（审查标尺） | 必带 |
| `CHANGELOG.md` | 全量变更日志（0.1.0–0.1.3、W1/W2、P1–P5） | 必带 |
| `README.md` | 双语产品说明 | 必带 |
| `docs/` | review-guide.md + 计划/调研/验收档案全套 | 必带（review-guide 是审查入口） |
| `pyproject.toml`、`.gitignore` | 工程配置 | 必带 |
| `business-plan-text.txt` | 企划书原文提取 | **是否纳入由创始人决定**；不纳入则删除后再打包 |

### 2.2 明确排除（不得进入审查包）

- `.tmp/`（含全部审核临时脚本、攻击实证脚本、快照）、`.deps2/`、`__pycache__/`、`.pytest_cache/`、`.git/`；
- 任何真实用户数据（角色卡、聊天记录、图片、附件、密钥、凭据）——本项目当前**没有任何真实用户数据**，
  样本全为程序化合成（规则 2 合规）；
- 私有/个人文件（如 `_docx_text.txt` 之外的任何非项目文件）。

### 2.3 打包命令参考（PowerShell，在仓库根目录执行）

```powershell
$exclude = @('.git', '.tmp', '.deps2', '__pycache__', '.pytest_cache', 'continuity-st-review.zip')
Compress-Archive -Path src, extensions, tests, preview, tools, samples, AGENTS.md, CHANGELOG.md, README.md, docs, pyproject.toml, .gitignore `
  -DestinationPath continuity-st-review.zip
# 若需附企划书原文：先复制 business-plan-text.txt 到一个临时目录再与上述内容合并打包
```

> 上传后请将 zip 发送给 ChatGPT（支持附件版本）并附第一节提示词中【审查标尺】起的内容
> （把「读 GitHub 仓库」改为「读压缩包内文件」）。

---

## 三、隐私与安全说明（规则 2 红线）

1. 审查包**零真实用户数据**：全部样本为合成（samples/synthetic/make_samples.py 生成），
   测试 fixture 为程序化假 context——上传不违反 AGENTS.md 规则 2。
2. 企划书原文（business-plan-text.txt）是创始人的内部商业文档：**是否分享给外部 AI 由创始人决定**，
   不分享时从包中删除（review-guide 隐私节已注明）。
3. 建议先在浏览器/仓库设置确认仓库可见性（public/private）；private 仓库请改用方案 B。
4. 审查不涉及运行任何不可信代码；外部 AI 返回的「修改建议」**绝不直接执行**，
   一律经 qa-reviewer 三态复核（真问题/证据不足/误报）后按 AGENTS.md 流程处理。

---

## 四、审查结果回流的处理流程（沿用 0.1.1–0.1.3 三轮先例）

1. ChatGPT 输出分级发现清单 → 存档（建议存入 docs/ 或 .tmp/ 由创始人指定）；
2. qa-reviewer 以审判官模式逐条三态复核：**真问题（有证据）→ 退回对应开发者修复**；
   **证据不足 → 要求外部补充或我方验证**；**误报 → 记录驳回理由**；
3. 修复后由 qa-reviewer 执行严格三轮审核（含真实运行全套 pytest 回归），通过后交创始人验收；
4. 创始人验收通过 → commit → 按投放规则处理（当前市场验证未通过，投放保持冻结）。
