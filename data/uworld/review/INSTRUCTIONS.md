# Review task: correct auto-extracted UWorld questions

Each folder `UWORLD_<id>/` holds:
- `current.json`: what a deterministic OCR extractor produced for one question. `issues` says why it was flagged (it may be empty).
- `page-NNNN.jpg`: the screenshots of that question (UWorld web viewer). They are the source of truth.

For every folder, look at ALL its page images and write a corrected JSON to `<OUT>/UWORLD_<id>.json` with exactly these keys:

```
{"id": "...",
 "question": "full stem text exactly as on screen",
 "options": [{"letter": "A", "text": "...", "selection_percent": 8 or null}, ...],
 "correct_label": "D",
 "answered_correctly_percent": 63 or null,
 "explanation_paragraphs": ["paragraph 1", "paragraph 2", ...],
 "educational_objective": "...",
 "status": "verified" or "blocked",
 "notes": "one line: what you changed"}
```

Rules:
- Copy text exactly as shown on screen. Fix OCR errors (split words, wrong characters, missing accents, ≥/≤ signs). Do not paraphrase, summarise or add medical content.
- The explanation is the prose under "Explanation", up to (not including) "Educational objective". Exclude text that sits inside figures, tables, diagrams, popups ("Exhibit Display") and UI chrome (toolbar, "Correct answer", "Answered correctly", "Time Spent", "Version", footer, watermarks). Keep each paragraph once, even if screenshots overlap. Paragraphs starting "(Choice X)" or "(Choices X and Y)" are separate paragraphs.
- The objective is the text after "Educational objective:", without the subject/system/topic labels and "References".
- Options: letters A, B, C… in order. The percentage in brackets after each choice is `selection_percent` (null if not shown).
- Choices that are table rows: write each choice as its row values joined with " · ", each prefixed by its column header (e.g. "TSH ↑ · Free T4 ↓ · Free T3 ↓"). Choices that are letters or labels on a figure/graph: write the label exactly as shown (e.g. "A"), and make sure the figure that carries those labels is part of the question (it already is when current.json has a question_blocks figure; if it is missing, set status "blocked" and say which page shows it). Such questions may be "verified" when the transcription is exact.
- The correct answer is the choice with the GREEN TICK on the answered screenshot. If it differs from current.json's correct_label, use the tick and say "answer changed X→Y (green tick on page N)" in notes.
- If the folder's pages contain parts of a different question (another Question Id in the header), use only the pages whose header shows this folder's question id and say which pages you ignored.
- Never invent text you cannot see. If something needed is not visible in any page, leave it out and set status "blocked".
- Set status "verified" only if you are confident that everything matches the screenshots; otherwise "blocked" and say why in notes.
- Work only from the files in this folder. Do not read other directories.

Apply with `tools/uworld_auto/apply_reviews.py <slug> <OUT> --careful`.
