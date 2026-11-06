"""P1：ST 插件（extensions/sillytavern/continuity-st/）静态契约测试。

全部为 Python 静态检查（不执行 JS、不依赖 Node），在受限沙箱内真实可运行：
- manifest.json schema 校验（必填字段/语义版本/license/引用文件存在）；
- JS 源码安全 lint（无 eval/innerHTML/外部 URL/存储/密钥字样/网络 API/import 内部模块）；
- checks.js 占位与双语 README 占位检查。

与 docs/st-plugin-plan.md 第 4 节 P1 验收要点一一对应。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

EXT_DIR = Path(__file__).resolve().parent.parent / "extensions" / "sillytavern" / "continuity-st"

EXPECTED_FILES = {"manifest.json", "index.js", "checks.js", "style.css", "README.md", "package.json"}

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _read(name: str) -> str:
    return (EXT_DIR / name).read_text(encoding="utf-8")


# —— 目录与文件集合 ——

def test_extension_dir_exists_with_expected_files():
    assert EXT_DIR.is_dir(), f"插件目录不存在: {EXT_DIR}"
    actual = {p.name for p in EXT_DIR.iterdir() if p.is_file()}
    assert EXPECTED_FILES <= actual, f"缺少文件: {EXPECTED_FILES - actual}"


def test_no_junk_files_in_extension_dir():
    for p in EXT_DIR.iterdir():
        if p.is_file():
            assert p.suffix not in {".pyc", ".tmp", ".bak"}, f"发现垃圾文件: {p.name}"
            assert not p.name.startswith("."), f"发现隐藏文件: {p.name}"


# —— manifest.json schema ——

@pytest.fixture(scope="module")
def manifest():
    raw = (EXT_DIR / "manifest.json").read_text(encoding="utf-8")
    return json.loads(raw)


def test_manifest_is_valid_json(manifest):
    assert isinstance(manifest, dict)


@pytest.mark.parametrize(
    "field",
    ["manifest_version", "display_name", "js", "css", "author", "version", "homePage", "license", "minimum_client_version"],
)
def test_manifest_required_fields(manifest, field):
    assert field in manifest, f"manifest 缺少字段: {field}"
    assert manifest[field], f"manifest 字段为空: {field}"


def test_manifest_version_is_semver(manifest):
    assert _SEMVER.match(str(manifest["version"])), f"版本号不是语义版本: {manifest['version']}"


def test_manifest_minimum_client_version_is_1_12_0(manifest):
    assert manifest["minimum_client_version"] == "1.12.0"
    assert _SEMVER.match(str(manifest["minimum_client_version"]))


def test_manifest_license_is_mit(manifest):
    assert manifest["license"] == "MIT"


def test_manifest_referenced_js_css_exist(manifest):
    assert (EXT_DIR / manifest["js"]).is_file(), f"manifest.js 指向的文件不存在: {manifest['js']}"
    assert (EXT_DIR / manifest["css"]).is_file(), f"manifest.css 指向的文件不存在: {manifest['css']}"


# —— JS 源码安全 lint（index.js + checks.js；先剥除注释，只检实际代码） ——

def _strip_comments(source: str) -> str:
    """剥除 JS 注释（/* */ 与 //），但**保留字符串与模板字面量内容**。

    状态机（QA P1-1 方案 A）：正确跟踪 '' / "" / `` / 转义与模板插值 ${...}，
    只把「真实注释」剥掉——字符串里的 `http://x`、`//` 是数据不是注释，
    必须保留供 URL/网络 API 检查检出（否则可被投毒绕过）。
    """
    out: list = []
    stack = ["code"]  # code | line | block | single | double | template | interp
    i = 0
    n = len(source)
    while i < n:
        state = stack[-1]
        ch = source[i]
        nxt = source[i + 1] if i + 1 < n else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                stack.append("line")
                i += 2
            elif ch == "/" and nxt == "*":
                stack.append("block")
                i += 2
            elif ch == "'":
                stack.append("single")
                out.append(ch)
                i += 1
            elif ch == '"':
                stack.append("double")
                out.append(ch)
                i += 1
            elif ch == "`":
                stack.append("template")
                out.append(ch)
                i += 1
            else:
                out.append(ch)
                i += 1
        elif state == "line":
            if ch == "\n":  # 保留换行，避免跨行 token 粘连
                stack.pop()
                out.append(ch)
            i += 1
        elif state == "block":
            if ch == "*" and nxt == "/":
                stack.pop()
                i += 2
            else:
                i += 1
        elif state in ("single", "double"):
            quote = "'" if state == "single" else '"'
            out.append(ch)
            if ch == "\\" and i + 1 < n:  # 转义：跳过下一个字符（如 \" 与 \'）
                out.append(source[i + 1])
                i += 2
                continue
            if ch == quote:
                stack.pop()
            i += 1
        elif state == "template":
            out.append(ch)
            if ch == "\\" and i + 1 < n:  # 转义（如 \`）
                out.append(source[i + 1])
                i += 2
                continue
            if ch == "`":
                stack.pop()
                i += 1
                continue
            if ch == "$" and nxt == "{":  # 模板插值：${...} 内按代码处理
                stack.append("interp")
                out.append(ch)
                out.append(nxt)
                i += 2
                continue
            i += 1
        elif state == "interp":
            # 模板插值内的代码：花括号配对 + 嵌套字符串/注释
            if ch == "{":
                out.append(ch)
                stack.append("interp-brace")
                i += 1
            elif ch == "}":
                stack.pop()  # 回到 template
                out.append(ch)
                i += 1
            elif ch == "/" and nxt == "/":
                stack.append("line")
                i += 2
            elif ch == "/" and nxt == "*":
                stack.append("block")
                i += 2
            elif ch == "'":
                stack.append("single")
                out.append(ch)
                i += 1
            elif ch == '"':
                stack.append("double")
                out.append(ch)
                i += 1
            elif ch == "`":
                stack.append("template")
                out.append(ch)
                i += 1
            else:
                out.append(ch)
                i += 1
        elif state == "interp-brace":
            if ch == "{":
                stack.append("interp-brace")
                out.append(ch)
                i += 1
            elif ch == "}":
                stack.pop()
                out.append(ch)
                i += 1
            else:
                out.append(ch)
                i += 1
    return "".join(out)


@pytest.fixture(scope="module", params=["index.js", "checks.js"])
def js_source(request):
    return request.param, _strip_comments(_read(request.param))


_EXTERNAL_URL = re.compile(r"https?://", re.IGNORECASE)


def _no_external_urls(source: str) -> bool:
    """任何 http(s) URL 都视为外部——插件契约：除 127.0.0.1 外零网络。

    检查 127.0.0.1 引用不算外部（唤起目标地址允许出现）。
    """
    for m in _EXTERNAL_URL.finditer(source):
        tail = source[m.end(): m.end() + 32]
        if "127.0.0.1" not in tail:
            return False
    return True


def test_js_no_eval(js_source):
    name, src = js_source
    assert "eval(" not in src, f"{name} 含 eval()（规则 3）"


def test_js_no_innerhtml(js_source):
    name, src = js_source
    assert "innerHTML" not in src, f"{name} 含 innerHTML（规则 3：动态内容必须 textContent/节点 API）"


def test_js_no_document_write(js_source):
    name, src = js_source
    assert "document.write" not in src, f"{name} 含 document.write"


def test_js_no_external_urls(js_source):
    name, src = js_source
    assert _no_external_urls(src), f"{name} 含外部 URL（规则 2：插件零外部网络请求，127.0.0.1 除外）"


def test_js_no_localstorage(js_source):
    name, src = js_source
    assert "localStorage" not in src, f"{name} 使用 localStorage（持久化必须走 extensionSettings）"


_KEY_PATTERNS = ("api_key", "apikey", "apiKey", "Bearer ", "secret_key", "access_token")


def test_js_no_key_literals(js_source):
    name, src = js_source
    for pat in _KEY_PATTERNS:
        assert pat not in src, f"{name} 含密钥相关字样: {pat!r}（规则 2：插件不接触密钥）"


def test_js_no_network_apis(js_source):
    name, src = js_source
    for api in ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource"):
        assert api not in src, f"{name} 使用网络 API {api}（MVP 契约：仅 window.open 唤起，零跨域调用）"


_IMPORT_SOURCE = re.compile(r"\bimport\s+(?:[^\"';]*?\s+from\s+)?[\"']([^\"']+)[\"']")


def test_js_imports_only_relative_local_modules(js_source):
    """P2 起 index.js 允许 import 插件自有模块（如 ./checks.js），
    但只允许插件目录内的相对路径——绝不 import ST 内部模块或外部包。"""
    name, src = js_source
    sources = _IMPORT_SOURCE.findall(src)
    for s in sources:
        assert s.startswith("./"), f"{name} import 了非相对模块: {s!r}（契约：禁止 import ST 内部模块）"
        assert ".." not in s, f"{name} import 逃出插件目录: {s!r}"
        assert s.endswith(".js"), f"{name} import 了非 JS 文件: {s!r}"


def test_js_no_st_script_imports(js_source):
    """ST 内部入口（script.js）绝不能被插件 import（官方最佳实践：只用 getContext）。"""
    name, src = js_source
    assert "script.js" not in src, f"{name} 引用了 ST 内部模块 script.js"


def test_js_no_r_level_judgments_in_code(js_source):
    """R 级修复判定只由 Python 引擎给出——插件 JS 的实际代码中不得出现 R0–R3。"""
    name, src = js_source
    for token in ("R0", "R1", "R2", "R3"):
        assert token not in src, f"{name} 代码中含 {token}（规则 4/9：插件只提示不判定）"


# —— 回归（P1-1）：字符串/模板字面量不得被注释剥除误伤 ——

def test_strip_comments_keeps_url_in_string_detected():
    """回归（P1-1 ①）：字符串内的恶意 URL 必须被保留并检出，不能当注释剥掉漏检。"""
    src = 'const u = "http://evil.example/x";\n'
    stripped = _strip_comments(src)
    assert "http://evil.example" in stripped, "字符串内 URL 被误剥（漏检）"
    assert _no_external_urls(stripped) is False, "字符串内恶意 URL 未被检出"


def test_strip_comments_string_slash_not_swallow_following_code():
    """回归（P1-1 ②）：字符串内 `//` 是数据不是注释，其后真实代码（fetch）必须仍可检出。"""
    src = 'const path = "a//b";\nconst r = fetch("/api");\n'
    stripped = _strip_comments(src)
    assert "a//b" in stripped, "字符串内容被误当注释剥掉"
    assert "fetch(" in stripped, "字符串后的真实代码被注释剥除吞掉（fetch 漏检）"
    assert _no_external_urls(stripped) is True, "相对路径 fetch 不应被误报为外部 URL"


def test_index_js_contract():
    src = _read("index.js")
    assert "SillyTavern.getContext" in src, "index.js 未使用 getContext()"
    assert "APP_READY" in src, "index.js 未注册 APP_READY"
    assert "use strict" in src
    assert 'const VERSION = "0.1.0"' in src, "index.js 无版本常量"


# —— checks.js 契约（P2：H1–H5 纯函数已实现） ——

def test_checks_js_exports():
    src = _read("checks.js")
    for fn in (
        "buildSnapshot",
        "checkIntegrity",
        "checkResetChat",
        "checkDuplicateNames",
        "checkCardFields",
        "checkMessageStructure",
        "runChecks",
    ):
        assert f"export function {fn}" in src, f"checks.js 缺少导出: {fn}"
    assert "use strict" in src
    assert "无副作用" in src, "checks.js 应声明无副作用原则"


def test_index_js_has_check_panel():
    """P2 契约：面板含「开始体检」按钮，经 runChecks 渲染，全程 textContent。"""
    src = _read("index.js")
    assert "continuity-check-run" in src, "index.js 缺少体检按钮"
    assert "runChecks" in src, "index.js 未调用 checks.js 的 runChecks"
    assert "textContent" in src, "index.js 渲染必须使用 textContent（规则 3）"


def test_package_json_declares_module():
    """Node 需要 type=module 才能以 ESM 加载 checks.js（node:test 前置条件）。"""
    p = EXT_DIR / "package.json"
    assert p.is_file(), "缺少 package.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("type") == "module"
    assert data.get("private") is True


# —— 双语 README 占位 ——

def test_readme_bilingual_placeholder():
    src = _read("README.md")
    assert "TODO-P4" in src, "README 应含 TODO-P4 占位标记"
    assert "Installation" in src and "安装" in src, "README 缺英文/中文安装章节"
    assert "Privacy Statement" in src and "隐私声明" in src, "README 缺英文/中文隐私声明"
    assert "127.0.0.1" in src, "README 应说明仅访问 127.0.0.1"
    assert "MIT" in src, "README 应标注 MIT 许可证"
    assert "1.12.0" in src, "README 应标注 minimum_client_version 1.12.0"


def test_manifest_display_name_matches_readme():
    manifest = json.loads((EXT_DIR / "manifest.json").read_text(encoding="utf-8"))
    src = _read("README.md")
    assert manifest["display_name"] in src, "README 标题应与 manifest display_name 一致"
