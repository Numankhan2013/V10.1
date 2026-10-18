# UWorld review batches (Microbiology, Dermatology, Immunology, Ethics, ENT)

This branch (`uworld-review`) holds only review material; it is never merged into `main`.

- `batches/flagged-01` … `flagged-18`: 108 questions the extractor assembled but could not verify. Follow `INSTRUCTIONS.md`.
- `batches/rescue-01` … `rescue-08`: 40 questions the extractor could not assemble. Follow `INSTRUCTIONS.md` **and** `INSTRUCTIONS_RESCUE.md`.
- Each question folder `UWORLD_<id>/` has `current.json` (what the extractor read; rescue folders also have `partial.json`, ignore it) and `page-NNNN.jpg` screenshots, which are the source of truth.
- Answers go to `answers/<batch>/UWORLD_<id>.json` (that folder is the `<OUT>` of the instructions), one per question folder.
- Check: `python3 tools/uworld_auto/review/check_review.py data/uworld/review/batches/<batch>` (plain Python 3, no packages). It must print `0 problems`.

## Prompt for one agent (fill in the range)

```text
You are transcribing medical exam questions from screenshots in the GitHub repo
Numankhan2013/V10.1, branch uworld-review.

Your batches: <FIRST> to <LAST>   (e.g. flagged-01 to flagged-04, or rescue-01 to rescue-02)

1. Check out branch uworld-review and create your own branch from it:
   uworld-review/<FIRST>-<LAST>. Never push to main or to uworld-review itself.
2. Read data/uworld/review/README.md and data/uworld/review/INSTRUCTIONS.md.
   For rescue batches also read data/uworld/review/INSTRUCTIONS_RESCUE.md.
   Follow them exactly.
3. For every question folder in each of your batches
   (data/uworld/review/batches/<batch>/UWORLD_<id>/), open EVERY page-NNNN.jpg
   and write data/uworld/review/answers/<batch>/UWORLD_<id>.json.
   Copy text exactly as on screen; never invent or paraphrase. The correct answer
   is the choice with the green tick. When unsure, set "status": "blocked" and
   say why in "notes".
4. Run: python3 tools/uworld_auto/review/check_review.py data/uworld/review/batches/<batch>
   for each batch and fix every problem until it prints "0 problems".
5. Commit only files under data/uworld/review/answers/ and push your branch.
   Do not change or delete anything else.
```

Suggested split: 18 flagged batches + 8 rescue batches = 26 batches; for example
one agent per 4 flagged batches (`flagged-01`–`04`, `05`–`08`, `09`–`12`, `13`–`16`, `17`–`18`)
and one per 4 rescue batches (`rescue-01`–`04`, `05`–`08`).
