# Learning Insights

The final Insights screen is owned by `tools/apply_learning_insights_v1.py`,
`tools/learning_insights_core.js`, and `tools/learning_insights.css`.
It preserves the shared study engines and derives analytics without a second
persisted progress model.

## Screen

- A full-year activity calendar leads the screen. It supports the past 12 months
  and available calendar years, local-day labels, daily answer details, active
  days, total answers, and longest consecutive run. Phones scroll within the
  calendar and open near today; the page itself has no horizontal overflow.
- Week/month/year controls browse past periods and compare the same elapsed
  calendar position for a current unfinished period. Subject/bank filters apply
  to dashboard metrics and the year calendar, independently of active study bank.
- Chart legends and comparison columns say This week/month/year and Previous week/month/year; historical selections use explicit date ranges. Paired donuts align even with empty data; zero-value comparison bars do not displace the visible bar from its interval label.
- Five totals lead into paired question-outcome donuts, interval answer bars,
  recorded study-time trend, period comparison, topic/subject performance,
  spaced repetition, missed-question recovery, and module progress.
- The user explicitly removed Study Map and Topics to revisit from Insights.
  Their historical helpers remain, but their UI journeys are no longer mandatory
  build steps. The new responsive dashboard journey verifies their absence.

## Metric definitions

| Metric | Definition |
| --- | --- |
| Questions practised | Effective, saved answer events for known question IDs in the period/scope. Repeated retrievals count again. |
| Distinct questions | Unique IDs among those answer events. |
| Accuracy | Correct / answered; skips are excluded. No answers displays unknown. |
| Skips | Unanswered IDs in saved submitted results, dated at completion. Pausing does not create skips. |
| Recorded study time | Each completed result's duration once, replacing its matched answer timing; unmatched answers retain saved question timing. |
| Topic accuracy | Period answer events grouped by exact subject + bank + source topic ID. Small samples are labelled. |
| Subject accuracy | Period answer events combined across selected banks per subject. |
| FSRS reviews | Answers whose source is `spaced-review` or `fsrs-review`. A rating amendment adds no retrieval. |
| Review accuracy | Correct spaced-review answers / spaced-review answers. This is observed recall, not desired retention or a prediction. |
| Due / eligible / forecast | Current scoped FSRS eligibility and due timestamps. Overdue cards enter today's forecast; local calendar days preserve DST boundaries. |
| Missed-question recovery | Distinct IDs missed in the period whose latest answer by period end is correct. A later new miss reopens the question. |
| Current unresolved | Scoped questions whose latest active answer is incorrect, irrespective of dashboard period. |
| Modules finished | Current saved modules completed during the period. |
| Module ring | Current scoped library completed / total; explicitly not a historical completion snapshot. |
| Module score / time | Completed module results in period/scope; score uses correct / selected question count, time uses the same per-question allocation as general timing. |
| Heatmap intensity | Continuous daily count divided by the displayed year's maximum daily count, within the selected subject/bank. Shade and glow use the ratio; zero activity stays neutral. |

Heatmap colors are comparative, not fixed-count bins: 40 and 60 differ; if a new
day reaches 120, earlier 40/60 days become lighter. Doubling every daily workload
leaves relative color unchanged. The legend updates to the actual busiest day.

Undo events and rating revisions do not count as answers, study days or extra
reviews. The dashboard uses effective answers, preserving original test scores.
It never fabricates missing time or treats background screen time as study time.

Completed-session time is attributed to its completion date. Subject/bank time
uses stored question timing as weights, or equal allocation when those weights
are unavailable. New results carry optional `sessionId` provenance for exact
attempt matching; legacy results match one latest compatible answer per ID.
Historical saved results are not rewritten. Removed/deleted modules and sessions
aged out of the existing 100-result history are unavailable as result analytics.

## Verification

`test_learning_insights_v1.py` runs in UTC and America/New_York and verifies
independent totals, timing deduplication, exact/legacy session attribution,
Undo/rating edits, recovery/re-misses, scope/topic identity, DST/short-month/leap
boundaries, fair comparisons, relative heatmap colors and read-only state.

`verify_learning_insights_browser.py` verifies the generated six-bank app at
320/390/820/1194 pixels: empty/seeded states, period browsing, scopes, interval
details, real full-year tiles, rescaling after a new peak, responsive sizing,
topic/FSRS navigation, reload, and the five primary navigation buttons.
Diagnostics are injected only into the test response, never the shipped app.

Full CI retains source, explanation/image, Practice/Continue, FSRS, result,
PWA/APK/package and Android WebView checks. Build verification, user review,
physical APK acceptance, and production promotion remain separate.
