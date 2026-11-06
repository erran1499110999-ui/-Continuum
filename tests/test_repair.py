"""修复引擎测试：源只读、R0 自动修复、R2 建议、R3 隔离与 diff 报告。"""

import json

import pytest

from continuity.repair import RepairError, apply_repairs


@pytest.fixture
def broken_tree(tmp_path):
    root = tmp_path / "srcdata"
    root.mkdir()
    (root / "good.json").write_text(json.dumps({"a": 1}), encoding="utf-8")
    (root / "trailing.json").write_text('{\n  "name": "x",\n}\n', encoding="utf-8")
    (root / "bom.json").write_text('\ufeff{"a": 1}', encoding="utf-8")
    (root / "truncated.json").write_text('{"a": 1, "b": [1, 2', encoding="utf-8")
    (root / "run.bat").write_bytes(b"@echo off\r\n")
    (root / "note.txt").write_text("hello", encoding="utf-8")
    return root


def _snapshot(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }


def test_source_never_modified(broken_tree, tmp_path):
    before = _snapshot(broken_tree)
    out = tmp_path / "fixed"
    apply_repairs(broken_tree, out)
    assert _snapshot(broken_tree) == before


def test_trailing_comma_fixed(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    report = apply_repairs(broken_tree, out)
    fixed = json.loads((out / "trailing.json").read_text(encoding="utf-8"))
    assert fixed == {"name": "x"}
    assert any(f["rule_id"] == "R0-001" and f["file"] == "trailing.json" for f in report.fixes)
    assert report.r0_applied >= 1


def test_bom_stripped(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    apply_repairs(broken_tree, out)
    text = (out / "bom.json").read_text(encoding="utf-8")
    assert not text.startswith("\ufeff")
    assert json.loads(text) == {"a": 1}


def test_valid_and_text_untouched(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    apply_repairs(broken_tree, out)
    assert (out / "good.json").read_bytes() == (broken_tree / "good.json").read_bytes()
    assert (out / "note.txt").read_text(encoding="utf-8") == "hello"
    assert (out / "trailing.json").read_bytes() != (broken_tree / "trailing.json").read_bytes()


def test_truncated_json_r2_advice(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    report = apply_repairs(broken_tree, out)
    assert (out / "truncated.json").read_bytes() == (broken_tree / "truncated.json").read_bytes()
    files = [a["file"] for a in report.r2_advice]
    assert "truncated.json" in files
    assert "trailing.json" not in files  # 已 R0 修复的文件不再给 R2 建议


def test_executable_r3_isolated(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    report = apply_repairs(broken_tree, out)
    assert any(i["file"] == "run.bat" for i in report.r3_isolated)
    assert (out / "run.bat").is_file()  # 隔离 = 复制但不执行、不解析


def test_diff_recorded_and_report_written(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    report = apply_repairs(broken_tree, out)
    fix = next(f for f in report.fixes if f["file"] == "trailing.json")
    assert fix["before_sha256"] != fix["after_sha256"]
    assert '-  "name": "x",' in fix["diff"]
    assert (out / "diffs" / "trailing.json.diff").is_file()
    raw = json.loads((out / "repair-report.json").read_text(encoding="utf-8"))
    assert raw["files_total"] == 6
    assert raw["files_repaired"] >= 2  # trailing + bom


def test_refuses_existing_output(broken_tree, tmp_path):
    out = tmp_path / "fixed"
    apply_repairs(broken_tree, out)
    with pytest.raises(RepairError, match="已存在"):
        apply_repairs(broken_tree, out)


def test_refuses_output_inside_source(broken_tree):
    with pytest.raises(RepairError, match="源目录之内"):
        apply_repairs(broken_tree, broken_tree / "inner")
