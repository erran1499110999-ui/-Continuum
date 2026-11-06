/**
 * Continuity 体检（Continuity Studio 官方 ST 插件）— P2：内存态体检
 *
 * 定位：本地 Web UI 的获客敲门砖（薄壳）。P1 提供骨架（APP_READY、徽标、面板）；
 * P2 接入 checks.js 的内存态体检（H1–H5，只读纯函数）并全 textContent 渲染结果；
 * P3 将加入一键唤起本地 Web UI 与 /continuity slash command。
 *
 * 约束（AGENTS.md 规则，静态契约由 tests/test_st_plugin_static.py 锁定）：
 * - 只读内存，绝不写文件、绝不写设置（本阶段零写路径）；
 * - 只使用 SillyTavern.getContext() 与浏览器原生 API，不 import ST 内部模块；
 * - 不执行导入内容（无 eval/innerHTML，渲染全走 textContent/节点 API），
 *   不上传任何数据（零外部网络请求）；
 * - 不接触任何密钥；不使用 localStorage（持久化一律走 extensionSettings，P3 起）。
 */
import { runChecks } from "./checks.js";

"use strict";

(function () {
  const NAME = "Continuity 体检";
  const VERSION = "0.1.0";

  /** 能力检测：getContext 必须可用，否则在控制台与徽标中给出降级提示。 */
  function getContextSafe() {
    if (
      typeof SillyTavern === "undefined" ||
      typeof SillyTavern.getContext !== "function"
    ) {
      return null;
    }
    return SillyTavern.getContext();
  }

  /** 从 ST context 提取纯数据（字段名与 checks.js buildSnapshot 约定一致）。 */
  function collectContext(ctx) {
    return {
      chat: ctx.chat,
      characters: ctx.characters,
      characterId: ctx.characterId,
      chatMetadata: ctx.chatMetadata,
      chat_metadata: ctx.chat_metadata,
    };
  }

  /** 渲染体检结果：全部 textContent/节点 API，绝不把数据当 HTML 解析（规则 3）。 */
  function renderFindings(container, result) {
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    const count = result.findings.length;

    const summary = document.createElement("div");
    summary.className = "continuity-check-summary";
    summary.textContent =
      count === 0
        ? "内存态检查未发现上述异常提示（不代表全量健康）。"
        : "发现 " + count + " 项内存态提示：";
    container.appendChild(summary);

    for (const finding of result.findings) {
      const item = document.createElement("div");
      item.className = "continuity-check-item";
      const title = document.createElement("div");
      title.className = "continuity-check-item-title";
      title.textContent = finding.title;
      const detail = document.createElement("div");
      detail.className = "continuity-check-item-detail";
      detail.textContent = finding.detail;
      item.appendChild(title);
      item.appendChild(detail);
      container.appendChild(item);
    }

    // 薄壳原则：插件只提示与引导，深度结论在本地 Web UI（Python 引擎）
    const note = document.createElement("div");
    note.className = "continuity-check-note";
    note.textContent =
      "以上均为内存态初步提示；深度体检/备份/恢复/迁移请打开本地 Web UI（127.0.0.1:8777，P3 提供一键唤起）。";
    container.appendChild(note);
  }

  /** 一键体检：读取 ST 内存 → 纯函数检查 → 渲染结果。全程只读。 */
  function runHealthCheck() {
    const results = document.getElementById("continuity-check-results");
    const ctx = getContextSafe();
    if (!ctx) {
      if (results) {
        results.textContent = "无法读取 SillyTavern 上下文（请升级 SillyTavern 至 1.12.0+）。";
      }
      return;
    }
    if (results) {
      renderFindings(results, runChecks(collectContext(ctx)));
    }
  }

  /** 创建面板容器与版本徽标（纯 DOM + textContent，样式见 style.css）。 */
  function buildShell() {
    const badge = document.createElement("div");
    badge.id = "continuity-check-badge";
    badge.className = "continuity-check-badge";
    badge.textContent = NAME + " v" + VERSION;

    const panel = document.createElement("div");
    panel.id = "continuity-check-panel";
    panel.className = "continuity-check-panel hidden";
    const title = document.createElement("div");
    title.className = "continuity-check-title";
    title.textContent = NAME + " v" + VERSION;
    panel.appendChild(title);

    const body = document.createElement("div");
    body.className = "continuity-check-body";
    body.id = "continuity-check-body";

    const intro = document.createElement("div");
    intro.className = "continuity-check-intro";
    intro.textContent = "内存态轻量体检（只读，不写任何数据）。";
    body.appendChild(intro);

    const runButton = document.createElement("button");
    runButton.type = "button";
    runButton.id = "continuity-check-run";
    runButton.className = "continuity-check-run";
    runButton.textContent = "开始体检（内存态）";
    runButton.addEventListener("click", runHealthCheck);
    body.appendChild(runButton);

    const results = document.createElement("div");
    results.id = "continuity-check-results";
    results.className = "continuity-check-results";
    body.appendChild(results);

    panel.appendChild(body);

    badge.addEventListener("click", function () {
      panel.classList.toggle("hidden");
    });

    document.body.appendChild(badge);
    document.body.appendChild(panel);
  }

  /** APP_READY 初始化（能力检测 + 降级提示）。 */
  function onAppReady() {
    const context = getContextSafe();
    if (!context) {
      console.warn(
        "Continuity 体检: 当前环境不支持 SillyTavern.getContext()，插件未启用（请升级 SillyTavern）。"
      );
      return;
    }
    console.debug("Continuity 体检: P2 内存态体检已加载（" + NAME + " v" + VERSION + "）。");
    buildShell();
  }

  const context = getContextSafe();
  if (!context) {
    console.warn(
      "Continuity 体检: 当前环境不支持 SillyTavern.getContext()，插件未启用（请升级 SillyTavern）。"
    );
    return;
  }
  if (context.eventSource && context.event_types && typeof context.eventSource.on === "function") {
    context.eventSource.on(context.event_types.APP_READY, onAppReady);
  } else {
    onAppReady();
  }
})();
