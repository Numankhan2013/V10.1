#!/usr/bin/env python3
"""Create a Cloudflare Pages-ready PWA from the generated Android assets."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
DEFAULT_OUT = ROOT / "build/web"
PAGES_FILE_LIMIT = 25 * 1024 * 1024


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--version", default="dev")
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    skipped = []
    for source in ASSETS.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(ASSETS)
        if source.stat().st_size > PAGES_FILE_LIMIT:
            skipped.append(str(relative))
            continue
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    html = out / "index.html"
    html.write_text(html.read_text(encoding="utf-8").replace('src="assets/physiology_image_pages.js"', 'src="physiology_image_pages.js"').replace('href="assets/Biochemistry_QBank_Source.pdf"', 'href="Biochemistry_QBank_Source.pdf"'), encoding="utf-8")
    sw = out / "sw.js"
    sw.write_text(sw.read_text(encoding="utf-8").replace("const BUILD_VERSION='dev';", f"const BUILD_VERSION={args.version!r};", 1), encoding="utf-8")
    (out / "_headers").write_text(
        "/sw.js\n  Cache-Control: no-cache\n/index.html\n  Cache-Control: no-cache\n/qbank-config.js\n  Cache-Control: no-cache\n/source_visuals/*\n  Cache-Control: public, max-age=31536000, immutable\n/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n",
        encoding="utf-8",
    )
    (out / "_redirects").write_text("/* /index.html 200\n", encoding="utf-8")
    if "Anatomy_QBank_Source.pdf" not in skipped:
        raise SystemExit("Expected oversized Anatomy PDF to be excluded from Pages output")
    print(f"WEB_DIST_OK files={sum(1 for p in out.rglob('*') if p.is_file())} skipped_oversize={','.join(skipped)}")


if __name__ == "__main__":
    main()
