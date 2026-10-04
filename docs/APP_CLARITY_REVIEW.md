# Navigation clarity review — 2026-10-01

The user’s phone screenshots and fresh390px captures of the current preview showed content displaced by duplicate labels, descriptive paragraphs and large gaps. A compact presentation pass retains actions, context and data.

1. **Revision:** removed the repeated REVISION kicker, subtitle, obvious queue definitions and repeated session-size footnotes. Count and practice size remain visible. Scope and focus share a row; empty queues show their zero count. All four populated queues fit above phone navigation at320/390px.
2. **Insights:** removed promotional kickers, subtitle and summary, repeated chart instructions and per-card calculation prose. The year heatmap is titled Activity and begins within280px of the viewport top. Date/scope/period controls remain. Calculation details are available in About these metrics; current FSRS forecast and small topic samples remain labelled.
3. **Tests:** removed exam-practice/history kickers, introductory paragraph and builder instruction. Build, quick tests and completed history remain.
4. **Home:** removed the greeting slogan and brand subtitle, obvious focus instructions, duplicate section kickers and repeated revision status copy. Retained the accepted liquid streak, greeting, counts and session progress.
5. **More:** removed the irrelevant subject kicker and obvious subtitle. Account merge/sign-in information and sync status remain.
6. **FSRS:** removed the long scheduling introduction. Counts, subject queues, forecast and daily-limit rollover information remain.
7. **Review settings:** replaced the promotional title with Review settings, removed repeated section headers/taglines and collapsed scheduling information. Field definitions, ranges, retention warning and save/cancel states remain.
8. **Study library:** removed instructions that restate the next navigation action. Subject counts and bank selection remain.
9. **Question finder:** removed the obvious page introduction. Search and filter labels remain.
10. **Notes:** removed the subtitle repeating the page purpose. Empty-state instructions still explain where to create a note.
11. **CBT/module builders:** removed duplicate step kickers and instructions to select the visibly labelled controls. Stepper, selections, count, timer budget and validation remain.

Owner: `tools/apply_app_clarity_v1.py`, installed after Insights and before final syntax/package contracts. Browser evidence is generated as `build/ui-checks/clarity-*.png`, alongside the existing study-flow suites. Screenshot review establishes visible density and geometry; it does not establish full accessibility compliance or physical Android acceptance. Native interaction CI remains mandatory before release.
