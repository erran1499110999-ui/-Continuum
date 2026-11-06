"""W1：入参校验纯函数测试（路径、目录关系、Host 白名单、JSON 请求体）。"""
from __future__ import annotations

import pytest

from continuity.webui.validation import (
    ValidationError,
    host_is_allowed,
    parse_json_body,
    require_new_output_dir,
    require_path,
    require_source_dir,
)


# —— require_path ——

def test_require_path_ok():
    assert require_path("D:\\数据 目录") == "D:\\数据 目录"
    assert require_path("中文目录名") == "中文目录名"


@pytest.mark.parametrize("bad", ["", "   ", None, 123])
def test_require_path_empty_or_wrong_type(bad):
    with pytest.raises(ValidationError):
        require_path(bad)


@pytest.mark.parametrize("bad", ["a\x00b", "a\nb", "a\tb", "a\x7fb"])
def test_require_path_control_chars(bad):
    with pytest.raises(ValidationError):
        require_path(bad)


# —— require_source_dir ——

def test_require_source_dir_ok(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    assert require_source_dir(str(src)) == src.resolve()


def test_require_source_dir_missing(tmp_path):
    with pytest.raises(ValidationError):
        require_source_dir(str(tmp_path / "nope"))


def test_require_source_dir_is_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(ValidationError):
        require_source_dir(str(f))


# —— require_new_output_dir ——

def test_require_new_output_dir_ok(tmp_path):
    out = require_new_output_dir(str(tmp_path / "out"))
    assert out == (tmp_path / "out").resolve()
    assert not out.exists()


def test_require_new_output_dir_exists_rejected(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(ValidationError):
        require_new_output_dir(str(out))


def test_require_new_output_dir_inside_source_rejected(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    with pytest.raises(ValidationError):
        require_new_output_dir(str(src / "out"), source=str(src))


def test_require_new_output_dir_equals_source_rejected(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    with pytest.raises(ValidationError):
        require_new_output_dir(str(src), source=str(src))


def test_require_new_output_dir_sibling_ok(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    out = require_new_output_dir(str(tmp_path / "source-out"), source=str(src))
    assert out == (tmp_path / "source-out").resolve()


# —— host_is_allowed ——

@pytest.mark.parametrize(
    "host",
    ["127.0.0.1", "127.0.0.1:8765", "localhost", "localhost:8765", "LOCALHOST:1"],
)
def test_host_is_allowed_yes(host):
    assert host_is_allowed(host) is True


@pytest.mark.parametrize(
    "host",
    [
        "",
        "evil.example",
        "evil.example:80",
        "192.168.1.1",
        "127.0.0.2",
        "localhost.evil",
        "127.0.0.1.evil",
        "[::1]:8765",
    ],
)
def test_host_is_allowed_no(host):
    assert host_is_allowed(host) is False


# —— parse_json_body ——

def test_parse_json_body_ok():
    assert parse_json_body(b'{"a": 1}') == {"a": 1}


def test_parse_json_body_utf8_chinese():
    assert parse_json_body('{"p": "中文 路径"}'.encode("utf-8")) == {"p": "中文 路径"}


def test_parse_json_body_invalid():
    with pytest.raises(ValidationError):
        parse_json_body(b"not json")


def test_parse_json_body_non_object():
    with pytest.raises(ValidationError):
        parse_json_body(b"[1, 2]")


def test_parse_json_body_too_large():
    with pytest.raises(ValidationError):
        parse_json_body(b"{}", max_bytes=1)


def test_parse_json_body_empty():
    with pytest.raises(ValidationError):
        parse_json_body(b"")
