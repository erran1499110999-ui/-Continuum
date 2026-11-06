/* Continuity Studio 本地工作台前端逻辑（前端改版 + 深链引导流程，2026-11-07）。
 * 安全约定（AGENTS.md 规则 3）：所有动态内容一律用 textContent 写入，
 * 禁止 innerHTML / eval / 内联事件，绝不把导入数据按 HTML 解析。
 * 改版说明（docs/frontend-redesign-brief.md）：
 * - 保留全部原有业务逻辑（token、API 调用、扫描轮询、导航切换），只调整文案与新增接线；
 * - 新增：主题切换（浅色暖阳奶油 / 深色森林夜语，语义令牌见 style.css）；
 *         Hero 按钮接线（主 CTA 聚焦输入或直接提交、次 CTA 滚动到修复等级区）。
 * 深链引导流程（创始人路径 A，最高优先级）：
 * - ST 插件深链 #emergency / #backup / #restore 切入对应引导页；
 * - 对应 API（以 src/continuity/webui/server.py 实际契约为准，勿改后端）：
 *   POST /api/jobs/emergency-backup（{source, output}）
 *   POST /api/jobs/backup            （{source, bundle}）
 *   POST /api/jobs/restore           （{bundle, dest}）
 *   进度轮询 GET /api/jobs/{id}；X-Continuity-Token 由 meta 自动携带。
 * - 自动开始白名单（Q12 安全细化）：auto=1 仅对 #emergency / #backup 生效；
 *   #restore 永不自动开始——必须由用户人工确认目标目录并手动点击开始。
 */
"use strict";

(function () {
  var root = document.documentElement;
  var tokenMeta = document.querySelector('meta[name="continuity-token"]');
  var TOKEN = tokenMeta ? tokenMeta.content : "";

  /* ---------- API 封装：所有请求带 X-Continuity-Token（服务器随机令牌） ---------- */
  function api(path) {
    return fetch(path, { headers: { "X-Continuity-Token": TOKEN } }).then(function (res) {
      return res.json().catch(function () {
        return { error: "服务器响应异常（HTTP " + res.status + "）" };
      });
    });
  }

  function setText(id, text) {
    var el = document.getElementById(id);
    if (el) {
      el.textContent = text;
    }
  }

  function val(id) {
    var el = document.getElementById(id);
    return el ? el.value : "";
  }

  /* ---------- 主题切换（与预览页同源机制：data-theme 属性 + localStorage 记忆） ---------- */
  var THEME_KEY = "cs-ui-theme";

  function applyTheme(name) {
    root.setAttribute("data-theme", name);
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      /* 按钮文案显示「切到对方」的操作：当前浅色 → 显示"深色主题" */
      btn.textContent = name === "dark" ? "浅色主题" : "深色主题";
      btn.setAttribute("aria-pressed", String(name === "dark"));
    }
    try { localStorage.setItem(THEME_KEY, name); } catch (e) { /* 忽略存储不可用 */ }
  }

  var savedTheme = null;
  try { savedTheme = localStorage.getItem(THEME_KEY); } catch (e) { /* 忽略 */ }
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  /* 初始主题：本地记忆 > 系统深色偏好 > 默认浅色 */
  applyTheme(savedTheme === "dark" || savedTheme === "light" ? savedTheme : (prefersDark ? "dark" : "light"));

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }

  /* ---------- Hero 按钮接线：真实动作，不造演示 ---------- */
  var heroStart = document.getElementById("hero-start");
  var scanForm = document.getElementById("scan-form");
  if (heroStart && scanForm) {
    heroStart.addEventListener("click", function () {
      var input = document.getElementById("scan-source");
      /* 已填路径 → 直接提交检查；未填 → 聚焦输入框引导填写 */
      if (input && input.value.trim() === "") {
        input.focus();
      } else if (typeof scanForm.requestSubmit === "function") {
        scanForm.requestSubmit();
      }
    });
  }
  var heroLevels = document.getElementById("hero-levels");
  var levelsBox = document.getElementById("levels");
  if (heroLevels && levelsBox) {
    heroLevels.addEventListener("click", function () {
      levelsBox.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  /* ---------- 概览信息：工具名 / 版本 / 服务状态 / 端口 ---------- */
  function loadOverview() {
    if (window.location && window.location.port) {
      setText("info-port", window.location.port);
    }
    api("/api/version").then(function (v) {
      if (v && v.error) {
        setText("info-version", v.error);
        return;
      }
      setText("info-tool", v.tool || "");
      setText("info-version", v.version || "");
    });
    api("/api/health").then(function (h) {
      if (h && h.error) {
        setText("info-health", h.error);
        return;
      }
      setText("info-health", h.status === "ok" ? "运行中" : "异常");
    });
  }

  /* ---------- 导航：单页切换（隐藏/显示 .page 区块） ---------- */
  function showPage(name) {
    var pages = document.querySelectorAll(".page");
    for (var i = 0; i < pages.length; i++) {
      pages[i].classList.toggle("hidden", pages[i].id !== "page-" + name);
    }
    var buttons = document.querySelectorAll(".nav-btn");
    for (var j = 0; j < buttons.length; j++) {
      buttons[j].classList.toggle("is-active", buttons[j].dataset.page === name);
    }
  }

  var nav = document.getElementById("nav");
  if (nav) {
    nav.addEventListener("click", function (ev) {
      var btn = ev.target && ev.target.closest ? ev.target.closest("button") : null;
      if (btn && btn.dataset.page) {
        showPage(btn.dataset.page);
        /* 用户手动导航后清除深链 hash，避免刷新又跳回引导页 */
        if (window.location.hash && window.history && typeof window.history.replaceState === "function") {
          window.history.replaceState(null, "", window.location.pathname + window.location.search);
        }
      }
    });
  }

  /* ---------- 通用任务状态机：POST 启动 → 轮询 GET /api/jobs/{id} → 结果/错误 ---------- */

  function setBusy(runBtn, stateBox, running, text) {
    /* 加载态：按钮禁用 + .loading 类渲染转圈（唯一状态反馈动效，尊重 reduced-motion） */
    runBtn.disabled = running;
    stateBox.classList.toggle("loading", running);
    stateBox.textContent = running ? text : "";
  }

  /* 轮询任务状态；opts = {runBtn, stateBox, onError, onResult}。
     成功/失败统一收尾（清转圈、恢复按钮、透传后端错误文案）。 */
  function pollJob(jobId, opts) {
    var finished = false;
    var timer = window.setInterval(function () {
      if (finished) { return; }
      api("/api/jobs/" + jobId).then(function (snap) {
        if (finished || !snap) { return; }
        if (snap.error) {
          finished = true;
          window.clearInterval(timer);
          opts.onError(snap.error);
          setBusy(opts.runBtn, opts.stateBox, false, "");
        } else if (snap.state === "succeeded") {
          finished = true;
          window.clearInterval(timer);
          opts.onResult(snap.result || {});
          setBusy(opts.runBtn, opts.stateBox, false, "");
        } else if (snap.state === "failed") {
          finished = true;
          window.clearInterval(timer);
          opts.onError(snap.error || snap.error_kind || "任务失败");
          setBusy(opts.runBtn, opts.stateBox, false, "");
        }
      });
    }, 300);
  }

  /* ---------- 目录检查（原扫描流程，业务逻辑未改） ---------- */

  function clearChildren(el) {
    while (el.firstChild) {
      el.removeChild(el.firstChild);
    }
  }

  function makeLi(text) {
    var li = document.createElement("li");
    li.textContent = text;
    return li;
  }

  function makeLiTagged(tag, text) {
    var li = document.createElement("li");
    var span = document.createElement("span");
    span.textContent = tag;
    span.className = "tag";
    li.appendChild(span);
    li.appendChild(document.createTextNode(" " + text));
    return li;
  }

  function setScanError(text) {
    var box = document.getElementById("scan-error");
    box.textContent = text || "";
    box.classList.toggle("hidden", !text);
  }

  function setScanRunning(running) {
    setBusy(
      document.getElementById("scan-run"),
      document.getElementById("scan-state"),
      running,
      "正在检查…（请稍候，检查为串行任务）"
    );
  }

  function renderScan(data) {
    var files = Array.isArray(data.files) ? data.files : [];
    var findings = Array.isArray(data.findings) ? data.findings : [];
    var duplicates = Array.isArray(data.duplicates) ? data.duplicates : [];
    var symlinks = Array.isArray(data.skipped_symlinks) ? data.skipped_symlinks : [];

    document.getElementById("scan-summary").textContent =
      "检查完成：" + files.length + " 个文件（目录：" + (data.root || "") + "）";

    var kinds = {};
    for (var i = 0; i < files.length; i++) {
      var k = files[i].kind || "unknown";
      kinds[k] = (kinds[k] || 0) + 1;
    }
    var kindsBox = document.getElementById("scan-kinds");
    clearChildren(kindsBox);
    var kindNames = Object.keys(kinds).sort();
    for (var j = 0; j < kindNames.length; j++) {
      kindsBox.appendChild(makeLi(kindNames[j] + ": " + kinds[kindNames[j]]));
    }

    var findingsBox = document.getElementById("scan-findings");
    clearChildren(findingsBox);
    document.getElementById("scan-findings-count").textContent = String(findings.length);
    for (var m = 0; m < findings.length; m++) {
      var f = findings[m];
      var level = f.repair_level ? "，修复等级 " + f.repair_level : "";
      var text = f.file + ": " + f.problem + "（证据：" + f.evidence + "；建议：" +
        f.suggestion + level + "）";
      findingsBox.appendChild(makeLiTagged(f.severity, text));
    }

    var dupsBox = document.getElementById("scan-duplicates");
    clearChildren(dupsBox);
    document.getElementById("scan-duplicates-count").textContent = String(duplicates.length);
    for (var d = 0; d < duplicates.length; d++) {
      dupsBox.appendChild(makeLi(duplicates[d].join("、")));
    }

    var linksBox = document.getElementById("scan-symlinks");
    clearChildren(linksBox);
    document.getElementById("scan-symlinks-count").textContent = String(symlinks.length);
    for (var s = 0; s < symlinks.length; s++) {
      linksBox.appendChild(makeLi(symlinks[s]));
    }

    document.getElementById("scan-result").classList.remove("hidden");
  }

  if (scanForm) {
    scanForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setScanError("");
      document.getElementById("scan-result").classList.add("hidden");
      var source = document.getElementById("scan-source").value;
      setScanRunning(true);
      fetch("/api/jobs/scan", {
        method: "POST",
        headers: { "X-Continuity-Token": TOKEN, "Content-Type": "application/json" },
        body: JSON.stringify({ source: source }),
      }).then(function (res) {
        return res.json().catch(function () {
          return { error: "服务器响应异常（HTTP " + res.status + "）" };
        });
      }).then(function (data) {
        if (data && data.job_id) {
          pollJob(data.job_id, {
            runBtn: document.getElementById("scan-run"),
            stateBox: document.getElementById("scan-state"),
            onError: setScanError,
            onResult: renderScan,
          });
        } else {
          setScanError((data && data.error) || "启动检查任务失败");
          setScanRunning(false);
        }
      });
    });
  }

  /* ---------- 深链引导流程（#emergency / #backup / #restore，ST 插件入口） ---------- */

  /* 每个流程的配置：API 端点 + 载荷构造 + 进行中文案 + 完成文案。
     载荷契约以 src/continuity/webui/server.py 实际实现为准（勿改后端）。 */
  var GUIDE_FLOWS = {
    emergency: {
      endpoint: "/api/jobs/emergency-backup",
      buildPayload: function () {
        return { source: val("emergency-source"), output: val("emergency-output") };
      },
      busyText: "正在打包…（请稍候，打包为串行任务）",
      doneText: "急救备份完成"
    },
    backup: {
      endpoint: "/api/jobs/backup",
      buildPayload: function () {
        return { source: val("backup-source"), bundle: val("backup-bundle") };
      },
      busyText: "正在备份…（请稍候）",
      doneText: "备份完成"
    },
    restore: {
      endpoint: "/api/jobs/restore",
      buildPayload: function () {
        return { bundle: val("restore-bundle"), dest: val("restore-dest") };
      },
      busyText: "正在恢复…（请稍候）",
      doneText: "恢复完成"
    }
  };

  /* 结果字段的中文标签（未收录的字段回退显示原字段名） */
  var KEY_LABELS = {
    "bundle": "备份包位置",
    "dest": "目标目录",
    "source": "源目录",
    "restored": "已恢复文件数",
    "ok": "校验通过",
    "checked": "已校验文件数",
    "mismatches": "不一致文件数",
    "missing": "缺失文件数",
    "extra_files": "多余文件数",
    "warnings": "提醒",
    "errors": "问题",
    "created_at": "创建时间"
  };

  /* 结果通用渲染（textContent 安全）：输出路径优先入摘要；
     标量字段（含布尔，显示 是/否）→ 键值行；急救备份的 verify 自检对象扁平一层；
     字符串数组（errors/warnings 等）→ 标题 + 列表。 */
  function renderGuideResult(flowName, resultBox, doneText, result) {
    var summary = document.getElementById(flowName + "-summary");
    var kvBox = document.getElementById(flowName + "-kv");
    var outputField = { emergency: "emergency-output", backup: "backup-bundle", restore: "restore-dest" };
    var outputKey = ["output_path", "output", "bundle", "dest", "path"]
      .filter(function (k) { return typeof result[k] === "string" && result[k]; })[0];
    /* 后端结果未带路径时（如 restore 只返回报告），回退展示用户填写的目标目录 */
    var outputValue = outputKey ? result[outputKey] : (val(outputField[flowName]) || "");

    var scalarKeys = Object.keys(result).filter(function (k) {
      var v = result[k];
      return (typeof v === "string" || typeof v === "number" || typeof v === "boolean") && k !== outputKey;
    });
    var parts = [doneText];
    if (outputValue) {
      parts.push("输出位置：" + outputValue);
    } else if (scalarKeys.length === 0) {
      parts.push("任务已完成，暂无详细结果");
    }
    summary.textContent = parts.join(" · ");

    clearChildren(kvBox);
    var rows = [];
    for (var i = 0; i < scalarKeys.length; i++) {
      var k = scalarKeys[i];
      var v = result[k];
      rows.push([KEY_LABELS[k] || k, typeof v === "boolean" ? (v ? "是" : "否") : String(v)]);
    }
    /* 急救备份的 verify 自检结论（后端已知字段）扁平一层；manifest 等对象不展开 */
    if (result.verify && typeof result.verify === "object") {
      Object.keys(result.verify).forEach(function (k) {
        var v = result.verify[k];
        if (typeof v === "string" || typeof v === "number" || typeof v === "boolean") {
          rows.push(["自检·" + (KEY_LABELS[k] || k), typeof v === "boolean" ? (v ? "是" : "否") : String(v)]);
        }
      });
    }
    for (var r = 0; r < rows.length; r++) {
      var dt = document.createElement("dt");
      dt.textContent = rows[r][0];
      var dd = document.createElement("dd");
      dd.textContent = rows[r][1];
      kvBox.appendChild(dt);
      kvBox.appendChild(dd);
    }
    /* 字符串数组字段（校验报告条目等）渲染为标题 + 列表，追加在结果容器内 */
    var listKeys = Object.keys(result).filter(function (k) {
      return Array.isArray(result[k]) && result[k].every(function (x) { return typeof x === "string"; });
    });
    for (var j = 0; j < listKeys.length; j++) {
      var h4 = document.createElement("h4");
      h4.textContent = KEY_LABELS[listKeys[j]] || String(listKeys[j]);
      var ul = document.createElement("ul");
      ul.className = "list";
      result[listKeys[j]].forEach(function (x) { ul.appendChild(makeLi(x)); });
      resultBox.appendChild(h4);
      resultBox.appendChild(ul);
    }
  }

  /* 为一个引导流程接线：提交 → POST 启动 → 轮询 → 结果/错误展示 */
  function wireGuide(flowName) {
    var cfg = GUIDE_FLOWS[flowName];
    var form = document.getElementById(flowName + "-form");
    if (!form) { return; }
    var errBox = document.getElementById(flowName + "-error");
    var resultBox = document.getElementById(flowName + "-result");
    var runBtn = document.getElementById(flowName + "-run");
    var stateBox = document.getElementById(flowName + "-state");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      errBox.textContent = "";
      errBox.classList.add("hidden");
      resultBox.classList.add("hidden");
      setBusy(runBtn, stateBox, true, cfg.busyText);
      fetch(cfg.endpoint, {
        method: "POST",
        headers: { "X-Continuity-Token": TOKEN, "Content-Type": "application/json" },
        body: JSON.stringify(cfg.buildPayload()),
      }).then(function (res) {
        return res.json().catch(function () {
          return { error: "服务器响应异常（HTTP " + res.status + "）" };
        });
      }).then(function (data) {
        if (data && data.job_id) {
          pollJob(data.job_id, {
            runBtn: runBtn,
            stateBox: stateBox,
            onError: function (msg) {
              errBox.textContent = msg;
              errBox.classList.remove("hidden");
            },
            onResult: function (result) {
              renderGuideResult(flowName, resultBox, cfg.doneText, result);
              resultBox.classList.remove("hidden");
            },
          });
        } else {
          /* 错误透传：后端校验/忙碌/未实现等文案原样展示给用户 */
          errBox.textContent = (data && data.error) || "启动任务失败";
          errBox.classList.remove("hidden");
          setBusy(runBtn, stateBox, false, "");
        }
      });
    });
  }
  wireGuide("emergency");
  wireGuide("backup");
  wireGuide("restore");

  /* ---------- 深链路由：location.hash 为 #emergency / #backup / #restore 时切入对应页 ---------- */
  var HASH_PAGES = { emergency: true, backup: true, restore: true };

  /* 自动开始白名单（Q12 安全细化，调研者质疑）：
     - #restore 永不自动开始——恢复必须由用户人工确认目标目录并手动点击开始；
     - #emergency / #backup 仅在「所有必填目录都已填写」时才自动提交；
       否则只聚焦第一个空白字段引导用户填写（绝不带空值自动提交）。 */
  function tryAutoStart(name) {
    var formId = name === "emergency" ? "emergency-form" : "backup-form";
    var fieldIds = name === "emergency"
      ? ["emergency-source", "emergency-output"]
      : ["backup-source", "backup-bundle"];
    var empty = null;
    for (var i = 0; i < fieldIds.length; i++) {
      var el = document.getElementById(fieldIds[i]);
      if (el && !el.value.trim()) {
        empty = el;
        break;
      }
    }
    if (empty) {
      empty.focus();   /* 有空白字段：只聚焦引导，不自动提交 */
      return;
    }
    var form = document.getElementById(formId);
    if (form && typeof form.requestSubmit === "function") {
      form.requestSubmit();
    }
    /* restore 分支刻意不存在：任何情况下都不自动执行恢复 */
  }

  function routeFromHash() {
    var raw = window.location.hash || "";
    /* 兼容两种深链写法：#emergency 与 #w=emergency&auto=1（见 docs/plugin-viability-plan.md） */
    var m = /(?:^|[#?&])w=([A-Za-z0-9_-]+)/.exec(raw);
    var name = m ? m[1] : raw.replace(/^#/, "").split(/[?&]/)[0].trim();
    var auto = /(?:^|[#?&])auto=1(?:$|[&#])/.test(raw);
    if (!name) {
      showPage("overview");
      return;
    }
    if (HASH_PAGES[name]) {
      showPage(name);
      if (auto && name !== "restore") {  /* Q12：restore 明确排除在自动开始之外 */
        tryAutoStart(name);
      }
    }
  }
  window.addEventListener("hashchange", routeFromHash);

  loadOverview();
  showPage("overview");
  routeFromHash();   /* 初始化时按 hash 覆盖默认页（插件深链直达） */
})();
