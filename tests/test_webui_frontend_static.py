"""tests/test_webui_frontend_static.py — 前端静态契约测试（方案甲：tests/ 下新增，不改旧文件）。

覆盖对象（frontend-developer 写作用域，全部只读检查）：
- preview/style-preview.html（风格预览页 v2：Claude 交互骨架 × 暖色两主题，纯预览演示）；
- src/continuity/webui/static/（产品静态资源 index.html/style.css/app.js，前端改版后）。

全部为 Python 静态结构检查（不执行 JS、不依赖浏览器/Node），在受限沙箱内真实可运行。

改版后的测试增删理由（对应 docs/frontend-redesign-brief.md，供交付说明引用）：
- 删除「产品页含 data-page="scan"」断言：扫描已并入首页右侧目录操作区（brief §三/§五），
  导航保留 7 个入口，扫描业务流程（id 与事件绑定）原样保留在 overview 页；
- 新增断言：index.html 零内联样式/脚本（服务端 CSP 契约，brief §九）；
  标题字体栈为宋体系且不含楷体/霞鹜文楷（brief §四）；无粒子/光斑/装饰动画与
  预览演示文案（composer 等，brief §五/§七）；两主题语义令牌齐全且角色稳定（brief §七）；
  触控目标 ≥44px、断点 1024/768/480、reduced-motion（brief §八）；
- 安全断言只增强不弱化：app.js 剥除注释后仍禁 eval/innerHTML/document.write。

边界说明：主题切换/扫描流程的「运行时行为」依赖浏览器环境，本文件只做结构级契约
（CSS 钩子 + JS 函数名 + 事件绑定存在），真实交互验证由浏览器端人工预览完成
（受限沙箱无浏览器，不伪造运行结果，符合 AGENTS.md 规则 10）。
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


def _theme_block(css: str, name: str) -> str:
    """提取某主题（light/dark）的 CSS 变量块正文。"""
    m = re.search(rf"html\[data-theme=\"{name}\"\]\s*\{{(.*?)\}}", css, flags=re.S)
    return m.group(1) if m else ""


@pytest.fixture(scope="module")
def preview() -> str:
    """预览页全文（模块级缓存，避免重复读盘）。"""
    return _read(PREVIEW)


@pytest.fixture(scope="module")
def static_html() -> str:
    """产品入口页全文（只读检查，不修改 developer 的文件）。"""
    return _read(STATIC_DIR / "index.html")


@pytest.fixture(scope="module")
def static_css() -> str:
    """产品样式全文。"""
    return _read(STATIC_DIR / "style.css")


@pytest.fixture(scope="module")
def static_js() -> str:
    """产品前端逻辑全文。"""
    return _read(STATIC_DIR / "app.js")


# ============ 一、文件存在性 ============

def test_preview_exists():
    assert PREVIEW.is_file(), f"预览页不存在: {PREVIEW}"


def test_static_assets_present():
    for name in ("index.html", "style.css", "app.js"):
        assert (STATIC_DIR / name).is_file(), f"产品静态资源缺失: {STATIC_DIR / name}"


# ============ 二、零外部资源契约（规则 2 精神：页面不依赖网络） ============

def test_preview_no_external_urls(preview):
    assert not _URL_RE.search(preview), "预览页含 http(s) URL（契约：零外部资源，data: 除外）"


@pytest.mark.parametrize("name", ["index.html", "style.css", "app.js"])
def test_static_no_external_urls(name):
    src = _read(STATIC_DIR / name)
    assert not _URL_RE.search(src), f"{name} 含外部 URL（产品页契约：零外部网络请求）"


# ============ 三、标签配对 ============

def test_preview_tag_balance(preview):
    errs = _tag_pairs(_strip_script_style_and_comments(preview))
    assert not errs, "预览页标签配对错误: " + "; ".join(errs)


def test_static_index_tag_balance(static_html):
    errs = _tag_pairs(_strip_script_style_and_comments(static_html))
    assert not errs, "产品页标签配对错误: " + "; ".join(errs)


# ============ 四、注释存在性抽查（AGENTS.md 规则 6：代码注释强制） ============

def test_preview_has_block_comments(preview):
    assert len(re.findall(r"/\*", preview)) >= 10, "预览页 CSS/JS 注释数量不足"
    assert len(re.findall(r"<!--", preview)) >= 4, "预览页 HTML 区块注释数量不足"


def test_preview_comments_document_design(preview):
    """关键设计依据必须在注释中说明（注释内容将被审核者审查）。"""
    c = _comments(preview)
    for kw in ("Claude", "主题", "字体", "氛围", "令牌"):
        assert kw in c, f"注释中缺少关键说明: {kw}"


def test_static_files_have_comments():
    """产品三文件必须带中文注释（改版后注释为强制要求）。"""
    for name in ("index.html", "style.css", "app.js"):
        src = _read(STATIC_DIR / name)
        c = _comments(src)
        assert c.strip(), f"{name} 缺少注释"
        assert re.search(r"[\u4e00-\u9fff]", c), f"{name} 注释不含中文"


# ============ 五、预览页关键类名（v2 Claude 骨架 + 原有氛围结构，预览页未参与改版） ============

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


# ============ 六、预览页：主题切换 / 氛围三档 / 粒子开关 / 降级（结构级） ============

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


def test_preview_reduced_motion(preview):
    assert "prefers-reduced-motion" in preview, "缺少系统动效偏好检测"
    assert "matchMedia" in preview, "未使用 matchMedia 监听动效偏好"
    assert "html.reduce" in preview, "缺少 html.reduce 降级 CSS 钩子"


def test_preview_badge_levels(preview):
    for lv in ("R0", "R1", "R2", "R3"):
        assert lv in preview, f"缺少修复等级 {lv}"
    for cls in ("b-r0", "b-r1", "b-r2", "b-r3"):
        assert cls in preview, f"缺少徽章类: {cls}"


def test_preview_bilingual_hero(preview):
    assert "安心回家" in preview, "缺少中文主标题"
    assert "Every story deserves a safe way home" in preview, "缺少英文副标题"


def test_preview_font_plan_documented(preview):
    """页脚必须注明最终 vendoring 方案（创始人要求，防止字体方案漂移）。"""
    for f in ("Cormorant Garamond", "Inter", "霞鹜文楷", "Noto Sans SC", "JetBrains Mono", "OFL"):
        assert f in preview, f"页脚未注明字体 vendoring 方案中的 {f}"


def test_preview_js_safe_baseline(preview):
    js = _section(preview, "script")
    assert "use strict" in js, "JS 缺少 use strict"
    assert "eval(" not in js, "JS 含 eval（规则 3）"
    assert "innerHTML" not in js, "JS 含 innerHTML（规则 3：动态内容必须 textContent/节点 API）"
    assert "textContent" in js, "JS 未使用 textContent 写入动态内容"


# ============ 七、产品页结构契约（改版后：Hero 双栏 + R0-R3 + 导航 7 入口） ============

@pytest.mark.parametrize(
    "cls",
    [
        "topbar", "nav-btn", "page", "hidden", "btn", "btn-primary", "btn-secondary",
        "input", "field", "field-label", "field-hint", "form", "error", "list",
        "state", "tip", "facts", "kv", "badge-readonly", "footer",
        "hero", "hero-work", "hero-copy", "hero-title",
        "levels", "level", "level-list", "level-tag", "scan-summary",
    ],
)
def test_static_index_key_classes(static_html, cls):
    assert cls in static_html, f"产品页缺少关键类: {cls}"


def test_static_index_nav_pages(static_html):
    """导航保留 7 个入口；扫描已并入首页目录操作区（brief §三/§五，见文件头增删理由）。"""
    for page in ("overview", "backup", "verify", "restore", "repair", "migrate", "history"):
        assert f'data-page="{page}"' in static_html, f"产品页缺少导航页: {page}"
    assert 'data-page="scan"' not in static_html, "扫描应并入首页，不再有独立 scan 页"


def test_static_index_token_placeholder_and_label(static_html):
    """服务端把占位符替换为随机令牌并校验「概览」存在（与 test_webui_server.py 契约一致）。"""
    assert 'content="__CONTINUITY_TOKEN__"' in static_html, "缺少令牌占位符 meta"
    assert "概览" in static_html, "缺少概览导航标签（服务端测试依赖）"


def test_static_index_scan_ids_preserved(static_html):
    """扫描业务依赖的 DOM id 一个都不能丢（brief §八：改 DOM 不得丢自动化选择器依赖）。"""
    for el in (
        "scan-form", "scan-source", "scan-run", "scan-state", "scan-error",
        "scan-result", "scan-summary", "scan-kinds", "scan-findings",
        "scan-findings-count", "scan-duplicates", "scan-duplicates-count",
        "scan-symlinks", "scan-symlinks-count",
        "info-tool", "info-version", "info-health", "info-port",
    ):
        assert f'id="{el}"' in static_html, f"产品页缺少扫描流程元素: {el}"


# ============ 八、产品页：零内联样式/脚本（服务端 CSP 契约） ============

def test_static_index_no_inline_style_or_script(static_html):
    """CSP 为 style-src 'self' + script-src 'self'：内联样式/脚本/事件属性一律禁止。"""
    assert "style=" not in static_html, "产品页出现内联 style 属性（CSP 会拦截）"
    assert "<style" not in static_html, "产品页出现内联 <style>（CSP 会拦截）"
    assert "<script>" not in static_html, "产品页出现内联 <script>（CSP 会拦截）"
    for attr in ("onclick=", "onerror=", "onload=", "onmouseover="):
        assert attr not in static_html, f"产品页出现内联事件属性 {attr}"
    assert 'src="/static/app.js"' in static_html, "产品页未引用外部 app.js"
    assert 'href="/static/style.css"' in static_html, "产品页未引用外部 style.css"


# ============ 九、产品页：字体契约（宋体标题、黑体正文、禁楷体/负字距/斜体） ============

def test_static_font_stacks(static_css):
    """brief §四：标题宋体系、正文黑体系，栈序必须与规范一致。"""
    assert '"Noto Serif SC", "Songti SC", "STSong", "SimSun", serif' in static_css, "标题字体栈不符合宋体系规范"
    assert '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif' in static_css, "正文字体栈不符合黑体系规范"
    # 只检查实际声明的 font-family 值——注释中「禁楷体」是合规文档说明，不算违规
    families = ";".join(re.findall(r"font-family:\s*([^;}]+)", static_css))
    for bad in ("楷", "KaiTi", "STKaiti", "霞鹜文楷", "LXGW", "WenKai", "Kaiti"):
        assert bad not in families, f"产品样式 font-family 出现禁用的楷体/手写字体: {bad}"


def test_static_no_italic_or_negative_tracking(static_css):
    """brief §四：不得斜体化、中文标题不照搬西文负字距。"""
    assert "font-style: italic" not in static_css, "产品样式出现斜体（禁用）"
    assert re.search(r"letter-spacing:\s*-", static_css) is None, "产品样式出现负字距（禁用）"


# ============ 十、产品页：无粒子/光斑/装饰动画，动效仅状态反馈 ============

def test_static_no_decorative_animation(static_css, static_html):
    """brief §五/§七：不新增粒子、光斑、循环背景动画；只保留状态反馈动画 spin。"""
    for bad in ("css-particle", "blob", "noise", "backdrop-filter", "drift", "float-up", "shimmer", "stagger"):
        assert bad not in static_css, f"style.css 出现装饰性动画/玻璃元素: {bad}"
        assert bad not in static_html, f"index.html 出现装饰性动画元素: {bad}"
    frames = set(re.findall(r"@keyframes\s+([\w-]+)", static_css))
    assert frames <= {"spin"}, f"只允许状态反馈动画 spin，实际: {frames}"


def test_static_no_preview_demo_artifacts():
    """brief §五：预览页的演示文案/样式（composer、focus-within 等）不得混进产品页。"""
    for name in ("index.html", "style.css", "app.js"):
        src = _read(STATIC_DIR / name)
        for bad in ("composer", "focus-within"):
            assert bad not in src, f"{name} 混入预览页演示内容: {bad}"


# ============ 十一、产品页：两主题语义令牌（角色稳定、含义不随主题改变） ============

SEMANTIC_TOKENS = [
    "--bg", "--surface", "--surface-muted", "--text", "--text-secondary",
    "--placeholder", "--border", "--primary", "--primary-text", "--primary-hover",
    "--focus", "--success", "--warning", "--suggest", "--danger",
]


def test_static_theme_blocks_exist(static_css):
    assert 'html[data-theme="light"]' in static_css, "缺少浅色主题块"
    assert 'html[data-theme="dark"]' in static_css, "缺少深色主题块"


@pytest.mark.parametrize("name", ["light", "dark"])
def test_static_theme_semantic_tokens(static_css, name):
    """每个主题都完整定义同一套语义角色（brief §七：角色稳定，不得随主题缺位）。"""
    block = _theme_block(static_css, name)
    assert block, f"未找到主题块 {name}"
    for token in SEMANTIC_TOKENS:
        assert token in block, f"主题 {name} 缺少语义令牌: {token}"


def test_static_theme_wiring(static_js, static_html):
    assert 'id="theme-toggle"' in static_html, "缺少主题切换按钮"
    assert "applyTheme" in static_js, "app.js 缺少 applyTheme()"
    assert "cs-ui-theme" in static_js, "app.js 缺少主题记忆键"
    assert "prefers-color-scheme" in static_js, "未跟随系统深色偏好取初始主题"
    assert 'aria-pressed="false"' in static_html, "主题切换按钮缺省 aria-pressed 状态"


# ============ 十二、产品页：无障碍与响应式（结构级） ============

def test_static_a11y_hooks(static_html):
    """brief §八：语义提示可被辅助技术读取；图标按钮有可访问名称。"""
    for hook in (
        'role="alert"', 'role="status"', 'aria-live="polite"',
        'aria-pressed', 'aria-label="功能导航"', 'aria-hidden="true"',
        'for="scan-source"',
    ):
        assert hook in static_html, f"缺少无障碍钩子: {hook}"


def test_static_touch_targets(static_css):
    """brief §八：触控目标 ≥44px（主按钮/导航按钮/输入框）。"""
    assert "min-height: 44px" in static_css, "缺少 44px 触控目标"


def test_static_breakpoints_and_reduced_motion(static_css):
    """brief §三/§八：1024/768/480 断点（覆盖 390/320 手机）+ reduced-motion 降级。"""
    for q in ("(max-width: 1024px)", "(max-width: 768px)", "(max-width: 480px)", "(min-width: 768px)"):
        assert q in static_css, f"缺少断点: {q}"
    assert "prefers-reduced-motion" in static_css, "缺少动效降级媒体查询"


# ============ 十三、产品页 JS 契约（安全断言增强：剥注释后检查真实代码） ============

def test_static_app_js_contract(static_js):
    assert "use strict" in static_js, "app.js 缺少 use strict"
    assert "fetch(" in static_js, "app.js 未使用 fetch 调用 API"
    assert "textContent" in static_js, "app.js 未使用 textContent（规则 3 安全纪律）"
    # 剥除注释后检查真实代码：注释里提到的禁用词不算违规，代码里出现才算
    code = re.sub(r"/\*.*?\*/", "", static_js, flags=re.S)
    assert "eval(" not in code, "app.js 真实代码含 eval（规则 3）"
    assert "innerHTML" not in code, "app.js 真实代码含 innerHTML（规则 3）"
    assert "document.write" not in code, "app.js 真实代码含 document.write"


def test_static_scan_business_logic_preserved(static_js):
    """brief §二/§八：不因视觉调整重写业务逻辑——扫描核心函数必须原样存在。"""
    for fn in ("pollJob", "renderScan", "setScanError", "setScanRunning", "loadOverview", "showPage"):
        assert f"function {fn}" in static_js or f"{fn}(" in static_js, f"app.js 缺少业务函数: {fn}"
    assert '"/api/jobs/scan"' in static_js, "app.js 缺少扫描端点"
    assert '"X-Continuity-Token"' in static_js, "app.js 缺少令牌头"


@pytest.mark.parametrize(
    "cls",
    [
        "topbar", "nav-btn", "facts", "kv", "tip", "hidden", "badge-readonly",
        "form", "field", "field-label", "field-hint", "input", "btn",
        "btn-primary", "btn-secondary", "state", "error", "list", "tag", "footer",
        "hero", "hero-work", "hero-copy", "hero-title", "hero-sub", "hero-note",
        "hero-actions", "levels", "level", "level-list", "level-tag",
        "level-icon", "level-body", "level-head", "level-name", "level-desc",
        "section-title", "section-desc", "form-actions", "scan-summary",
        "pledge", "brand", "info-block",
    ],
)
def test_static_style_css_contract(static_css, cls):
    assert f".{cls}" in static_css, f"style.css 缺少选择器: .{cls}"
