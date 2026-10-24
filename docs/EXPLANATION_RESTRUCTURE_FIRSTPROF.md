# Restructure run: First Prof Biochemistry, Physiology and Anatomy (2025 editions)

Same job and checker as `docs/EXPLANATION_RESTRUCTURE.md` (read its section "The
prompt"; the formatting rules are the same for every bank). Batches are on branch
`integration/v12` (Biochemistry and Physiology were also on `restructure/firstprof-base`;
both are done and imported):

| Bank | Batches (20 questions each) | Result files go in |
|---|---|---|
| Biochemistry | `data/Prepladder/biochemistry/restructure/batches/biochemistry-001` … `041` (816 Q) | `data/Prepladder/biochemistry/restructure/results/` |
| Physiology | `data/Prepladder/physiology/restructure/batches/physiology-001` … `047` (932 Q) | `data/Prepladder/physiology/restructure/results/` |
| Anatomy | `data/Prepladder/anatomy/restructure/batches/anatomy-001` … `055` (1,097 Q) | `data/Prepladder/anatomy/restructure/results/` |

Questions kept from the earlier edition (PDF-page explanations) are not in the batches.
Worked examples (generic formatting; ids are Pharmacology's):
`data/Prepladder/pharmacology/restructure/examples/example-result.json`.

## Lead-agent prompt (fill in BANK = anatomy, LAST = 055; earlier runs: biochemistry 041, physiology 047)

```text
You are the lead agent for a formatting job in the GitHub repo
Numankhan2013/V10.1. You run subagents in parallel. Correctness matters more
than speed. Bank: BANK. Batches: BANK-001 to BANK-LAST.

SETUP (once; small checkout)
  git clone --depth 1 --filter=blob:none --sparse --branch integration/v12 https://github.com/Numankhan2013/V10.1.git v10
  cd v10
  git sparse-checkout set tools data/Prepladder/BANK/source data/Prepladder/BANK/restructure data/Prepladder/pharmacology/restructure/examples docs
  git fetch --depth 1 origin restructure/BANK-all:restructure/BANK-all && git checkout restructure/BANK-all \
    || git checkout -b restructure/BANK-all
Read docs/EXPLANATION_RESTRUCTURE.md, section "The prompt" (the formatting
rules), and the worked examples in
data/Prepladder/pharmacology/restructure/examples/example-result.json.

THE WORK
- Batches: data/Prepladder/BANK/restructure/batches/BANK-NNN.json (20 questions each).
- Skip any batch whose data/Prepladder/BANK/restructure/results/BANK-NNN.result.json
  already passes the check (so you can resume).
- Run up to 6 subagents at a time, ONE batch each; give a finished one the next
  unassigned batch. Paste the SUBAGENT BRIEF to each, with NNN filled in.

AFTER EACH SUBAGENT FINISHES, YOU (the lead) MUST
1. Run: python3 tools/explanation_restructure.py check data/Prepladder/BANK/restructure/results/BANK-NNN.result.json
   Trust only this output, never the subagent's report.
2. If it is not RESTRUCTURE_CHECK_OK, send the REJECTED lines back to the same
   subagent (up to 2 rounds). Still failing: replace each failing question
   with {"id": "...", "unchanged": true} and re-check.
3. Spot-check two questions against the batch: layout follows the rules, prose
   not chopped into bullets, tables have the right columns. Also the other way:
   a question that already reads well should be "unchanged".
4. Commit that one file and push (only you run git):
     git add data/Prepladder/BANK/restructure/results/BANK-NNN.result.json
     git commit -m "Restructure BANK-NNN"
     git push -u origin restructure/BANK-all
   If rejected: git pull --rebase origin restructure/BANK-all, push again.

RULES FOR EVERYONE
- Only create files under data/Prepladder/BANK/restructure/results/. Do not
  edit, move or delete any other file.
- Do not run the bank builder, open a pull request, merge, or push to main.
- Answers are written by reading each question. No script may generate, split
  or rewrite answers (scripts may only run the checker).
- Source text is medical; keep every word, symbol and number (Greek letters,
  subscripts, arrows) exactly. Never "fix" it.

WHEN ALL ARE DONE reply with a table: batch, check line, any batch you patched.

SUBAGENT BRIEF (paste to each subagent)
  You format one batch of medical explanations. Repo checkout: ./v10.
  1. Read docs/EXPLANATION_RESTRUCTURE.md section "The prompt"; follow it
     exactly. Read the worked examples in
     data/Prepladder/pharmacology/restructure/examples/example-result.json.
  2. Read data/Prepladder/BANK/restructure/batches/BANK-NNN.json.
  3. Format every question yourself, by reading it. Keep every word exactly.
  4. Write the JSON reply to
     data/Prepladder/BANK/restructure/results/BANK-NNN.result.json
  5. Run: python3 tools/explanation_restructure.py check data/Prepladder/BANK/restructure/results/BANK-NNN.result.json
     Fix every REJECTED question and re-run until RESTRUCTURE_CHECK_OK.
  6. Do not run git; touch no other file. Reply with the final check line only.
```

## After the agents finish (needs Claude)

Fetch `restructure/BANK-all`, re-run the check, `python3 tools/explanation_restructure.py import
data/Prepladder/BANK/restructure/results/*.json`, rebuild the bank, test, PR, promote.
