"""Continuity Studio 本地 Web UI（提示词 8 / 开发计划阶段 W1 骨架）。

技术栈：纯标准库 ThreadingHTTPServer + 无构建原生 JS 单页应用（零新增运行时依赖）。
安全设计（详见 docs/webui-plan.md 第 5 节）：仅绑定 127.0.0.1；启动随机访问令牌；
Host 头白名单；CSP；前端渲染一律 textContent 转义（不执行导入内容，AGENTS.md 规则 3）。
"""
