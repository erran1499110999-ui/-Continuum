"""清单 schema 的读写与校验测试。"""

import json

import pytest

from continuity.backup.manifest import MANIFEST_FILENAME, read_manifest, write_manifest
from continuity.models import BundleManifest, ManifestEntry, ManifestError


def _sample() -> BundleManifest:
    return BundleManifest(
        bundle_id="b-1",
        bundle_version="1.0",
        created_at="2026-11-06T00:00:00+00:00",
        entries=[ManifestEntry(rel_path="a.txt", size=3, sha256="0" * 64, kind="text")],
    )


def test_roundtrip(tmp_path):
    write_manifest(tmp_path, _sample())
    m2 = read_manifest(tmp_path)
    assert m2.bundle_id == "b-1"
    assert m2.entries[0].rel_path == "a.txt"
    assert m2.entries[0].sha256 == "0" * 64
    assert m2.entries[0].size == 3


def test_written_json_is_valid(tmp_path):
    write_manifest(tmp_path, _sample())
    raw = json.loads((tmp_path / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert raw["bundle_id"] == "b-1"
    assert raw["entries"][0]["rel_path"] == "a.txt"


def test_reject_unknown_schema(tmp_path):
    m = _sample()
    m.schema_version = "9.9"
    write_manifest(tmp_path, m)
    with pytest.raises(ManifestError, match="schema"):
        read_manifest(tmp_path)


def test_reject_bad_sha256(tmp_path):
    m = _sample()
    m.entries[0].sha256 = "xyz"
    write_manifest(tmp_path, m)
    with pytest.raises(ManifestError, match="sha256"):
        read_manifest(tmp_path)


def test_reject_duplicate_rel_path(tmp_path):
    m = _sample()
    m.entries.append(ManifestEntry(rel_path="a.txt", size=1, sha256="1" * 64))
    write_manifest(tmp_path, m)
    with pytest.raises(ManifestError, match="重复"):
        read_manifest(tmp_path)


def test_reject_missing_manifest(tmp_path):
    with pytest.raises(ManifestError, match="manifest.json"):
        read_manifest(tmp_path)


def test_reject_invalid_json(tmp_path):
    (tmp_path / MANIFEST_FILENAME).write_text("{ 不是 JSON", encoding="utf-8")
    with pytest.raises(ManifestError, match="不是合法 JSON"):
        read_manifest(tmp_path)


@pytest.mark.parametrize("bad", ["a//b", "a/./b", "/a", "a/", "a\\b", " a", "C:/x", "a/../b"])
def test_reject_non_normalized_rel_path(tmp_path, bad):
    m = _sample()
    m.entries[0].rel_path = bad
    write_manifest(tmp_path, m)
    with pytest.raises(ManifestError, match="相对路径"):
        read_manifest(tmp_path)
