"""迁移引擎测试：全部角色卡迁移、源只读、sidecar、匹配率与安全边界。"""

import json

import pytest

from continuity.migration import MigrationError, migrate_sillytavern

from helpers import make_st_sample_tree

PRIMARY = "cards/角色卡.json"  # JSON 卡优先被选为主卡
SECONDARY = "cards/角色卡.png"


def _snapshot(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }


def _status(report, field):
    for item in report.items:
        if item["field"] == field:
            return item["status"]
    raise AssertionError(f"未找到校验项: {field}")


def test_full_roundtrip(st_sample_tree, tmp_path):
    before = _snapshot(st_sample_tree)
    out = tmp_path / "migrated"
    report = migrate_sillytavern(st_sample_tree, out)
    # 源目录未被修改
    assert _snapshot(st_sample_tree) == before

    # 主卡（JSON）逐项验证
    assert _status(report, f"角色卡.{PRIMARY}.name") == "ok"
    assert _status(report, f"角色卡.{PRIMARY}.personality") == "ok"
    assert _status(report, f"角色卡.{PRIMARY}.first_mes") == "ok"
    assert _status(report, f"角色卡.{PRIMARY}.alternate_greetings") == "ok"
    assert _status(report, f"角色卡.{PRIMARY}.tags") == "ok"
    # 第二张卡（PNG）同样逐项验证，绝不静默丢弃（审查 P1-1）
    assert _status(report, f"角色卡.{SECONDARY}.name") == "ok"
    assert _status(report, f"角色卡.{SECONDARY}.first_mes") == "ok"
    assert _status(report, "聊天.chats/chat1.jsonl.消息") == "ok"
    assert _status(report, "世界书.worlds/world1.json.条目") == "ok"
    assert _status(report, "附件.assets/portrait.png") == "ok"
    assert _status(report, "附件.README.md") == "ok"

    # 匹配率语义（审查 P1-3）
    assert report.completeness["score"] == 1.0
    assert report.completeness["score_label"] == "已检查支持项匹配率"
    assert report.completeness["source_files_total"] == 6
    assert report.completeness["migrated_cards"] == 2
    assert report.completeness["migrated_chats"] == 1
    assert report.completeness["migrated_worldinfo"] == 1
    assert report.completeness["migrated_assets"] == 2
    assert report.completeness["denominator_explanation"]
    assert _status(report, f"角色卡.{PRIMARY}.system_prompt") == "excluded"
    assert f"角色卡.{PRIMARY}.system_prompt" in report.completeness["excluded"]

    # 两张卡的输出文件都存在
    assert (out / "character-card.json").is_file()
    assert (out / "cards" / "00_角色卡.json").is_file()
    assert (out / "cards" / "01_角色卡.from_png.json").is_file()
    assert (out / "chats" / "chats" / "chat1.jsonl").is_file()
    assert (out / "worldinfo" / "worlds" / "world1.json").is_file()
    assert (out / "assets" / "assets" / "portrait.png").is_file()
    assert (out / "migration-report.json").is_file()


def test_unknown_field_preserved_in_card_and_sidecar(st_sample_tree, tmp_path):
    out = tmp_path / "migrated"
    report = migrate_sillytavern(st_sample_tree, out)
    assert _status(report, f"角色卡.{PRIMARY}.unknown_custom_field") == "unsupported"
    sidecar = json.loads((out / "unsupported-fields.json").read_text(encoding="utf-8"))
    assert "unknown_custom_field" in sidecar["unknown_fields"][PRIMARY]
    assert "unknown_custom_field" in sidecar["unknown_fields"][SECONDARY]
    card = json.loads((out / "character-card.json").read_text(encoding="utf-8"))
    assert card["data"]["unknown_custom_field"] == {"x": 1}


def test_report_contains_no_absolute_paths(st_sample_tree, tmp_path):
    out = tmp_path / "migrated"
    report = migrate_sillytavern(st_sample_tree, out)
    raw = (out / "migration-report.json").read_text(encoding="utf-8")
    # 隐私脱敏（审查 P1-4）：报告不出现绝对路径
    assert str(st_sample_tree.resolve()) not in raw
    assert str((tmp_path / "migrated").resolve()) not in raw
    assert report.source_dir_name == "stdata"
    assert report.output_dir_name == "migrated"


def test_png_only_migration(tmp_path):
    root = make_st_sample_tree(tmp_path / "pngonly", with_json_card=False)
    out = tmp_path / "migrated"
    report = migrate_sillytavern(root, out)
    assert _status(report, f"角色卡.{SECONDARY}.name") == "ok"
    assert report.completeness["score"] == 1.0
    assert report.completeness["migrated_cards"] == 1


def test_chat_bad_line_needs_review(st_sample_tree, tmp_path):
    chat = st_sample_tree / "chats" / "chat1.jsonl"
    chat.write_text(chat.read_text(encoding="utf-8") + "这不是JSON\n", encoding="utf-8")
    out = tmp_path / "migrated"
    report = migrate_sillytavern(st_sample_tree, out)
    assert _status(report, "聊天.chats/chat1.jsonl.消息") == "needs_review"
    assert report.completeness["score"] < 1.0
    assert report.needs_review
    assert any("不是合法 JSON" in w for w in report.warnings)
    # 字节级保留：原始 JSONL 完整字节副本 + 坏行字节索引（审查二轮 P2）
    original = out / "chats" / "chats" / "chat1.jsonl.original"
    assert original.is_file()
    assert original.read_bytes() == chat.read_bytes()  # 字节完全一致
    bad = out / "chats" / "chats" / "chat1.jsonl.bad-lines.txt"
    assert bad.is_file()
    content = bad.read_bytes()
    assert "这不是JSON".encode("utf-8") in content
    # 索引头注明字节级还原请用原始副本（第三轮审查 P2）
    assert ".original".encode("utf-8") in content


def test_valid_card_plus_corrupt_png_flagged(st_sample_tree, tmp_path):
    """二轮审查 P1：有效卡存在时，损坏 PNG 也必须进入待处理清单与报告。"""
    from helpers import make_png

    data = bytearray(make_png())
    data[16] ^= 0xFF  # CRC 损坏
    bad_rel = st_sample_tree / "assets" / "bad.png"
    bad_rel.write_bytes(bytes(data))
    out = tmp_path / "migrated"
    report = migrate_sillytavern(st_sample_tree, out)
    assert report.completeness["damaged_files"] == ["assets/bad.png"]
    assert report.completeness["coverage_complete"] is True  # 已按字节保留，覆盖未缺
    assert any("损坏" in n for n in report.needs_review)
    # 损坏 PNG 按字节原样保留
    assert (out / "assets" / "assets" / "bad.png").read_bytes() == bad_rel.read_bytes()
    # 常规项仍全部匹配，且损坏文件不计入附件计数
    assert report.completeness["score"] == 1.0
    assert report.completeness["migrated_assets"] == 2


def test_migration_unreadable_file_marked_incomplete(st_sample_tree, tmp_path, monkeypatch):
    """二轮审查 P1：无法读取的文件必须标记迁移不完整并进入待处理清单。"""
    import continuity.scanners.scan as scan_mod

    real = scan_mod.sha256_file

    def fake(path):
        if "README.md" in str(path):
            raise OSError("模拟拒绝访问")
        return real(path)

    monkeypatch.setattr(scan_mod, "sha256_file", fake)
    out = tmp_path / "migrated"
    report = migrate_sillytavern(st_sample_tree, out)
    assert report.completeness["coverage_complete"] is False
    assert "README.md" in report.completeness["unprocessed_files"]
    assert any("无法读取" in n for n in report.needs_review)
    # 不可读文件未被复制
    assert not (out / "assets" / "README.md").exists()


def test_missing_card_raises(tmp_path):
    root = tmp_path / "empty"
    root.mkdir()
    (root / "x.txt").write_text("hi", encoding="utf-8")
    with pytest.raises(MigrationError, match="未找到角色卡"):
        migrate_sillytavern(root, tmp_path / "out")


def test_refuses_existing_output(st_sample_tree, tmp_path):
    out = tmp_path / "migrated"
    migrate_sillytavern(st_sample_tree, out)
    with pytest.raises(MigrationError, match="已存在"):
        migrate_sillytavern(st_sample_tree, out)


def test_refuses_output_inside_source(st_sample_tree):
    with pytest.raises(MigrationError, match="源目录之内"):
        migrate_sillytavern(st_sample_tree, st_sample_tree / "inner")


def test_corrupt_card_png_fails_loudly(tmp_path):
    """只破坏 IDAT CRC 的卡也必须被识别为损坏（端到端：扫描分类 + 迁移报错）。"""
    from helpers import corrupt_idat

    root = make_st_sample_tree(tmp_path / "corrupt", with_json_card=False)
    card = root / "cards" / "角色卡.png"
    card.write_bytes(corrupt_idat(card.read_bytes()))
    with pytest.raises(MigrationError, match="损坏|CRC"):
        migrate_sillytavern(root, tmp_path / "out")
    assert not (tmp_path / "out").exists()  # 失败清理输出目录


def test_migration_file_limit_fails_cleanly(st_sample_tree, tmp_path):
    from continuity.limits import ResourceLimits

    out = tmp_path / "migrated"
    with pytest.raises(MigrationError, match="上限"):
        migrate_sillytavern(st_sample_tree, out, limits=ResourceLimits(max_file_bytes=1))
    assert not out.exists()  # 失败清理输出目录，不留貌似完整的结果


def test_migration_damaged_file_budget(tmp_path, monkeypatch):
    """第三轮审查 P2：损坏 PNG 与普通附件共用累计预算（受控测试：扫描放行、迁移内部拦截）。"""
    import continuity.migration.engine as mig_mod

    from helpers import corrupt_idat, make_png

    from continuity.limits import DEFAULT_LIMITS, ResourceLimits

    real = mig_mod.scan_directory

    def lax_scan(root, limits):
        return real(root, DEFAULT_LIMITS)  # 扫描阶段不设限，专测迁移内部预算

    monkeypatch.setattr(mig_mod, "scan_directory", lax_scan)

    root = make_st_sample_tree(tmp_path / "st", with_json_card=False)
    bad = root / "assets" / "broken.png"
    bad.write_bytes(corrupt_idat(make_png()))
    # 附件（portrait+README≈90B）可通过，加损坏文件后累计≈160B 超过 120 上限
    with pytest.raises(MigrationError, match="累计大小超过上限"):
        migrate_sillytavern(root, tmp_path / "out", limits=ResourceLimits(max_total_bytes=120))
    assert not (tmp_path / "out").exists()


def test_migration_chat_line_limit_fails_cleanly(st_sample_tree, tmp_path):
    from continuity.limits import ResourceLimits

    out = tmp_path / "migrated"
    with pytest.raises(MigrationError, match="行数上限"):
        migrate_sillytavern(st_sample_tree, out, limits=ResourceLimits(max_chat_lines=2))
    assert not out.exists()
