# Phase 4 scientific-notation forensic audit — 2026-09-19 (read-only, no repairs)

Input HEAD: `ee5d0dc` (P0 memory reconciliation; product code identical to verified `f5daabe`).
Method: raw corpus scan + post-`nkNormalizeScientificDisplayText` recount. No core/test/data edits.

## Counts

- Raw: PrepLadder 117/2,686 questions with ■ (stem 14, options 14, explanation 110 fields); Marrow 2/2,711 (both Biochemistry stems; CH14_Q013 ×16, CH17_Q008 ×1).
- Post-normalization: 60 questions with remaining ■ (stem 8 fields, option 3, explanation 56, structured 1). Replacement char �: 0 fields. Caret forms (`10^6`, `10^9`, `3 × 10^9`) are explicit-source notation already handled by `nkScientificMarkup`, not OCR loss.

## Category A — deterministically repairable candidates (require source-page confirmation, not yet repaired)

- `5-10` stem (p101): `■-1,4 linkage` → α via committed stem override (build-verified). Audit artifact: generic normalization still shows ■; override is the correct layer.
- `5-14` option B (p102): `cleaves ■-1,4 linkages`; the record's own explanation states `cleaves α-1,4 linkages (Option B)`. Same glycogen family as 5-10. Needs page-102 source confirmation + stable-ID/fingerprinted override (Phase 5 candidate).
- `4-12` explanation (×2): `connected by ■-1,4 linkage` / `cleaves ■-1,4 linkages`. Same family; needs source confirmation, not a global guess.

## Category B — ambiguous, must not guess (source-backed per-record review only)

- `14-9` stem/exp (p394): `enzyme ■ ALA synthase` (δ vs α/β prefix unclear from context).
- `physiology-9-18` stem/exp (p258): `([Na+]■) is 12`, `[Na+]inside■ = 12` (stray block; Nernst-formula context).
- `physiology-20-7` stem + 2 options (p558): `V■`, `U osm (V■)/ P osm` (flow-rate/superscript symbol unclear).
- `physiology-23-11` stem/exp (p640): `UV/P ■` (unclear superscript/annotation).
- `physiology-26-20` stem/exp (p748): `■ rd of the transit time`, `■ x` (fraction loss; explanation states 0.25s but stem fraction needs source).
- `marrow__BIOCHEM_CH14_Q013` stem/exp/structured (p214): `■9 desaturase` (Δ9 likely but must confirm from source, not infer).
- `marrow__BIOCHEM_CH17_Q008` stem (p264): `■reaction` (unclear prefix).
- Explanation `F■` (ATP-synthase F0/F1, e.g. `3-8`), `CH■CONH` / `NH■` / `CONH■` fragments, `ATP■ AMP+PPi` / `NH3 ■` (arrow vs symbol unclear).

## Renderer paths involved

`nkScientificMarkup` (escape-first, shared): Practice, timed CBT, Review stems/options, takeaways,
PrepLadder explanations/tables, Marrow native structured text/tables, enhanced-explanation wrapper.
`nkQuestionStemMarkup` renders `presentation.stem ?? question`, so stem overrides (4-3/5-10 pattern) bypass generic limits safely.

## Exact gap in current normalization

`nkNormalizeScientificDisplayText` covers only unambiguous classes: pCO■/pO■ strip, H■O→H2O, FADH■→FADH2,
NADP■→NADP+, NAD■→NAD+, HCO■→HCO3−, NH4■→NH4+, CO■→CO2, O■→O2, (Ca|Mg|Fe|Cu|Zn|Mn)[²³]■→ion charge,
Na■/K■→+, Cl■→−, H■→H+. It deliberately leaves Greek-prefix loss (Δ/δ/α/β), F0/F1, arrows, fractions,
V/P annotations, and fragmented amide/acetyl formulas visible for source-backed repair.

## Phase 4 checkpoint

`PHASE 4 COMPLETE` as forensic inventory (counts/categories/examples/paths/gap above).
No code changed. Phase 5 repair must be per-record stable-ID + source-fingerprint overrides from authoritative
PDF pages (starting candidate: 5-14 p102), one record at a time with focused tests + Linux browser/CI verification.
