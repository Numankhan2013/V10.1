from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"

s = HTML.read_text(encoding="utf-8")

# This contract is deliberately conservative: it protects the existing QBank
# experience without prescribing a future UI architecture.
required = [
    "nk-home-v4",
    "nk-home-v4-style",
    "NK_HOME_V5_FIXES",
    "nk-home-streak-header-v1",
    "nk-home-actions-v1",
    "Continue Practice",
    "Practice 20 Random Questions",
    "qbank-question-ui-v2",
    "qbank-practice-analysis-v1",
    "qbank-ui-polish-v1",
    "qbank-ui-polish-v2",
    "qbank-home-insights-polish-v1",
    "qbank-option-feedback-polish-v1",
    "qbank-practice-cleanup-v1",
    "qbank-option-hole-cleanup-v1",
    "NK_SOURCE_VISUALS_V11",
    "nk-session-review",
    "nk-cbt-review-footer-v1",
    "review-fixed-actions",
    "nk-review-solution-grid-style",
    'id="cr-grid"',
    "window.QB.openQuestionNavigator()",
    "openQuestionNavigator",
    "closeQuestionNavigator();",
    "sessionShell",
    "qb-nav-submit",
]

for marker in required:
    assert marker in s, f"Protected marker missing: {marker}"

for forbidden in [
    'id="v102-streak-layer-script"',
    'id="v102-streak-layer"',
    "home_polish_v3.js",
]:
    assert forbidden not in s, f"Legacy regression marker present: {forbidden}"

# Question Navigator is an intentional component. Do not confuse it with
# application navigation when doing future cleanup.
assert len(re.findall(r'class=[\"\'][^\"\']*navigator[^\"\']*[\"\']', s)) >= 1

# Catch accidental duplicate application-level bottom navigation containers.
# A Question Navigator is allowed and is separately protected above.
bottom_nav_containers = re.findall(r'<[^>]+class=[\"\'][^\"\']*\\bbottom-nav\\b[^\"\']*[\"\'][^>]*>', s)
assert len(bottom_nav_containers) <= 1, (
    f"Expected at most one persistent bottom-nav container; found {len(bottom_nav_containers)}"
)

# Every inline script must remain syntactically valid. This is cheap enough to
# run on every safe-polish change and catches the class of boot failures we have
# previously encountered.
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

print(f"SAFE_POLISH_BASELINE_OK scripts={checked} bottom_nav={len(bottom_nav_containers)}")
