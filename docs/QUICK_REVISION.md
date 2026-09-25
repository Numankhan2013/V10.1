# Quick revision

**More → Quick revision** gathers Mistakes, Bookmarks, Unseen, and Due questions
across every available subject and question bank. Counts and empty states make
each queue's scope visible before Practice begins.

- **Mistakes** includes questions with an active incorrect attempt. Practice
  starts a random set of up to 20. **View all** opens the searchable cross-bank
  list and preserves single-question entry.
- **Bookmarks** starts a random set of up to 20. **View all** keeps the full
  searchable list available.
- **Unseen** excludes attempted questions and questions explicitly submitted
  as skipped. Practice starts a random set of up to 20.
- **Due review** uses the shared FSRS queue, its priority order, and the
  configured daily cap. Practice starts up to 20 due cards. Remaining cards
  stay due.

A collapsed **Focus questions** control can narrow all four queues by subject,
question bank, and source topic. The displayed counts, full Mistakes/Bookmarks
lists, and launched sessions use the same focus. Clear focus returns to the
all-subject/all-bank view. The focus stays on this page during navigation and
does not change saved question data. Due filtering is applied inside the FSRS
queue before selecting cards while its daily limit remains global.

Each created session freezes its question IDs through the existing Practice
engine. No new scheduler, category tags, or Home actions are introduced.

Implementation: `tools/revision_desk_core.js` and
`tools/apply_revision_desk_v1.py`. Verification: the behavior/transform check
`tools/test_revision_desk_v1.py` and generated-app browser journey
`tools/verify_revision_desk_browser.py`.

Build verification: Engineering `36139455865` and full generated browser/PWA/APK/Android phone+tablet emulator run `36139466345` passed at `a5f2380`. Preview: https://9907728f.nk-qbank.pages.dev. Production was not promoted; physical user review is pending.

Focused revision verification: Engineering `36146934888` and full generated browser/PWA/APK/Android emulator run `36146938774` passed at `1d3b32e`. Preview: https://f9090829.nk-qbank.pages.dev. Physical review of the focus controls is pending.
