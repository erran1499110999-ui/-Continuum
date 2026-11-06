/**
 * Continuity 体检（Continuity Studio 官方 ST 插件）— P1 骨架
 *
 * 定位：本地 Web UI 的获客敲门砖（薄壳）。P1 只做骨架：APP_READY 注册、
 * 空面板容器与版本徽标；内存态体检逻辑在 P2（checks.js），slash command 与
 * 唤起按钮在 P3。
 *
 * 约束（AGENTS.md 规则，静态契约由 tests/test_st_plugin_static.py 锁定）：
 * - 只读内存，绝不写文件、绝不写设置（本阶段零写路径）；
 * - 只使用 SillyTavern.getContext() 与浏览器原生 API，不 import ST 内部模块；
 * - 不执行导入内容（无 eval/innerHTML），不上传任何数据（零外部网络请求）；
 * - 不接触任何密钥；不使用 localStorage（持久化一律走 extensionSettings，P3 起）。
 */
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

  /** 创建空面板容器与版本徽标（纯 DOM + textContent，样式见 style.css）。 */
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
    body.textContent = "P1 骨架：体检功能将在后续版本开放（P2）。";
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
    console.debug("Continuity 体检: P1 骨架已加载（" + NAME + " v" + VERSION + "）。");
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
