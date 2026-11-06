"""CLI 集成测试（直接调用 main，不经过子进程）。"""

from continuity.cli import main


def test_version(capsys):
    assert main(["version"]) == 0
    out = capsys.readouterr().out
    assert "continuity-studio" in out


def test_scan_cli(sample_tree, capsys):
    assert main(["scan", str(sample_tree)]) == 0
    out = capsys.readouterr().out
    assert "character_card_png" in out
    assert "疑似损坏" in out


def test_backup_restore_cli(sample_tree, tmp_path, capsys):
    bundle = tmp_path / "bundle"
    assert main(["backup", str(sample_tree), str(bundle)]) == 0
    assert "备份完成" in capsys.readouterr().out

    dest = tmp_path / "dest"
    assert main(["restore", str(bundle), str(dest)]) == 0
    assert "恢复完成" in capsys.readouterr().out
    assert (dest / "notes.txt").is_file()


def test_verify_cli(sample_tree, tmp_path, capsys):
    bundle = tmp_path / "bundle"
    main(["backup", str(sample_tree), str(bundle)])
    capsys.readouterr()
    assert main(["verify", str(bundle)]) == 0
    assert "通过" in capsys.readouterr().out


def test_restore_over_existing_fails(sample_tree, tmp_path, capsys):
    bundle = tmp_path / "bundle"
    main(["backup", str(sample_tree), str(bundle)])
    capsys.readouterr()
    dest = tmp_path / "dest"
    dest.mkdir()
    assert main(["restore", str(bundle), str(dest)]) == 2
    assert "已存在" in capsys.readouterr().err


def test_repair_cli(sample_tree, tmp_path, capsys):
    out = tmp_path / "fixed"
    assert main(["repair", str(sample_tree), str(out)]) == 0
    captured = capsys.readouterr().out
    assert "R0-001" in captured
    assert (out / "repair-report.json").is_file()


def test_migrate_cli(st_sample_tree, tmp_path, capsys):
    out = tmp_path / "migrated"
    assert main(["migrate", str(st_sample_tree), str(out)]) == 0
    captured = capsys.readouterr().out
    assert "迁移完成" in captured
    assert "匹配率: 100.0%" in captured
    assert (out / "migration-report.json").is_file()


def test_migrate_cli_incomplete_exit_code(st_sample_tree, tmp_path, capsys, monkeypatch):
    """第三轮审查 P2：迁移不完整必须明确输出且退出码非零。"""
    import continuity.scanners.scan as scan_mod

    real = scan_mod.sha256_file

    def fake(path):
        if "README.md" in str(path):
            raise OSError("模拟拒绝访问")
        return real(path)

    monkeypatch.setattr(scan_mod, "sha256_file", fake)
    out = tmp_path / "migrated"
    assert main(["migrate", str(st_sample_tree), str(out)]) == 1
    assert "迁移不完整" in capsys.readouterr().out
