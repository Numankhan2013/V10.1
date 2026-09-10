#!/usr/bin/env python3
"""Contract and behavior checks for the bounded Home command center."""

from pathlib import Path
import re
import subprocess

from apply_home_command_center_v1 import OLD_FOCUS_LINE, OLD_PANEL, RECOMMENDATION_HELPER, STYLE_ID, transform


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"


def main() -> None:
    helper = re.search(r"function nkHomeRecommendation\(.*?\n  \}", RECOMMENDATION_HELPER, re.S)
    if not helper:
        raise SystemExit("Recommendation helper could not be isolated")
    node = helper.group(0) + "\n" + r'''
const assert=require('node:assert/strict');
assert.equal(nkHomeRecommendation({id:'saved'},9),'module');
assert.equal(nkHomeRecommendation(null,9),'review');
assert.equal(nkHomeRecommendation(null,0),'practice');
console.log('HOME_COMMAND_CENTER_PRIORITY_OK');
'''
    subprocess.run(["node", "-"], input=node, text=True, check=True)

    fixture = f'''<html><head></head><body><style id="nk-custom-study-modules-v1"></style><script>
  function dashboard() {{
{OLD_FOCUS_LINE}
    return `{OLD_PANEL}`;
  }}
</script></body></html>'''
    updated = transform(fixture)
    if transform(updated) != updated:
        raise SystemExit("Home transform is not idempotent")
    required = (
        STYLE_ID,
        "homeRecommendation==='module'",
        "homeRecommendation==='review'",
        "window.QB.startStudyModule",
        "window.QB.startLibrary('review')",
        "window.QB.continuePractice()",
        "window.QB.startAllSubjectPractice()",
        "Practice 20 Random Questions",
        "window.QB.openTestBuilder()",
        'aria-label="Other study actions"',
        "@media(max-width:480px)",
        "@media(prefers-reduced-motion:reduce)",
    )
    missing = [item for item in required if item not in updated]
    if missing:
        raise SystemExit(f"Home command-center contract missing: {missing}")
    if updated.count(f'id="{STYLE_ID}"') != 1 or updated.count("function nkHomeRecommendation(") != 1:
        raise SystemExit("Home command center duplicated its owners")

    if HTML.exists():
        html = HTML.read_text(encoding="utf-8")
        if f'id="{STYLE_ID}"' in html:
            for item in required:
                if item not in html:
                    raise SystemExit(f"Generated Home command center missing: {item}")
            print("HOME_COMMAND_CENTER_INTEGRATION_OK")
    print("HOME_COMMAND_CENTER_CONTRACT_OK: priority, actions, accessibility, responsive and reduced-motion rules")


if __name__ == "__main__":
    main()
