# Custom Study Modules

Custom Study Modules turn existing subjects, topics, question history, bookmarks,
practice, review, and Insights into reusable focused study sets.

## Model and persistence

Modules live in the existing `qbank_state_v1` localStorage document under
`studyModules`. A module stores its subject/topic filters, pool type, frozen
question ID list, answers, submitted IDs, timing, current position, lifecycle
timestamps, completion state, and optional result-session ID.

The selected question IDs are frozen when the module is created. Changes to a
question's Wrong, Unattempted, or Bookmarked status never rebuild an existing
module. Missing IDs are skipped safely when a module resumes.

## Selection rules

1. Reuse `SUBJECTS`, each subject's existing topics, and the unified question map.
2. Filter by selected subject and topic IDs.
3. Apply Unattempted, Wrong, Bookmarked, or Mixed eligibility.
4. Deduplicate by canonical question ID.
5. Use a seeded shuffle so selection is maintainable and testable.
6. In Mixed mode, draw with a Wrong/Wrong/Unattempted/Wrong/Unattempted/Bookmarked
   weighting, then fill from remaining eligible questions.
7. Cap the created set at the actual eligible count and persist those IDs.

## Session integration

Modules create a normal Practice session with a `studyModuleId`. Existing answer,
explanation, source-PDF, navigator, Review Solutions, attempt-history, review,
and Insights paths remain authoritative. Every save synchronizes the active
session snapshot back into its module.

Finishing creates a normal Practice Analysis record linked to the module. Leaving
an unfinished module saves progress and returns Home. Restart clears module-local
progress but deliberately preserves the frozen question set and global attempt
history.

## Build ownership

`tools/apply_custom_study_modules_v1.py` runs after the V11.4 whole-app transform
and before final WebView syntax validation. `tools/test_custom_study_modules_v1.py`
covers eligibility, count contraction, deduplication, stable IDs, persistence,
resume progress, and Home prioritization.
