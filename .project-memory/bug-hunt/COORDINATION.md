# Coordination — six reviewers, one branch

Base: `main` at `25fa6b66`, branch `bug-hunt/2026-10-19`, checkout
`/root/bug-hunt/base` (sparse: app source, modules, tools, docs, memory,
small data; large PDFs/visuals are intentionally absent).

Only the lead writes git. Reviewers write Markdown under their own area
directory and nothing else.

| Area | Owner | Directory | Owns |
| --- | --- | --- | --- |
| 01 | agent 1 | `01-persistence-sync/` | `nk-store.js`, `durable_persistence.js`, `cross_device_sync.js`, restore points, state schema, account switching, multi-tab |
| 02 | agent 2 | `02-study-engines/` | `fsrs_scheduler.js`, `continue_practice_resume.js`, `bank_aware_cbt_builder.js`, `timed_*`, `exam_review_flags.js`, `practice_correction.js`, `revision_session.js`, `question_interaction.js`, session start/resume/review/submit |
| 03 | agent 3 | `03-question-rendering/` | `question_presentation.js`, `question_content_hygiene.js`, `question_details.js`, `source_visual_renderer.js`, `marrow_visual_renderer.js`, `uworld_biochemistry.js`, option/explanation/table renderers in `index.html` |
| 04 | agent 4 | `04-navigation-ui/` | `index.html` routes/pages, `app_clarity.js`, `insights_focus.js`, `learning_insights.js`, `qbank_coverage.js`, `refined_analysis.js`, `question_search.js`, `revision_desk.js`, notes UI, `study_modules.js`, `icon_refinement.js`, `interaction_polish.js` |
| 05 | agent 5 | `05-android-pwa-security/` | `MainActivity.java`, `sw.js`, `pwa_update.js`, `web_security_policy.py`, `build_web_dist.py` packaging, headers, auth/sync transport, file chooser, bridges |
| 06 | lead | `06-build-data-content/` | bank builders, `prepladder_text_bank.py`, `explanation_restructure.py`, `build_app_data.py`, `app_page.py`, question completeness, content hygiene data, generated contracts |

Boundaries that keep findings unique:

- Area 02 owns **when** a session commits; area 03 owns **what** the question
  renders; area 04 owns **where** a button goes.
- Area 01 owns the storage layer; area 05 owns the network/service-worker
  layer; a sync-merge bug belongs to 01, a cache/headers bug to 05.
- Area 06 owns build-time data correctness; a runtime renderer that mishandles
  correct data belongs to 03.
- If you find a cross-area bug, write it in the area that owns the **first
  incorrect step**, and mention the downstream file in `Files`.

Shared rules are in `TEMPLATE.md`. Do not duplicate a finding across areas.
