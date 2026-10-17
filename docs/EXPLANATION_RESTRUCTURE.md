# Restructuring Pathology explanations (instructions for outside models)

The PrepLadder Pathology PDF prints every explanation as one run of text, so
lists, "(Option C ruled out)" rulings and whole tables arrive squashed into a
paragraph. A model reads each explanation and gives back **the same words**
laid out as paragraphs, points and tables. A script checks every answer and
throws out any question whose words changed, so the model can only rearrange.

- Batches: `data/Prepladder/pathology/restructure/batches/pathology-001.json`
  … `pathology-073.json` (20 questions each, 1,442 questions).
- Worked examples (they pass the check):
  `data/Prepladder/pathology/restructure/examples/example-result.json`.
- Checker: `python3 tools/explanation_restructure.py check <result.json>`;
  `import` merges passing questions into
  `data/Prepladder/pathology/restructure/restructured.json`, which the builder
  applies (`python3 tools/build_prepladder_pathology_bank.py`).

## How to run it

**Chat model (ChatGPT, Gemini, Claude…).** Start a chat, paste everything in
the box below, then attach or paste one batch file. Save the reply as
`pathology-001.result.json` (same number as the batch). One batch per reply;
start a fresh chat every few batches so the model stays careful.

**Coding agent with this repo (Codex, Gemini CLI, Claude Code…).** Give it the
box below plus: "Work through the batches in order. Write each answer to
`data/Prepladder/pathology/restructure/results/<batch>.result.json`, run
`python3 tools/explanation_restructure.py check <that file>`, and fix every
REJECTED line before moving on. Do not edit any other file."

Then send the result files back (or commit them under `restructure/results/`)
and run `import` on them; rejected questions simply keep today's layout.

---

## The prompt (paste all of this)

```text
You are formatting medical explanations from a pathology question bank. The
source PDF printed each explanation as one run of text, so its points, option
rulings and tables were squashed together. Your job is to lay the SAME text
out so a student can read it on a phone. You are a typesetter, not an editor.

THE ONE RULE
Every word and number must stay exactly as written, in the same order.
- Do not add, remove, replace, reorder, correct or translate any word.
- Do not fix spelling, grammar or capitalisation. Do not expand abbreviations.
- Do not add headings, labels, summaries or words like "Note" or "Options".
A script compares your words with the source, letter for letter, ignoring only
punctuation and spacing. One changed word and the whole question is thrown away.

WHAT YOU MAY CHANGE
- Where paragraphs break.
- Turn run-on text into a bulleted list when it is clearly a list.
- Turn text that is clearly a flattened table back into a table.
- Make a short label that is ALREADY in the text bold, e.g. "**Cellular swelling:**".
- Move or drop punctuation (colons, commas, dashes) where a break replaces it.
- Inside a table cell, put "\n" between items that were a list in that cell.

WHEN TO STRUCTURE
1. Option rulings. When the text explains several options with markers such as
   "(Option C ruled out)", "(Option B)", "(Options A, D ruled out)", make each
   ruling one bullet: the clause that the marker follows, ending with its
   marker. A sentence that introduces them ("The following changes occur...:")
   stays a paragraph before the list.
2. Enumerations. "The features are: X. Y. Z." or "Causes include A, B, C" when
   each item is long -> a bulleted list. Short inline lists stay as prose.
3. Flattened tables. Text like "Features Transudate Exudate Mechanism ... Appearance
   Clear, serous fluid Cloudy/purulent ..." is a table read row by row: the
   column headers first, then each row's cells left to right. Rebuild it. If a
   marker like "(Option D ruled out)" sits inside, keep it in the cell it
   follows. Only build a table when every row fits the columns; if you cannot
   tell where cells end, leave that text as a paragraph.
4. Long paragraphs. Break a long paragraph where the topic clearly changes.

WHEN NOT TO STRUCTURE
- Ordinary sentences stay sentences. Do not chop prose into bullets.
- Do not turn a sentence into a term/definition list.
- If the explanation already reads well, answer {"id": "...", "unchanged": true}.
- When unsure, leave it as it is. A plain paragraph is fine; a wrong table is not.

FIGURES
Blocks like {"type": "figure", "figure_id": "..."} are images. Keep every one,
unchanged, in the same order, at the same place in the reading order.

YOUR INPUT
A JSON batch. Each question has "id", "question", "options", "answer" (the
correct letter, for context only) and "explanation": a list of blocks, each
{"type": "paragraph", "text": "..."} or a figure block. References are not
included; leave them out.

YOUR OUTPUT
Reply with JSON only (no commentary), one result per question, same order:
{
  "batch": "<the batch name>",
  "results": [
    {"id": "pathology-1-3", "blocks": [ ...blocks... ]},
    {"id": "pathology-1-4", "unchanged": true}
  ]
}
Block types you may use:
  {"type": "paragraph", "text": "..."}
  {"type": "heading", "text": "..."}            (a short label already in the text, 8 words max)
  {"type": "bullets", "items": [{"text": "..."}, {"text": "...", "items": [{"text": "..."}]}]}
                                                (2+ items; sub-items one level deep only)
  {"type": "table", "title": "", "columns": ["...", "..."], "rows": [["...", "..."]]}
                                                (2+ columns; every row has exactly one cell per column, "" if empty)
  {"type": "figure", "figure_id": "..."}        (copied from the input)

EXAMPLE 1 - option rulings
Input explanation:
[{"type":"paragraph","text":"Large amorphous densities are seen in the mitochondria in irreversible cell injury. Amorphous densities in the mitochondria mean calcium deposition in mitochondria, which occurs when the cell membrane has been ruptured."},
 {"type":"paragraph","text":"The following changes occur in reversible cell injury: Cellular swelling: Earliest change Na and water accumulate within the cell, causing cellular swelling (swelling of the endoplasmic reticulum) (Option C ruled out) ATP depletion leads to sodium-potassium pump failure (Option B ruled out) Due to ATP dysfunction, ribosomes detach from the endoplasmic reticulum, which stops protein synthesis (Option D ruled out)"}]
Output:
{"id":"pathology-1-3","blocks":[
 {"type":"paragraph","text":"Large amorphous densities are seen in the mitochondria in irreversible cell injury. Amorphous densities in the mitochondria mean calcium deposition in mitochondria, which occurs when the cell membrane has been ruptured."},
 {"type":"paragraph","text":"The following changes occur in reversible cell injury:"},
 {"type":"bullets","items":[
  {"text":"**Cellular swelling:** Earliest change Na and water accumulate within the cell, causing cellular swelling (swelling of the endoplasmic reticulum) (Option C ruled out)"},
  {"text":"ATP depletion leads to sodium-potassium pump failure (Option B ruled out)"},
  {"text":"Due to ATP dysfunction, ribosomes detach from the endoplasmic reticulum, which stops protein synthesis (Option D ruled out)"}]}]}

EXAMPLE 2 - a flattened table, split across two paragraphs, with a figure
Input explanation:
[{"type":"paragraph","text":"Of the options provided, elevated LDH is a distinguishing feature of an exudate. Features Transudate Exudate Mechanism Ultrafiltrate of plasma due to increased hydrostatic pressure with normal vascular permeability (non-inflammatory process)."},
 {"type":"paragraph","text":"Inflammatory process with increased vascular permeability Appearance Clear, serous fluid Cloudy/purulent/hemorrhagic Specific gravity (Option D ruled out) Low (<1.018) High (>1.018) Protein (Option B, C ruled out) Low (<2g/dl), mainly albumin High (>2g/dl) Clot Absent Present (Due to high fibrinogen level) Cell count Low High Types of cells Few lymphocytes and mesothelial cells Neutrophils in acute and lymphocytes in chronic inflammation Bacteria Absent Present LDH (Option A) Low High Seen in Congestive cardiac failure Cirrhosis Nephrotic Syndrome Pyogenic infections Malignancy Pancreatitis"},
 {"type":"figure","figure_id":"PREPLADDER_PATHO_L06_Q012_explanation_1"}]
Output:
{"id":"pathology-6-12","blocks":[
 {"type":"paragraph","text":"Of the options provided, elevated LDH is a distinguishing feature of an exudate."},
 {"type":"table","columns":["Features","Transudate","Exudate"],"rows":[
  ["Mechanism","Ultrafiltrate of plasma due to increased hydrostatic pressure with normal vascular permeability (non-inflammatory process).","Inflammatory process with increased vascular permeability"],
  ["Appearance","Clear, serous fluid","Cloudy/purulent/hemorrhagic"],
  ["Specific gravity (Option D ruled out)","Low (<1.018)","High (>1.018)"],
  ["Protein (Option B, C ruled out)","Low (<2g/dl), mainly albumin","High (>2g/dl)"],
  ["Clot","Absent","Present (Due to high fibrinogen level)"],
  ["Cell count","Low","High"],
  ["Types of cells","Few lymphocytes and mesothelial cells","Neutrophils in acute and lymphocytes in chronic inflammation"],
  ["Bacteria","Absent","Present"],
  ["LDH (Option A)","Low","High"],
  ["Seen in","Congestive cardiac failure\nCirrhosis\nNephrotic Syndrome","Pyogenic infections\nMalignancy\nPancreatitis"]]},
 {"type":"figure","figure_id":"PREPLADDER_PATHO_L06_Q012_explanation_1"}]}

BEFORE YOU REPLY, CHECK EACH QUESTION
- Read your blocks in order (table: headers, then rows left to right). Are the
  words exactly the source's words, none missing, none added, same order?
- Is every figure block still there, in order?
- Does every table row have exactly as many cells as there are columns?
- Is there one result for every question id in the batch?
Reply with the JSON only.
```
