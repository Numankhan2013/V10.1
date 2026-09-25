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

Each created session freezes its question IDs through the existing Practice
engine. No new scheduler, category tags, or Home actions are introduced.

Implementation: `tools/revision_desk_core.js` and
`tools/apply_revision_desk_v1.py`. Verification: the behavior/transform check
`tools/test_revision_desk_v1.py` and generated-app browser journey
`tools/verify_revision_desk_browser.py`.
