"""tests/test_webui_frontend_static.py — 前端静态契约测试（方案甲：tests/ 下新增，不改旧文件）。

覆盖对象（frontend-developer 写作用域，全部只读检查）：
- preview/style-preview.html（风格预览页 v2：Claude 交互骨架 × 暖色两主题）；
- src/continuity/webui/static/（产品静态资源 index.html/style.css/app.js）。

全部为 Python 静态结构检查（不执行 JS、不依赖浏览器/Node），在受限沙箱内真实可运行：
1. 标签配对：剥除 <script>/<style> 块与 HTML 注释后做栈式配对检查
   （避免 JS 中的 `<` 比较符、CSS 中的选择器被误判为标签）；
2. 无外部 URL：页面契约 = 零外部资源（data: URI 允许，协议相对/绝对 http(s) 均禁止）；
3. 中文注释存在性抽查：AGENTS.md 规则 6「代码注释强制」，注释由审核者审查；
4. 关键类名/结构钩子：主题切换、氛围三档、粒子开关、reduced-motion 的结构级验证。

边界说明：主题切换/氛围档位/粒子开关的「运行时行为」依赖浏览器环境，本文件只做
结构级契约（CSS 钩子 + JS 函数名 + 事件绑定存在），真实交互验证由浏览器端人工
预览完成（受限沙箱无浏览器，不伪造运行结果，符合 AGENTS.md 规则 10）。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "preview" / "style-preview.html"
STATIC_DIR = ROOT / "src" / "continuity" / "webui" / "static"

# 无闭合标签的 HTML void 元素（不参与配对）
_VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

_URL_RE = re.compile(r"https?://", re.IGNORECASE)  # 任何 http(s) URL 都视为外部


def _read(path: Path) -> str:
    """以 UTF-8 读取文本文件。"""
    return path.read_text(encoding="utf-8")


def _strip_script_style_and_comments(src: str) -> str:
    """剥除 <script>/<style> 块与 HTML 注释，返回纯标签结构。

    JS/CSS 内部的 <、> 字符（如 `p.y < -12`、`@media (max-width: 900px)`）会被
    整块剥除，不参与标签配对，避免误判。
    """
    src = re.sub(r"(?is)<(script|style)\b.*?</\1\s*>", "", src)
    src = re.sub(r"(?s)<!--.*?-->", "", src)
    return src


def _tag_pairs(src: str) -> list[str]:
    """栈式标签配对检查，返回错误列表（空列表 = 通过）。"""
    errors: list[str] = []
    stack: list[str] = []
    for m in re.finditer(r"<(/)?\s*([a-zA-Z][a-zA-Z0-9-]*)\b[^>]*>", src):
        raw = m.group(0)
        closing = m.group(1) == "/"
        name = m.group(2)
        if closing:
            if not stack:
                errors.append(f"多余闭合标签 </{name}>")
                continue
            if stack[-1] == name:
                stack.pop()
            else:
                errors.append(f"标签不匹配：期望 </{stack[-1]}>，实际 </{name}>")
        else:
            if raw.endswith("/>") or name.lower() in _VOID_TAGS:
                continue  # 自闭合或 void 标签不配对
            stack.append(name)
    for name in reversed(stack):
        errors.append(f"未闭合标签 <{name}>")
    return errors


def _section(src: str, tag: str) -> str:
    """取出页面内第一个 <tag>…</tag> 块的内容（用于单独检查 CSS/JS）。"""
    m = re.search(rf"(?is)<{tag}[^>]*>(.*?)</{tag}>", src)
    return m.group(1) if m else ""


def _comments(src: str) -> str:
    """提取全部 CSS/JS 块注释与 HTML 注释的正文（供注释存在性抽查）。"""
    parts = re.findall(r"/\*.*?\*/", src, flags=re.S)
    parts += re.findall(r"<!--.*?-->", src, flags=re.S)
    return "\n".join(parts)


@pytest.fixture(scope="module")
def preview() -> str:
    """预览页全文（模块级缓存，避免重复读盘）。"""
    return _read(PREVIEW)


@pytest.fixture(scope="module")
def static_html() -> str:
    """产品入口页全文（只读检查，不修改 developer 的文件）。"""
    return _read(STATIC_DIR / "index.html")


# —— 文件存在性 ——

def test_preview_exists():
    assert PREVIEW.is_file(), f"预览页不存在: {PREVIEW}"


def test_static_assets_present():
    for name in ("index.html", "style.css", "app.js"):
        assert (STATIC_DIR / name).is_file(), f"产品静态资源缺失: {STATIC_DIR / name}"


# —— 零外部资源契约（规则 2 精神：页面不依赖网络） ——

def test_preview_no_external_urls(preview):
    assert not _URL_RE.search(preview), "预览页含 http(s) URL（契约：零外部资源，data: 除外）"


@pytest.mark.parametrize("name", ["index.html", "style.css", "app.js"])
def test_static_no_external_urls(name):
    src = _read(STATIC_DIR / name)
    assert not _URL_RE.search(src), f"{name} 含外部 URL（产品页契约：零外部网络请求）"


# —— 标签配对 ——

def test_preview_tag_balance(preview):
    errs = _tag_pairs(_strip_script_style_and_comments(preview))
    assert not errs, "预览页标签配对错误: " + "; ".join(errs)


def test_static_index_tag_balance(static_html):
    errs = _tag_pairs(_strip_script_style_and_comments(static_html))
    assert not errs, "产品页标签配对错误: " + "; ".join(errs)


# —— 注释存在性抽查（AGENTS.md 规则 6：代码注释强制） ——

def test_preview_has_block_comments(preview):
    assert len(re.findall(r"/\*", preview)) >= 10, "预览页 CSS/JS 注释数量不足"
    assert len(re.findall(r"<!--", preview)) >= 4, "预览页 HTML 区块注释数量不足"


def test_preview_comments_document_design(preview):
    """关键设计依据必须在注释中说明（注释内容将被审核者审查）。"""
    c = _comments(preview)
    for kw in ("Claude", "主题", "字体", "氛围", "令牌"):
        assert kw in c, f"注释中缺少关键说明: {kw}"


# —— 预览页关键类名（v2 Claude 骨架 + 原有氛围结构） ——

@pytest.mark.parametrize(
    "cls",
    [
        "btn-primary", "btn-secondary", "btn-text", "btn-icon", "btn-danger",
        "glass", "badge", "seg", "composer", "skeleton", "spinner",
        "css-particles", "blob", "noise", "stagger-list", "mono",
    ],
)
def test_preview_key_classes(preview, cls):
    assert f".{cls}" in preview, f"预览页缺少关键类选择器: .{cls}"


# —— 主题切换（结构级：CSS 钩子 + JS 函数 + 按钮绑定） ——

def test_preview_theme_tokens(preview):
    for token in (
        "--bg-canvas", "--accent", "--surface-glass", "--on-accent",
        "--font-display", "--font-body", "--r-md", "--sp-section", "--dur-fast",
    ):
        assert token in preview, f"预览页缺少设计令牌: {token}"
    assert 'html[data-theme="sun"]' in preview, "缺少亮色主题钩子"
    assert 'html[data-theme="forest"]' in preview, "缺少暗色主题钩子"


def test_preview_theme_wiring(preview):
    js = _section(preview, "script")
    assert "setTheme" in js, "JS 缺少 setTheme()"
    assert 'id="theme-sun"' in preview and 'id="theme-forest"' in preview, "缺少主题切换按钮"
    assert 'aria-pressed="true"' in preview, "分段控件缺省 aria-pressed 状态"


# —— 氛围三档与粒子开关（结构级） ——

def test_preview_fx_levels_css(preview):
    assert 'body[data-fx="off"]' in preview, "缺少「氛围：关」CSS 钩子"
    assert 'body[data-fx="standard"]' in preview, "缺少「标准」档 CSS 钩子"
    assert '=== "rich"' in preview, "缺少「丰富」档 canvas 判定"


def test_preview_fx_wiring(preview):
    js = _section(preview, "script")
    assert "setFx" in js, "JS 缺少 setFx()"
    assert "syncCanvas" in js, "JS 缺少 syncCanvas()"
    for el in ("fx-off", "fx-standard", "fx-rich"):
        assert f'id="{el}"' in preview, f"缺少氛围档位按钮: {el}"


def test_preview_particle_wiring(preview):
    assert 'id="fx-canvas"' in preview, "缺少 canvas 粒子层"
    assert "requestAnimationFrame" in preview and "cancelAnimationFrame" in preview, "canvas 未使用 rAF 生命周期"
    # CSS-only 粒子固定 14 粒（结构契约：数量变化需同步设计文档）
    assert preview.count('class="css-particle"') == 14, "CSS 粒子数量不再是 14 粒"


# —— reduced-motion 降级（结构级） ——

def test_preview_reduced_motion(preview):
    assert "prefers-reduced-motion" in preview, "缺少系统动效偏好检测"
    assert "matchMedia" in preview, "未使用 matchMedia 监听动效偏好"
    assert "html.reduce" in preview, "缺少 html.reduce 降级 CSS 钩子"


# —— R0–R3 徽章（文字+图标双通道） ——

def test_preview_badge_levels(preview):
    for lv in ("R0", "R1", "R2", "R3"):
        assert lv in preview, f"缺少修复等级 {lv}"
    for cls in ("b-r0", "b-r1", "b-r2", "b-r3"):
        assert cls in preview, f"缺少徽章类: {cls}"


# —— 双语 Hero 与字体 vendoring 方案声明 ——

def test_preview_bilingual_hero(preview):
    assert "安心回家" in preview, "缺少中文主标题"
    assert "Every story deserves a safe way home" in preview, "缺少英文副标题"


def test_preview_font_plan_documented(preview):
    """页脚必须注明最终 vendoring 方案（创始人要求，防止字体方案漂移）。"""
    for f in ("Cormorant Garamond", "Inter", "霞鹜文楷", "Noto Sans SC", "JetBrains Mono", "OFL"):
        assert f in preview, f"页脚未注明字体 vendoring 方案中的 {f}"


# —— 预览页 JS 安全基线（与产品页同一纪律：动态内容只走 textContent） ——

def test_preview_js_safe_baseline(preview):
    js = _section(preview, "script")
    assert "use strict" in js, "JS 缺少 use strict"
    assert "eval(" not in js, "JS 含 eval（规则 3）"
    assert "innerHTML" not in js, "JS 含 innerHTML（规则 3：动态内容必须 textContent/节点 API）"
    assert "textContent" in js, "JS 未使用 textContent 写入动态内容"


# —— 产品静态资源结构契约（只读检查 developer 的文件） ——

@pytest.mark.parametrize(
    "cls",
    ["topbar", "nav-btn", "page", "hidden", "btn", "input", "field", "form",
     "error", "list", "state", "tip", "facts", "kv", "badge-readonly", "footer"],
)
def test_static_index_key_classes(static_html, cls):
    assert cls in static_html, f"产品页缺少关键类: {cls}"


def test_static_index_nav_pages(static_html):
    for page in ("overview", "scan", "backup", "verify", "restore", "repair", "migrate", "history"):
        assert f'data-page="{page}"' in static_html, f"产品页缺少导航页: {page}"


def test_static_index_asset_references(static_html):
    assert 'src="/static/app.js"' in static_html, "产品页未引用 app.js"
    assert 'href="/static/style.css"' in static_html, "产品页未引用 style.css"


def test_static_app_js_contract():
    js = _read(STATIC_DIR / "app.js")
    assert "use strict" in js, "app.js 缺少 use strict"
    assert "fetch(" in js, "app.js 未使用 fetch 调用 API"
    assert "textContent" in js, "app.js 未使用 textContent（规则 3 安全纪律）"


@pytest.mark.parametrize(
    "cls",
    ["topbar", "nav-btn", "facts", "kv", "tip", "hidden", "badge-readonly",
     "form", "field", "field-label", "input", "btn", "state", "error", "list", "footer"],
)
def test_static_style_css_contract(cls):
    css = _read(STATIC_DIR / "style.css")
    assert f".{cls}" in css, f"style.css 缺少选择器: .{cls}"
