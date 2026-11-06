"""pytest 配置：把 src 加入导入路径，并提供合成样本目录夹具。

受限环境适配（重要，勿删）：
沙箱会强制执行 POSIX 目录权限——`os.mkdir(mode=0o700)` 创建的目录连创建
进程自身都无法访问（scandir/写入均被拒绝，实测复现）。pytest 的临时目录
（basetemp、pytest-of-<用户>、编号目录）默认全部使用 0o700，因此在最底层
把 mkdir 的 0o700 改写为 0o755，覆盖 pytest 的所有调用点；本机 Windows
上目录权限本就不由 POSIX mode 决定，此改写无副作用。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_original_mkdir = os.mkdir


def _sandbox_safe_mkdir(path, mode=0o777, *args, **kwargs):
    if mode == 0o700:
        mode = 0o755
    return _original_mkdir(path, mode, *args, **kwargs)


os.mkdir = _sandbox_safe_mkdir

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest  # noqa: E402

from helpers import make_card_png, make_st_sample_tree  # noqa: E402


@pytest.fixture
def sample_tree(tmp_path: Path) -> Path:
    """含 Unicode、空格文件名与常见损坏样本的合成目录树（不含真实用户数据）。"""
    root = tmp_path / "source"
    (root / "characters").mkdir(parents=True)
    (root / "chats").mkdir()
    (root / "characters" / "角色卡.json").write_text(
        json.dumps({"name": "测试角色", "first_mes": "你好。"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (root / "characters" / "my card.png").write_bytes(make_card_png())
    (root / "chats" / "chat.jsonl").write_text(
        "".join(
            json.dumps(
                {"name": "测试角色", "is_user": i % 2 == 0, "mes": f"消息{i}"},
                ensure_ascii=False,
            )
            + "\n"
            for i in range(3)
        ),
        encoding="utf-8",
    )
    (root / "notes.txt").write_text("一些纯文本说明。", encoding="utf-8")
    (root / "broken.json").write_text('{\n  "name": "坏样本",\n}\n', encoding="utf-8")
    return root


@pytest.fixture
def st_sample_tree(tmp_path: Path) -> Path:
    """合成 SillyTavern 数据目录（含 JSON 与 PNG 两张角色卡、聊天、世界书、附件）。"""
    return make_st_sample_tree(tmp_path / "stdata", with_json_card=True)
