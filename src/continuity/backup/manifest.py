"""备份包清单的读写。"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from ..models import BundleManifest, ManifestError

MANIFEST_FILENAME = "manifest.json"


def write_manifest(bundle_dir: Path, manifest: BundleManifest) -> Path:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    path = bundle_dir / MANIFEST_FILENAME
    path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def read_manifest(bundle_dir: Path) -> BundleManifest:
    path = bundle_dir / MANIFEST_FILENAME
    if not path.is_file():
        raise ManifestError(f"备份包中缺少 {MANIFEST_FILENAME}: {bundle_dir}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"{MANIFEST_FILENAME} 不是合法 JSON: {exc}") from exc
    try:
        return BundleManifest.model_validate(raw)
    except ValidationError as exc:
        errors = exc.errors()
        first = errors[0] if errors else {}
        loc = ".".join(str(x) for x in first.get("loc", ()))
        raise ManifestError(
            f"清单校验失败（{loc or 'manifest'}）: {first.get('msg', '')}"
        ) from exc
