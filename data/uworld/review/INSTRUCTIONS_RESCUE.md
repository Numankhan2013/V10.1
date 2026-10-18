# Rescue task: transcribe UWorld questions the extractor could not assemble

Follow every rule in `INSTRUCTIONS.md` (same output keys, same `<OUT>` file naming), plus:

- `current.json` may be empty or wrong (its `issues` says why the extractor gave up). Transcribe everything from the screenshots; ignore `partial.json`.
- If no screenshot shows the answered state (green tick and choice percentages), set status "blocked" with notes "no answered screenshot".
- Choice letters must be consecutive from A. The correct answer is the green-tick choice.
- If the stem or the choices need a picture, graph, ECG or image that is NOT listed as a figure in current.json `question_blocks`, add the key "question_figure_page": N, where N is the page number (from the file name) that shows that picture largest and complete (an "Exhibit Display" popup page is best). It is cropped from that page automatically, and the question may then be "verified". Only one picture can be added this way; if it needs two or more different pictures, set status "blocked". A table of lab values in the stem may be transcribed as text lines instead ("Hemoglobin 9.0 g/dL").
- Choices that are rows of a table: transcribe them as described in `INSTRUCTIONS.md`; they may be "verified".
- If the question id on screen differs from the folder name, set status "blocked" and say so in notes.

Packets: `rescue.py <slug> packets <dir>`. Apply: `rescue.py <slug> adopt <dir> <OUT>`.
