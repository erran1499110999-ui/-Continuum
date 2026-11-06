"""备份引擎测试：往返、源只读、安全边界与完整性校验。"""

from pathlib import Path

import pytest

from continuity.backup import (
    BackupError,
    BackupOptions,
    create_backup,
    restore_backup,
    safe_join,
    verify_bundle,
)
from continuity.hashing import sha256_file


def _snapshot(root: Path) -> dict:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_backup_restore_roundtrip(sample_tree, tmp_path):
    before = _snapshot(sample_tree)
    bundle = tmp_path / "bundle"
    manifest = create_backup(sample_tree, bundle)
    assert len(manifest.entries) == 5
    assert _snapshot(sample_tree) == before  # 源目录未被修改

    dest = tmp_path / "restored"
    report = restore_backup(bundle, dest)
    assert report.ok
    assert report.restored == 5
    for entry in manifest.entries:
        restored_file = dest / entry.rel_path
        assert restored_file.is_file()
        assert sha256_file(restored_file) == entry.sha256
    assert _snapshot(dest) == _snapshot(sample_tree)


def test_manifest_hash_matches_source(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    manifest = create_backup(sample_tree, bundle)
    for entry in manifest.entries:
        assert sha256_file(sample_tree / entry.rel_path) == entry.sha256
        assert (bundle / "files" / entry.rel_path).read_bytes() == (
            sample_tree / entry.rel_path
        ).read_bytes()


def test_refuses_existing_bundle(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    create_backup(sample_tree, bundle)
    with pytest.raises(BackupError, match="已存在"):
        create_backup(sample_tree, bundle)


def test_refuses_bundle_inside_source(sample_tree):
    with pytest.raises(BackupError, match="源目录之内"):
        create_backup(sample_tree, sample_tree / "inner")


def test_refuses_restore_over_existing(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    create_backup(sample_tree, bundle)
    dest = tmp_path / "dest"
    dest.mkdir()
    keep = dest / "keep.txt"
    keep.write_text("不要动我", encoding="utf-8")
    with pytest.raises(BackupError, match="已存在"):
        restore_backup(bundle, dest)
    assert keep.read_text(encoding="utf-8") == "不要动我"


def test_failed_backup_cleans_up(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    with pytest.raises(BackupError, match="上限"):
        create_backup(sample_tree, bundle, options=BackupOptions(max_file_bytes=1))
    assert not bundle.exists()


def test_symlink_skipped(sample_tree, tmp_path):
    link = sample_tree / "link.png"
    try:
        link.symlink_to(sample_tree / "characters" / "my card.png")
    except OSError as exc:
        pytest.skip(f"当前环境无法创建符号链接: {exc}")
    bundle = tmp_path / "bundle"
    manifest = create_backup(sample_tree, bundle)
    assert "link.png" not in {e.rel_path for e in manifest.entries}
    assert any("link.png" in w for w in manifest.warnings)


def test_verify_detects_tamper_and_missing(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    create_backup(sample_tree, bundle)
    assert verify_bundle(bundle).ok

    (bundle / "files" / "notes.txt").write_text("被篡改", encoding="utf-8")
    report = verify_bundle(bundle)
    assert not report.ok
    assert "notes.txt" in report.mismatches

    (bundle / "files" / "broken.json").unlink()
    report2 = verify_bundle(bundle)
    assert "broken.json" in report2.missing


def test_verify_detects_extra_file(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    create_backup(sample_tree, bundle)
    (bundle / "files" / "extra.txt").write_text("x", encoding="utf-8")
    report = verify_bundle(bundle)
    assert "extra.txt" in report.extra_files
    assert not report.ok  # 二轮审查 P2：清单外文件 = 完整性失败


def test_stat_signature_detects_same_length_change(tmp_path):
    """二轮审查 P2：同长度内容变化也通过 mtime 签名检出。"""
    import time

    from continuity.backup.engine import _stat_signature

    p = tmp_path / "f.txt"
    p.write_text("aaaa", encoding="utf-8")
    sig1 = _stat_signature(p)
    time.sleep(0.05)
    p.write_text("bbbb", encoding="utf-8")  # 同长度、不同内容
    sig2 = _stat_signature(p)
    assert sig1 != sig2
    sig3 = _stat_signature(p)
    assert sig2 == sig3  # 未变化时签名稳定


def test_stat_signature_limitation_known(tmp_path):
    """第三轮审查 P2：同长度改写并恢复 mtime 时签名不变——属已知局限，
    文档已声明为"尽力检测"，不承诺检出所有并发修改。"""
    import os
    import time

    from continuity.backup.engine import _stat_signature

    p = tmp_path / "f.txt"
    p.write_text("aaaa", encoding="utf-8")
    sig1 = _stat_signature(p)
    st = p.stat()
    time.sleep(0.05)
    p.write_text("bbbb", encoding="utf-8")
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))  # 恢复修改时间
    sig2 = _stat_signature(p)
    assert sig1 == sig2  # 已知局限：此场景无法检出，属尽力检测


def test_restore_missing_entry_fails_without_partial(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    create_backup(sample_tree, bundle)
    (bundle / "files" / "notes.txt").unlink()
    dest = tmp_path / "dest"
    with pytest.raises(BackupError, match="缺少"):
        restore_backup(bundle, dest)
    assert not dest.exists()  # 失败不留部分恢复目录


def test_restore_enforces_single_file_limit(sample_tree, tmp_path):
    bundle = tmp_path / "bundle"
    create_backup(sample_tree, bundle)
    dest = tmp_path / "dest"
    with pytest.raises(BackupError, match="单文件上限"):
        restore_backup(bundle, dest, options=BackupOptions(max_file_bytes=1))
    assert not dest.exists()


def test_copy_and_hash_consistency(tmp_path):
    """P2-1：单次读取同步完成复制与哈希——清单哈希与备份内容必然一致。"""
    from continuity.backup.engine import _copy_and_hash
    from continuity.hashing import sha256_file

    src = tmp_path / "src.bin"
    data = bytes(range(256)) * 100
    src.write_bytes(data)
    dst = tmp_path / "dst.bin"
    copied, sha = _copy_and_hash(src, dst)
    assert copied == len(data)
    assert sha == sha256_file(src)
    assert dst.read_bytes() == data


@pytest.mark.parametrize("bad", ["../x", "/abs", "a/../../x", "C:/x", "a\\..\\b", "", "."])
def test_safe_join_rejects(tmp_path, bad):
    with pytest.raises(BackupError, match="不安全"):
        safe_join(tmp_path, bad)


def test_safe_join_ok(tmp_path):
    assert safe_join(tmp_path, "a/b.txt") == tmp_path / "a" / "b.txt"
