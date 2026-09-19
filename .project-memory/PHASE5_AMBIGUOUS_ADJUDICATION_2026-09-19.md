# Phase 5 ambiguous-notation adjudication — 2026-09-19 (read-only, no repairs)

Input HEAD: `4c00bd9` (`feature/marrow-canonical-full-current`; product code identical to verified `bf1be33`).
Method: per-record authoritative-source check with pypdf text-layer extraction (plus `fonttools` for Marrow CFF/Symbol fonts). No core/test/data edits. Deterministic queue first: a corpus scan for further `■-1,4` / `■-1,6` family instances found only the four already-repaired display sites (5-10 stem, 5-14 option B, 2× 4-12 explanation — stored source strings intentionally unchanged). The deterministic repair set is empty.

Status: **all 7 remaining Phase 4 Category-B candidates stay flagged; none meets the source-confirmation bar.** No product code changed.

## Per-record evidence

- `14-9` (Biochemistry p394; `enzyme ■ ALA synthase`): authoritative solution (PDF p412) carries the identical `■ ALAsynthase` in its own text layer. δ/α/β prefix unresolvable from available source. FLAG.
- `physiology-9-18` (p258; `([Na■]■)`, explanation `[Na■]inside■`): solution (PDF p291) carries the identical blocks. First `■` already resolves to Na+ through the safe generic rule; the trailing `■` (subscript vs stray) is unresolvable. Answer (61 mV) unaffected. FLAG.
- `physiology-20-7` (p558; `V■` stem + 2 options): solution (PDF p573–574) discusses urine flow rate in words only and never renders the symbol (likely V-dot, unconfirmable from text). FLAG.
- `physiology-23-11` (p640; `UV/P ■`): solution (PDF p663) writes the formula bare as `UV/P,` yet also carries bare `■` in distractor rationales — subscript-x vs stray artifact unresolvable. FLAG.
- `physiology-26-20` (p748; `■ rd`, `■ x`): solution (PDF p766) carries the identical blocks. The value is arithmetically forced by the record's own equation (■ × 0.75 = 0.25 → 1/3), but the rendered form is unknown and the stem is explicitly diagram-dependent, so per Category-B + image-lane ownership it stays flagged rather than reconstructed. FLAG.
- `marrow__BIOCHEM_CH14_Q013` (Marrow p214/217/222; `■9 desaturase` ×6 fields): Marrow text layer is custom-font garbled (`/uni25A0` leak, mojibake) with and without `fonttools`; rendered source shows ■ per existing reviewNotes. Δ9 strongly suggested by same-explanation `Δ9,12` + stearic→oleic biology, but that is inference, not source confirmation. FLAG.
- `marrow__BIOCHEM_CH17_Q008` (Marrow p264/269/274; `■reaction`): text layers unusable (no `reaction` contexts extract); own explanation heavily garbled; answer (NH3) unaffected; prefix word unconfirmable. FLAG.

## Phase 5 checkpoint implication

`PHASE 5 COMPLETE` as far as safe per-record repair goes: shared notation architecture extended conservatively (4-3/5-10 stem, 5-14 option, 4-12 explanation overrides, all build/browser-verified); no broad regex introduced; ambiguous loss left visible per policy. Remaining notation work (55 PrepLadder + 1 Marrow explanation residuals: F0/F1, amide fragments, arrows) is per-record source-visual comparison, not text-layer repair — it belongs to a future source-review lane with rendered-page evidence, not to this campaign's text architecture.
