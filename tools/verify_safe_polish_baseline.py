from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"

s = HTML.read_text(encoding="utf-8")

# Source-level contract. Keep this deliberately tied to stable source markers,
# not build-time generated JS names, because CI transforms index.html.
required = [
    ".bottom-nav",
    ".navigator",
    ".question-shell",
    ".question-card",
    ".question-text",
    ".option-list",
    ".feedback",
    ".q-footer",
    "qb-nav-submit",
]

for marker in required:
    assert marker in s, f"Protected source marker missing: {marker}"

# Known legacy layers that must never silently return.
for forbidden in [
    'id="v102-streak-layer-script"',
    'id="v102-streak-layer"',
    "home_polish_v3.js",
]:
    assert forbidden not in s, f"Legacy regression marker present: {forbidden}"

# Question Navigator is intentional and must survive future navigation cleanup.
assert re.search(r'class=[\"\'][^\"\']*navigator[^\"\']*[\"\']', s)

# Do not allow two persistent application-level bottom navigation containers.
bottom_nav_containers = re.findall(
    r'<[^>]+class=[\"\'][^\"\']*\bbottom-nav\b[^\"\']*[\"\'][^>]*>', s
)
assert len(bottom_nav_containers) <= 1, (
    f"Expected at most one persistent bottom-nav container; found {len(bottom_nav_containers)}"
)

# Every inline script must remain syntactically valid. This catches WebView
# boot failures before a device is ever asked to install a build.
scripts = re.findall(r'<script(?:[^>]*)>(.*?)</script>', s, re.S | re.I)
with tempfile.TemporaryDirectory() as td:
    checked = 0
    for i, src in enumerate(scripts):
        if not src.strip():
            continue
        f = Path(td) / f"inline_{i}.js"
        f.write_text(src, encoding="utf-8")
        subprocess.run(["node", "--check", str(f)], check=True)
        checked += 1

print(f"SAFE_POLISH_SOURCE_OK scripts={checked} bottom_nav={len(bottom_nav_containers)}")
