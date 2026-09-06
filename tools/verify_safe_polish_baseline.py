from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"

s = HTML.read_text(encoding="utf-8")

# Source-level contract: these are the existing systems that every future
# polish/feature branch must preserve. Generated build-time markers are tested
# by the APK build workflow, not by this source gate.
required = [
    ".bottom-nav",
    ".navigator",
    ".question-shell",
    ".question-card",
    ".question-text",
    ".option-list",
    ".feedback",
    ".q-footer",
    "sessionShell",
    "openQuestionNavigator",
    "closeQuestionNavigator();",
    "window.QB.openQuestionNavigator()",
    "qb-nav-submit",
    "localStorage",
    "Bookmark",
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

# The Question Navigator is a legitimate question-level component. It must not
# be removed as part of application-navigation cleanup.
assert re.search(r'class=[\"\'][^\"\']*navigator[^\"\']*[\"\']', s)

# There must be no duplicate persistent application navigation containers.
# Keep this intentionally structural rather than tying the test to a specific
# future navigation label set.
bottom_nav_containers = re.findall(
    r'<[^>]+class=[\"\'][^\"\']*\bbottom-nav\b[^\"\']*[\"\'][^>]*>', s
)
assert len(bottom_nav_containers) <= 1, (
    f"Expected at most one persistent bottom-nav container; found {len(bottom_nav_containers)}"
)

# Every inline script must remain syntactically valid. This catches boot
# failures before a device is ever asked to install a build.
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
