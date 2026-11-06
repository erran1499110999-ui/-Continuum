/* Continuity Studio 本地工作台前端逻辑（前端改版，2026-11-07）。
 * 安全约定（AGENTS.md 规则 3）：所有动态内容一律用 textContent 写入，
 * 禁止 innerHTML / eval / 内联事件，绝不把导入数据按 HTML 解析。
 * 改版说明（docs/frontend-redesign-brief.md）：
 * - 保留全部原有业务逻辑（token、API 调用、扫描轮询、导航切换），只调整文案与新增接线；
 * - 新增：主题切换（浅色暖阳奶油 / 深色森林夜语，语义令牌见 style.css）；
 *         Hero 按钮接线（主 CTA 聚焦输入或直接提交、次 CTA 滚动到修复等级区）。
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
      }
    });
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
    var run = document.getElementById("scan-run");
    run.disabled = running;
    var state = document.getElementById("scan-state");
    /* .loading 类由 CSS 渲染转圈动画（唯一状态反馈动效，尊重 reduced-motion） */
    state.classList.toggle("loading", running);
    state.textContent = running ? "正在检查…（请稍候，检查为串行任务）" : "";
  }

  function pollJob(jobId, onDone) {
    var finished = false;
    var timer = window.setInterval(function () {
      if (finished) { return; }
      api("/api/jobs/" + jobId).then(function (snap) {
        if (finished || !snap) { return; }
        if (snap.error) {
          finished = true;
          window.clearInterval(timer);
          setScanError(snap.error);
          setScanRunning(false);
          if (onDone) { onDone(); }
          return;
        }
        if (snap.state === "succeeded") {
          finished = true;
          window.clearInterval(timer);
          renderScan(snap.result || {});
          setScanRunning(false);
          if (onDone) { onDone(); }
        } else if (snap.state === "failed") {
          finished = true;
          window.clearInterval(timer);
          setScanError(snap.error || snap.error_kind || "检查失败");
          setScanRunning(false);
          if (onDone) { onDone(); }
        }
      });
    }, 300);
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
          pollJob(data.job_id);
        } else {
          setScanError((data && data.error) || "启动检查任务失败");
          setScanRunning(false);
        }
      });
    });
  }

  loadOverview();
  showPage("overview");
})();
