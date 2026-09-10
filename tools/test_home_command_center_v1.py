#!/usr/bin/env python3
"""Regression contract for the approved Home + New Test interaction flows."""

from pathlib import Path

from apply_home_command_center_v1 import FLOW_MARKER, STYLE_ID, transform

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"


def main() -> None:
    fixture = '''<html><head></head><body><script>
function openStudyModuleBuilder(){ return 'custom'; }
/* NK_CUSTOM_STUDY_MODULES_V1_START */
function dashboard(){const recent=[1];return shell(`<main>${recent.length?`<b>${recent.map(x=>`${x}`).join('')}</b>`:`none`}<i id="legacy-home-tail">old</i></main>`,'dashboard');}
function testsPage(){return shell('<div id="legacy-tests">old tests</div>','tests');}
function examPage(){return '<div id="legacy-exam">old exam</div>';}
function startExamTicker(){return 'legacy ticker';}
function submitExam(auto=false){return auto;}
function untouchedQuestionEngine(){ return 'protected'; }
window.QB={openStudyModuleBuilder};
</script></body></html>'''
    updated = transform(fixture)
    if transform(updated) != updated:
        raise SystemExit("Home/Test transform is not idempotent")

    required = (
        FLOW_MARKER,
        STYLE_ID,
        "nk-home-approved-v1",
        "NK QBank",
        "Your Personal Study App",
        "TODAY'S FOCUS",
        "Continue Practice",
        "window.QB.nkContinueRecentPractice()",
        "nkLatestPracticeContext",
        "a.source==='exam'",
        "window.QB.nkOpenPracticeSubjects()",
        "nkOpenPracticeTopics",
        "nkStartTopicPractice",
        "Opening a topic starts Practice immediately.",
        "My Progress",
        "Today",
        "This Week",
        "This Month",
        "This Year",
        "window.QB.nkSetHomeProgressRange(this.value)",
        "nkHomeRangeStart",
        "nkHomeProgressStats",
        "New Test",
        "Timed Test",
        "Practice",
        "Question Source",
        "Full Question Bank",
        "Custom Module",
        "Wrong Questions",
        "Bookmarked Questions",
        "window.QB.openStudyModuleBuilder()",
        "Timer",
        "One minute per question when enabled.",
        "nkSetTestTimer(true)",
        "nkSetTestTimer(false)",
        "[10,20,50,100]",
        "nkStartConfiguredTest",
        "nkOpenTestSubjects",
        "nkOpenTestTopics",
        "nkStartConfiguredTopic",
        "s.questionIds.length*60",
        "s.questionIds.length*60000",
        "timerEnabled===false",
        "submitExam(true)",
        "60 sec / question",
        "@media(max-width:560px)",
        "@media(prefers-reduced-motion:reduce)",
    )
    missing = [item for item in required if item not in updated]
    if missing:
        raise SystemExit(f"Home/Test contract missing: {missing}")

    for legacy in (
        "legacy-home-tail",
        "legacy-tests",
        "legacy-exam",
        "window.QB.startAllSubjectPractice()",
        "window.QB.nav('analytics')",
        "Start Practice</span>",
    ):
        if legacy in updated:
            raise SystemExit(f"Obsolete Home/Test behavior survived: {legacy}")

    if updated.count(f'id="{STYLE_ID}"') != 1:
        raise SystemExit("Home/Test stylesheet owner duplicated")
    for fn in ("dashboard", "testsPage", "examPage", "startExamTicker", "submitExam"):
        if updated.count(f"function {fn}(") != 1:
            raise SystemExit(f"{fn} duplicated or missing")
    if "function untouchedQuestionEngine(){ return 'protected'; }" not in updated:
        raise SystemExit("Home/Test transform mutated protected question-engine code")
    for prohibited in ("Membership", "Premium Member", "Rank"):
        if prohibited in updated:
            raise SystemExit(f"Personal QBank UI introduced prohibited account/rank UI: {prohibited}")

    if HTML.exists():
        html = HTML.read_text(encoding="utf-8")
        if FLOW_MARKER in html:
            integration_missing = [item for item in required if item not in html]
            if integration_missing:
                raise SystemExit(f"Generated Home/Test integration missing: {integration_missing}")
            print("HOME_TEST_FLOW_INTEGRATION_OK")

    print("HOME_TEST_FLOW_CONTRACT_OK: recent-topic resume, subject→topic Practice, progress ranges, New Test sources, Custom Module, optional 60s/question timer")


if __name__ == "__main__":
    main()
