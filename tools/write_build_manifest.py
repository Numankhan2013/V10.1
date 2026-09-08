#!/usr/bin/env python3
"""Create a reproducibility manifest for the exact APK and generated web app."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> dict[str, object]:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": h.hexdigest()}


apk_files = sorted((ROOT / "app/build/outputs/apk/debug").glob("*.apk"))
if len(apk_files) != 1:
    raise SystemExit(f"Expected exactly one debug APK, found {len(apk_files)}")

tracked = [
    ROOT / "app/src/main/assets/index.html",
    ROOT / "app/src/main/AndroidManifest.xml",
    ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java",
    ROOT / ".github/workflows/build-apk.yml",
    apk_files[0],
]

manifest = {
    "schema": 1,
    "product": "NK QBank",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "git_commit": os.environ.get("GITHUB_SHA") or subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip(),
    "git_ref": os.environ.get("GITHUB_REF_NAME", "local"),
    "files": [digest(path) for path in tracked],
}

output = ROOT / "app/build/outputs/apk/debug/NK-QBank-build-manifest.json"
output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(output)
