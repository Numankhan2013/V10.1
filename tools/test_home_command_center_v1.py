#!/usr/bin/env python3
"""Contract checks for the approved Home-only mobile dashboard."""

from pathlib import Path

from apply_home_command_center_v1 import STYLE_ID, transform


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"


def main() -> None:
    # The real pre-transform dashboard contains nested template literals inside
    # `${...}` expressions. Keep that shape here so the replacement cannot pass
    # unit tests while leaving a legacy Home tail in the generated application.
    fixture = '''<html><head></head><body><style id="nk-custom-study-modules-v1"></style><script>
function dashboard() {
  const recent=[{name:'one'}];
  return shell(`<main>${recent.length?`<section>${recent.map(x=>`<b>${x.name}</b>`).join('')}</section>`:`<section>none</section>`}<div id="legacy-home-tail">legacy tail</div></main>`, 'dashboard');
}
function untouchedQuestionEngine(){ return 'protected'; }
</script></body></html>'''
    updated = transform(fixture)
    if transform(updated) != updated:
        raise SystemExit("Approved Home transform is not idempotent")

    required = (
        STYLE_ID,
        "nk-home-approved-v1",
        "nk-home-command-center",
        "nk-focus-secondary",
        "nk-focus-primary",
        "Recommended now",
        "CONTINUE LEARNING",
        "Continue Practice",
        "Practice 20 Random Questions",
        "Quick practice",
        "Timed Test",
        "Timed CBT · exam mode",
        "Custom Test",
        "Review",
        "Today's goal",
        "Recent Activity",
        "window.QB.continuePractice()",
        "window.QB.startAllSubjectPractice()",
        "window.QB.openTestBuilder()",
        "window.QB.openStudyModuleBuilder()",
        "window.QB.startLibrary('review')",
        "@media(max-width:560px)",
        "@media(prefers-reduced-motion:reduce)",
        "body:has(.nk-home-approved-v1) .topbar",
    )
    missing = [item for item in required if item not in updated]
    if missing:
        raise SystemExit(f"Approved Home contract missing: {missing}")
    if updated.count(f'id="{STYLE_ID}"') != 1:
        raise SystemExit("Approved Home style owner duplicated")
    if updated.count("function dashboard()") != 1:
        raise SystemExit("Approved Home dashboard owner duplicated or missing")
    if "legacy-home-tail" in updated:
        raise SystemExit("Legacy Home tail survived nested-template replacement")
    if "function untouchedQuestionEngine(){ return 'protected'; }" not in updated:
        raise SystemExit("Home transform mutated a protected non-Home function")
    for prohibited in ("Membership", "Rank", "Premium Member"):
        if prohibited in updated:
            raise SystemExit(f"Personal QBank Home introduced prohibited account/rank UI: {prohibited}")

    if HTML.exists():
        html = HTML.read_text(encoding="utf-8")
        if f'id="{STYLE_ID}"' in html:
            for item in required:
                if item not in html:
                    raise SystemExit(f"Generated approved Home missing: {item}")
            print("HOME_APPROVED_REFERENCE_INTEGRATION_OK")

    print("HOME_APPROVED_REFERENCE_CONTRACT_OK: full Home hierarchy, nested-template replacement, actions, personal-app scope, responsiveness and engine isolation")


if __name__ == "__main__":
    main()
