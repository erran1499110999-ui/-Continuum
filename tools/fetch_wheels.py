"""开发辅助：从 PyPI 下载纯 Python wheel 并解压到 .deps2（受限环境替代 pip）。

仅用于本机开发环境准备，不属于产品代码。用法：
  python .tmp/fetch_wheels.py
"""

from __future__ import annotations

import json
import urllib.request
import zipfile
from pathlib import Path

PKGS = ["pytest", "colorama", "iniconfig", "packaging", "pluggy", "pygments"]
ROOT = Path(__file__).resolve().parent.parent
WHEELS = ROOT / ".wheels"
DEPS = ROOT / ".deps2"


def fetch(url: str, retries: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "continuity-studio-dev"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as exc:  # 网络抖动：重试
            last = exc
            print(f"  retry {attempt + 1}/{retries}: {exc}")
    raise last


def main() -> int:
    WHEELS.mkdir(exist_ok=True)
    DEPS.mkdir(exist_ok=True)
    for pkg in PKGS:
        try:
            info = json.loads(fetch(f"https://pypi.org/pypi/{pkg}/json").decode())
            version = info["info"]["version"]
            wheels = [
                u
                for u in info["urls"]
                if u["filename"].endswith(".whl")
                and ("py3-none-any" in u["filename"] or "py2.py3-none-any" in u["filename"])
            ]
            if not wheels:
                print(f"skip {pkg}: no pure wheel")
                continue
            name = wheels[0]["filename"]
            data = fetch(wheels[0]["url"])
            (WHEELS / name).write_bytes(data)
            print(f"downloaded {pkg} {version} -> {name} ({len(data)} bytes)")
        except Exception as exc:
            print(f"FAILED {pkg}: {exc}")
    print("== extract ==")
    for w in sorted(WHEELS.glob("*.whl")):
        try:
            with zipfile.ZipFile(w) as z:
                z.extractall(DEPS)
            print(f"extracted: {w.name}")
        except Exception as exc:
            print(f"EXTRACT FAILED {w.name}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
