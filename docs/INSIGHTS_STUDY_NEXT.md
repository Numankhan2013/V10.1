# Insights: Topics to revisit

Insights now offers up to three study areas across all subjects and question banks.
Each source topic is identified by its subject, bank, and topic ID. Its evidence
is the latest active answer to each distinct question; undo events do not count.
A topic appears after at least three questions have been answered and at least
two are currently missed. Topics sort by missed share, then missed count. The
UI shows both counts rather than an unexplained weakness score.

**Practice missed** starts up to 20 of that topic's currently missed questions
through the existing Practice engine. If later answers correct those questions,
the recommendation disappears. The empty state distinguishes too little study
history from topics with no current retry signal. No new persisted analytics
model or Home action is added.

Implementation: `tools/insights_focus_core.js` and
`tools/apply_insights_focus_v1.py`. Checks: `tools/test_insights_focus_v1.py`
and the generated browser journey `tools/verify_insights_focus_browser.py`.

Build verification: Engineering `36149901357` and full generated browser/PWA/APK/Android emulator run `36149908749` passed at `d8e50e0`. Preview: https://221f15a2.nk-qbank.pages.dev. Production was not promoted; physical preview review is pending.
