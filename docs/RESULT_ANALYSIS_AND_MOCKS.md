# Result analysis and saved mocks

The late `apply_refined_analysis_v1.py` owner runs after Insights and screen
clarity. It changes result presentation and adds mock presets to the existing
CBT builder and Tests page; it does not create another study engine.

- Score is correct / all questions. Accuracy is correct / answered questions;
  an unanswered test has unknown accuracy, not zero accuracy.
- Correct, incorrect and omitted outcomes use green, coral and amber. Tests
  offer subject/topic breakdowns, grouped using exact source identities. Zero
  correct still shows incorrect or omitted evidence. Practice has no breakdown.
- Time taken uses saved session duration. Average time per question divides
  that duration by the total. Missing timing displays unknown. Distribution and
  cumulative charts use finite saved question times only, including genuine
  recorded zeroes; missing entries are excluded and counted separately.
- Review Solutions, retry comparison, missed/marked-question practice,
  Practice correction and module restart retain their original engine paths.
  Original answer counts and timing remain unchanged by later corrections.
- An optional mock name in the CBT builder saves a fixed ordered question set;
  Save mock works without starting a session. Completed tests can be renamed
  and saved as mocks. Repeat uses blank answers and a new timer, with the
  existing retake comparison when an initial exact-set result exists.
- Saved mocks are an optional durable `state.savedMocks` collection. Sync uses
  existing per-entity winners and deletion tombstones, account isolation and
  reset. Every saved question must remain available and answerable; an invalid
  exact set is blocked rather than silently shortened. Older clients preserve
  unknown state fields but do not display or sync this new collection.
- Study modules already support naming, saving, resuming and restarting; the
  result screen retains Restart module and Return Home without a topic list.

`test_refined_analysis_v1.py` checks grouping, timing boundaries, missing/zero
timing, exact repeats, unavailable questions and storage failure.
`verify_refined_analysis_browser.py` exercises 320/390/820/1194px result screens,
period labels, chart alignment, naming, reload, save, repeat and timed-session
protection. Full CI also retains the existing Practice, FSRS, review, sync,
content, package and Android phone/tablet regression gates.
