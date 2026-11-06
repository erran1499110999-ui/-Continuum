"""目录扫描测试：类型识别、发现提示与重复检测。"""

from continuity.models import FileKind
from continuity.scanners.scan import scan_directory


def test_scan_report_kinds(sample_tree):
    report = scan_directory(sample_tree)
    kinds = {f.rel_path: f.kind for f in report.files}
    assert kinds["characters/角色卡.json"] is FileKind.CHARACTER_CARD_JSON
    assert kinds["characters/my card.png"] is FileKind.CHARACTER_CARD_PNG
    assert kinds["chats/chat.jsonl"] is FileKind.CHAT_JSONL
    assert kinds["notes.txt"] is FileKind.TEXT
    assert kinds["broken.json"] is FileKind.TEXT


def test_scan_reports_broken_json_finding(sample_tree):
    report = scan_directory(sample_tree)
    assert any("损坏" in f.problem for f in report.findings)


def test_scan_detects_duplicates(tmp_path):
    root = tmp_path / "d"
    root.mkdir()
    (root / "a.txt").write_text("same", encoding="utf-8")
    (root / "b.txt").write_text("same", encoding="utf-8")
    report = scan_directory(root)
    assert len(report.duplicates) == 1
    assert len(report.duplicates[0]) == 2


def test_scan_missing_dir_raises(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError, match="目录不存在"):
        scan_directory(tmp_path / "nope")


def test_scan_reports_corrupt_png(tmp_path):
    from helpers import make_png

    root = tmp_path / "d"
    root.mkdir()
    data = bytearray(make_png())
    data[16] ^= 0xFF  # CRC 损坏
    (root / "bad.png").write_bytes(bytes(data))
    report = scan_directory(root)
    assert any("PNG" in f.problem for f in report.findings)


def test_scan_enforces_limits(tmp_path):
    import pytest

    from continuity.limits import ResourceLimits
    from continuity.scanners.scan import ScanError

    root = tmp_path / "d"
    root.mkdir()
    (root / "a.txt").write_text("x" * 100, encoding="utf-8")
    with pytest.raises(ScanError, match="上限"):
        scan_directory(root, limits=ResourceLimits(max_total_bytes=10))
