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

  loadOverview();
  showPage("overview");
})();
