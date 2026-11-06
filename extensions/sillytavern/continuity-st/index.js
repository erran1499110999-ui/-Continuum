/**
 * Continuity 体检（Continuity Studio 官方 ST 插件）— P3：唤起与入口
 *
 * 定位：本地 Web UI 的获客敲门砖（薄壳）。P1 提供骨架（APP_READY、徽标、面板）；
 * P2 接入 checks.js 的内存态体检（H1–H5，只读纯函数）；P3 新增：
 * - 「打开本地 Web UI」按钮（端口读 extensionSettings，默认 8777；仅 window.open，
 *   不做跨域 API 探测——服务是否在运行由用户看到的新标签页判断）；
 * - `/continuity` slash command（新式 SlashCommandParser.addCommandObject +
 *   旧式 registerSlashCommand 能力检测回退）；
 * - 设置页 settings.html（Web UI 端口 + 提示开关，经 ST 扩展设置框架持久化）。
 *
 * 约束（AGENTS.md 规则，静态契约由 tests/test_st_plugin_static.py 锁定）：
 * - 只读内存，绝不写文件（设置持久化由 ST 的 settings.html 表单框架完成）；
 * - 只使用 SillyTavern.getContext() 与浏览器原生 API，不 import ST 内部模块；
 * - 不执行导入内容（无 eval/innerHTML，渲染全走 textContent/节点 API），
 *   不上传任何数据（除 127.0.0.1 外零外部网络请求，且本轮连跨域调用都不做）；
 * - 不接触任何密钥；不使用 localStorage（持久化一律走 extensionSettings）。
 */
import { runChecks } from "./checks.js";

"use strict";

(function () {
  const NAME = "Continuity 体检";
  const VERSION = "0.1.0";
  const DEFAULT_WEBUI_PORT = 8777; // 与本地 Web UI 默认端口一致（创始人裁决）
  // ST 以扩展文件夹名为键保存设置：settings.html 的表单字段自动绑定到该命名空间
  const SETTINGS_KEY = "continuity-st";

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

  /**
   * 读取插件设置（只读，写入由 ST 设置表单框架完成）。
   * 端口越界/缺失时回退默认 8777；提示开关默认开启。
   */
  function getSettings(ctx) {
    const store =
      ctx && ctx.extensionSettings && typeof ctx.extensionSettings === "object"
        ? ctx.extensionSettings
        : {};
    const raw =
      store[SETTINGS_KEY] && typeof store[SETTINGS_KEY] === "object"
        ? store[SETTINGS_KEY]
        : {};
    const port =
      typeof raw.webuiPort === "number" &&
      Number.isInteger(raw.webuiPort) &&
      raw.webuiPort > 0 &&
      raw.webuiPort < 65536
        ? raw.webuiPort
        : DEFAULT_WEBUI_PORT;
    const showHints = raw.showHints !== false; // 未设置/其它值均视为开启
    return { port, showHints };
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

  /**
   * 版本门槛提示（只用能力检测，绝不做版本号字符串比较——版本格式会变，比较易误判）：
   * 依据 1.12+ 扩展体系的关键能力是否存在，给出「建议升级」级别的提示而非阻断。
   */
  function detectVersionHints(ctx) {
    const hints = [];
    // 设置持久化能力：1.12+ 扩展体系的基础；缺失时端口/提示开关只能走默认值
    if (
      !ctx ||
      typeof ctx !== "object" ||
      !ctx.extensionSettings ||
      typeof ctx.extensionSettings !== "object"
    ) {
      hints.push(
        "当前 SillyTavern 版本可能过低（建议 ≥ 1.12.0）：扩展设置不可用，将使用默认配置。"
      );
    }
    const parser =
      (ctx.SlashCommandParser) ||
      (typeof SillyTavern !== "undefined" ? SillyTavern.SlashCommandParser : null) ||
      (typeof window !== "undefined" ? window.SlashCommandParser : null) ||
      null;
    const hasSlash =
      (parser && typeof parser.addCommandObject === "function") ||
      (ctx.registerSlashCommand && typeof ctx.registerSlashCommand === "function");
    if (!hasSlash) {
      hints.push("当前版本不支持 slash command 注册，请使用面板按钮。");
    }
    return hints;
  }

  /** 渲染体检结果：全部 textContent/节点 API，绝不把数据当 HTML 解析（规则 3）。 */
  function renderFindings(container, result, showHints) {
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

    if (showHints) {
      // 薄壳原则：插件只提示与引导，深度结论在本地 Web UI（Python 引擎）
      const note = document.createElement("div");
      note.className = "continuity-check-note";
      note.textContent =
        "以上均为内存态初步提示；深度体检/备份/恢复/迁移请使用下方「打开本地 Web UI」。";
      container.appendChild(note);
    }
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
      renderFindings(results, runChecks(collectContext(ctx)), getSettings(ctx).showHints);
    }
  }

  /**
   * 服务存活探测：用 Image() 加载 http://127.0.0.1:<port>/api/ping。
   * 选择 Image() 而非 fetch：跨域探测不需要读响应体、不需要 CORS 头，
   * 成功（onload）即「服务在运行」；失败（onerror）即「未运行」。
   * 探测对象是免 token 的 ping 端点，其响应只含 {"status":"ok"}（无版本指纹）。
   */
  function probeWebUIStatus() {
    const statusEl = document.getElementById("continuity-check-status");
    const ctx = getContextSafe();
    const settings = getSettings(ctx);
    const url = "http://127.0.0.1:" + settings.port + "/api/ping";
    if (statusEl) {
      statusEl.textContent = "服务状态：检测中…";
    }
    const img = new Image();
    let done = false;
    const finish = function (ok) {
      if (done || !statusEl) {
        return;
      }
      done = true;
      statusEl.textContent = ok
        ? "服务状态：运行中（127.0.0.1:" + settings.port + "）"
        : "服务状态：未运行——请先运行 python -m continuity.webui（端口 " + settings.port + "）。";
    };
    img.onload = function () {
      finish(true);
    };
    img.onerror = function () {
      finish(false);
    };
    img.src = url;
  }

  /**
   * 深链跳转：把用户带到本地 Web UI 的对应页面。
   * auto=1 语义（Q13）：仅允许「急救备份/升级前备份」自动开始（页面自动发起任务）；
   * 「恢复」绝不带 auto=1——恢复目标目录必须由用户人工确认后再点开始。
   */
  function openDeepLink(kind) {
    const ctx = getContextSafe();
    const settings = getSettings(ctx);
    let hash = "";
    if (kind === "emergency") {
      hash = "#emergency?auto=1";
    } else if (kind === "backup") {
      hash = "#backup?auto=1";
    } else if (kind === "restore") {
      hash = "#restore"; // 无 auto=1：人工确认目标目录后才允许执行
    } else {
      hash = "";
    }
    window.open(
      "http://127.0.0.1:" + settings.port + "/" + hash,
      "_blank",
      "noopener"
    );
    if (settings.showHints) {
      const note = document.getElementById("continuity-check-note");
      if (note) {
        note.classList.remove("hidden");
        note.textContent =
          "若新标签页未打开，请先运行 python -m continuity.webui（端口 " +
          settings.port +
          "）。";
      }
    }
    probeWebUIStatus(); // 跳转后刷新状态显示
  }

  /**
   * 一键唤起本地 Web UI：新标签页打开首页，token 由服务器注入的页面自取自用，
   * 插件零接触、零存储（见 docs/st-plugin-plan.md 6.3）。
   * 本轮仅 window.open：无法探测服务是否在运行，故始终附一句友好提示。
   */
  function openWebUI() {
    const ctx = getContextSafe();
    const settings = getSettings(ctx);
    window.open(
      "http://127.0.0.1:" + settings.port + "/",
      "_blank",
      "noopener"
    );
    if (settings.showHints) {
      const note = document.getElementById("continuity-check-note");
      if (note) {
        note.classList.remove("hidden");
        note.textContent =
          "若新标签页未打开，请先运行 python -m continuity.webui（端口 " +
          settings.port +
          "）。";
      }
    }
    probeWebUIStatus();
  }

  /** 展开面板并执行一次体检（slash command 触发路径）。 */
  function openPanelAndRun() {
    const panel = document.getElementById("continuity-check-panel");
    if (panel) {
      panel.classList.remove("hidden");
    }
    runHealthCheck();
  }

  /**
   * 注册 /continuity slash command。
   * 新式优先（SlashCommandParser.addCommandObject，官方推荐），
   * 旧式 registerSlashCommand 能力检测回退；两者都不可用则降级提示。
   */
  function registerSlashCommand() {
    const ctx = getContextSafe();
    if (!ctx) {
      return;
    }
    // 回调返回空字符串：slash 命令在 STscript 管道中不产出文本，只触发面板
    const callback = function () {
      openPanelAndRun();
      return "";
    };
    const parser =
      (ctx.SlashCommandParser) ||
      (typeof SillyTavern !== "undefined" ? SillyTavern.SlashCommandParser : null) ||
      (typeof window !== "undefined" ? window.SlashCommandParser : null) ||
      null;
    if (parser && typeof parser.addCommandObject === "function") {
      parser.addCommandObject({
        name: "continuity",
        callback: callback,
        helpString: "打开 Continuity 体检面板并执行内存态体检（只读）",
        returns: "",
        namedArgumentList: [],
      });
      return;
    }
    if (ctx.registerSlashCommand && typeof ctx.registerSlashCommand === "function") {
      // 旧式签名（不同 ST 版本参数有差异）：能力检测内使用最通用形态
      ctx.registerSlashCommand(
        "continuity",
        callback,
        [],
        "打开 Continuity 体检面板并执行内存态体检（只读）",
        true,
        true
      );
      return;
    }
    console.warn(
      "Continuity 体检: 当前版本不支持 slash command 注册，请使用面板按钮。"
    );
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
    intro.id = "continuity-check-intro";
    intro.textContent = "内存态轻量体检（只读，不写任何数据）。";
    body.appendChild(intro);

    const runButton = document.createElement("button");
    runButton.type = "button";
    runButton.id = "continuity-check-run";
    runButton.className = "continuity-check-run";
    runButton.textContent = "开始体检（内存态）";
    runButton.addEventListener("click", runHealthCheck);
    body.appendChild(runButton);

    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.id = "continuity-check-open";
    openButton.className = "continuity-check-open";
    openButton.textContent = "打开本地 Web UI";
    openButton.addEventListener("click", openWebUI);
    body.appendChild(openButton);

    // P5 深链入口：急救备份/升级前备份（可自动开始）与恢复（必须人工确认目标）
    const deepLinks = [
      { id: "continuity-check-emergency", label: "急救备份（一键）", kind: "emergency" },
      { id: "continuity-check-backup", label: "升级前备份", kind: "backup" },
      { id: "continuity-check-restore", label: "恢复（需人工确认）", kind: "restore" },
    ];
    for (const entry of deepLinks) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.id = entry.id;
      btn.className = "continuity-check-open";
      btn.textContent = entry.label;
      btn.addEventListener(
        "click",
        (function (kind) {
          return function () {
            openDeepLink(kind);
          };
        })(entry.kind)
      );
      body.appendChild(btn);
    }

    const statusLine = document.createElement("div");
    statusLine.id = "continuity-check-status";
    statusLine.className = "continuity-check-status";
    statusLine.textContent = "服务状态：尚未检测";
    body.appendChild(statusLine);

    const results = document.createElement("div");
    results.id = "continuity-check-results";
    results.className = "continuity-check-results";
    body.appendChild(results);

    const note = document.createElement("div");
    note.id = "continuity-check-note";
    note.className = "continuity-check-note hidden";
    body.appendChild(note);

    panel.appendChild(body);

    badge.addEventListener("click", function () {
      panel.classList.toggle("hidden");
      // 每次展开面板时刷新服务状态（Image 探测，零开销）
      if (!panel.classList.contains("hidden")) {
        probeWebUIStatus();
      }
    });

    document.body.appendChild(badge);
    document.body.appendChild(panel);
  }

  /** APP_READY 初始化（能力检测 + 降级提示 + 按设置收起提示文案）。 */
  function onAppReady() {
    const context = getContextSafe();
    if (!context) {
      console.warn(
        "Continuity 体检: 当前环境不支持 SillyTavern.getContext()，插件未启用（请升级 SillyTavern）。"
      );
      return;
    }
    console.debug("Continuity 体检: P4 上市就绪（" + NAME + " v" + VERSION + "）。");
    buildShell();
    const settings = getSettings(context);
    // 版本门槛提示：只用能力检测（detectVersionHints），绝不做版本号字符串比较
    const hints = detectVersionHints(context);
    for (const hint of hints) {
      console.warn("Continuity 体检: " + hint);
    }
    const intro = document.getElementById("continuity-check-intro");
    if (intro) {
      if (!settings.showHints) {
        // 提示开关关闭时收起说明文案（设置页可改，下次启动生效）
        intro.classList.add("hidden");
      } else if (hints.length > 0) {
        intro.textContent = hints.join("；") + "。" + intro.textContent;
      }
    }
    registerSlashCommand();
    probeWebUIStatus(); // 启动即探测一次，面板状态行有据可依
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
