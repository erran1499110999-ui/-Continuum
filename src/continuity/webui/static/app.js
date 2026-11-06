/* Continuity Studio 本地工作台（W1）：原生 JS，无构建、无依赖。
 * 安全约定（AGENTS.md 规则 3）：所有动态内容一律用 textContent 写入，
 * 禁止 innerHTML / eval / 内联事件，绝不把导入数据按 HTML 解析。
 */
"use strict";

(function () {
  const tokenMeta = document.querySelector('meta[name="continuity-token"]');
  const TOKEN = tokenMeta ? tokenMeta.content : "";

  function api(path) {
    return fetch(path, { headers: { "X-Continuity-Token": TOKEN } }).then(function (res) {
      return res.json().catch(function () {
        return { error: "服务器响应异常（HTTP " + res.status + "）" };
      });
    });
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = text;
    }
  }

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

  function showPage(name) {
    const pages = document.querySelectorAll(".page");
    for (let i = 0; i < pages.length; i++) {
      pages[i].classList.toggle("hidden", pages[i].id !== "page-" + name);
    }
    const buttons = document.querySelectorAll(".nav-btn");
    for (let j = 0; j < buttons.length; j++) {
      buttons[j].classList.toggle("is-active", buttons[j].dataset.page === name);
    }
  }

  const nav = document.getElementById("nav");
  if (nav) {
    nav.addEventListener("click", function (ev) {
      const btn = ev.target && ev.target.closest ? ev.target.closest("button") : null;
      if (btn && btn.dataset.page) {
        showPage(btn.dataset.page);
      }
    });
  }

  /* ---------- 扫描（W2）：POST /api/jobs/scan + 轮询 job 状态 ---------- */

  function clearChildren(el) {
    while (el.firstChild) {
      el.removeChild(el.firstChild);
    }
  }

  function makeLi(text) {
    const li = document.createElement("li");
    li.textContent = text;
    return li;
  }

  function makeLiTagged(tag, text) {
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.textContent = tag;
    span.className = "tag";
    li.appendChild(span);
    li.appendChild(document.createTextNode(" " + text));
    return li;
  }

  function setScanError(text) {
    const box = document.getElementById("scan-error");
    box.textContent = text || "";
    box.classList.toggle("hidden", !text);
  }

  function setScanRunning(running) {
    const run = document.getElementById("scan-run");
    run.disabled = running;
    const state = document.getElementById("scan-state");
    state.textContent = running ? "运行中…（请稍候，扫描为串行任务）" : "";
  }

  function pollJob(jobId, onDone) {
    let finished = false;
    const timer = window.setInterval(function () {
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
          setScanError(snap.error || snap.error_kind || "扫描失败");
          setScanRunning(false);
          if (onDone) { onDone(); }
        }
      });
    }, 300);
  }

  function renderScan(data) {
    const files = Array.isArray(data.files) ? data.files : [];
    const findings = Array.isArray(data.findings) ? data.findings : [];
    const duplicates = Array.isArray(data.duplicates) ? data.duplicates : [];
    const symlinks = Array.isArray(data.skipped_symlinks) ? data.skipped_symlinks : [];

    document.getElementById("scan-summary").textContent =
      "扫描完成：" + files.length + " 个文件（目录：" + (data.root || "") + "）";

    const kinds = {};
    for (let i = 0; i < files.length; i++) {
      const k = files[i].kind || "unknown";
      kinds[k] = (kinds[k] || 0) + 1;
    }
    const kindsBox = document.getElementById("scan-kinds");
    clearChildren(kindsBox);
    const kindNames = Object.keys(kinds).sort();
    for (let j = 0; j < kindNames.length; j++) {
      kindsBox.appendChild(makeLi(kindNames[j] + ": " + kinds[kindNames[j]]));
    }

    const findingsBox = document.getElementById("scan-findings");
    clearChildren(findingsBox);
    document.getElementById("scan-findings-count").textContent = String(findings.length);
    for (let m = 0; m < findings.length; m++) {
      const f = findings[m];
      const level = f.repair_level ? "，修复等级 " + f.repair_level : "";
      const text = f.file + ": " + f.problem + "（证据：" + f.evidence + "；建议：" +
        f.suggestion + level + "）";
      findingsBox.appendChild(makeLiTagged(f.severity, text));
    }

    const dupsBox = document.getElementById("scan-duplicates");
    clearChildren(dupsBox);
    document.getElementById("scan-duplicates-count").textContent = String(duplicates.length);
    for (let d = 0; d < duplicates.length; d++) {
      dupsBox.appendChild(makeLi(duplicates[d].join("、")));
    }

    const linksBox = document.getElementById("scan-symlinks");
    clearChildren(linksBox);
    document.getElementById("scan-symlinks-count").textContent = String(symlinks.length);
    for (let s = 0; s < symlinks.length; s++) {
      linksBox.appendChild(makeLi(symlinks[s]));
    }

    document.getElementById("scan-result").classList.remove("hidden");
  }

  const scanForm = document.getElementById("scan-form");
  if (scanForm) {
    scanForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setScanError("");
      document.getElementById("scan-result").classList.add("hidden");
      const source = document.getElementById("scan-source").value;
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
          setScanError((data && data.error) || "启动扫描任务失败");
          setScanRunning(false);
        }
      });
    });
  }

  loadOverview();
  showPage("overview");
})();
