#!/usr/bin/env python3
"""Add post-answer historical community response stats without changing QBank UI/logic.

The source sidecar is matched fail-closed to the canonical Marrow Biochemistry
bundle at build time. Runtime presentation is additive only: existing option
classes, answer logic, navigation, CBT behavior, and explanation rendering are
left untouched. Percentages are never rendered until correctness is already
revealed by the existing question renderer.
"""
from __future__ import annotations

import base64
import difflib
import hashlib
import html
import json
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
DATA = ROOT / "data/marrow"
STATS = DATA / "community_stats_v1.json"
BUNDLE_PREFIX = "biochemistry_ch001_028"
STYLE_ID = "nk-community-stats-v1-style"
SCRIPT_ID = "nk-community-stats-v1-script"
SUBSCRIPT_TRANS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def normalize_stem(value: str) -> str:
    value = html.unescape(str(value or "")).lower()
    value = re.sub(r"[_\W]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def normalize_option(value: str) -> str:
    value = html.unescape(str(value or "")).translate(SUBSCRIPT_TRANS).lower()
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def load_verified_bundle(prefix: str) -> dict:
    manifest_path = DATA / f"{prefix}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if len(parts) != int(manifest.get("parts", 0)):
        raise SystemExit(f"Community stats: {prefix} shard count mismatch")
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    if len(encoded) != int(manifest.get("base64_chars", 0)):
        raise SystemExit(f"Community stats: {prefix} base64 length mismatch")
    compressed = base64.b64decode(encoded, validate=True)
    if len(compressed) != int(manifest.get("compressed_bytes", 0)):
        raise SystemExit(f"Community stats: {prefix} compressed length mismatch")
    if hashlib.sha256(compressed).hexdigest() != manifest.get("compressed_sha256"):
        raise SystemExit(f"Community stats: {prefix} compressed SHA-256 mismatch")
    raw = zlib.decompress(compressed)
    if len(raw) != int(manifest.get("raw_bytes", 0)):
        raise SystemExit(f"Community stats: {prefix} raw length mismatch")
    if hashlib.sha256(raw).hexdigest() != manifest.get("raw_sha256"):
        raise SystemExit(f"Community stats: {prefix} raw SHA-256 mismatch")
    return json.loads(raw.decode("utf-8"))


def source_option_map(record: dict) -> dict[str, str]:
    options = record.get("sourceOptions") or {}
    if set(options) != {"A", "B", "C", "D"}:
        return {}
    normalized = {letter: normalize_option(options[letter]) for letter in "ABCD"}
    if any(not value for value in normalized.values()) or len(set(normalized.values())) != 4:
        return {}
    return normalized


def option_fingerprint_match(question: dict, source_options: dict[str, str]) -> dict[str, str] | None:
    options = question.get("options") or []
    if len(options) != 4:
        return None
    canonical = {str(option.get("letter", "")): normalize_option(option.get("text", "")) for option in options}
    if set(canonical) != {"A", "B", "C", "D"} or any(not value for value in canonical.values()):
        return None
    if set(canonical.values()) != set(source_options.values()):
        return None
    # Return source letter -> canonical letter so percentages remain attached to
    # the exact option text even if a newer QBank edition reordered choices.
    reverse = {value: letter for letter, value in canonical.items()}
    return {source_letter: reverse[value] for source_letter, value in source_options.items()}


def find_canonical_question(record: dict, questions: list[dict], by_stem: dict[str, list[dict]]) -> tuple[dict, dict[str, str], str]:
    stem_key = normalize_stem(record.get("questionStem", ""))
    exact = by_stem.get(stem_key, [])
    source_options = source_option_map(record)

    if len(exact) == 1:
        question = exact[0]
        if source_options:
            mapping = option_fingerprint_match(question, source_options)
            if mapping is None:
                raise SystemExit(
                    f"Community stats: exact stem matched {question.get('id')} but source options differ"
                )
        else:
            mapping = {letter: letter for letter in "ABCD"}
        return question, mapping, "exact_stem"
    if len(exact) > 1:
        raise SystemExit(
            f"Community stats: ambiguous exact stem for {record.get('sourceQuestionId')}: {len(exact)} matches"
        )

    # Old solved-QBank references can use slightly different wording from ED8.
    # In that case, only accept a question whose full four-option fingerprint is
    # identical after harmless formula/markup normalization. This is stricter
    # than fuzzy-stem matching and prevents percentages being attached to a
    # merely similar question.
    if source_options:
        fingerprint_matches: list[tuple[dict, dict[str, str], float]] = []
        for question in questions:
            mapping = option_fingerprint_match(question, source_options)
            if mapping is None:
                continue
            ratio = difflib.SequenceMatcher(
                None, stem_key, normalize_stem(question.get("question", ""))
            ).ratio()
            fingerprint_matches.append((question, mapping, ratio))
        if len(fingerprint_matches) == 1:
            question, mapping, ratio = fingerprint_matches[0]
            if ratio < 0.45:
                raise SystemExit(
                    f"Community stats: option fingerprint found {question.get('id')} but stem similarity "
                    f"is only {ratio:.3f}"
                )
            return question, mapping, f"option_fingerprint:{ratio:.3f}"
        if len(fingerprint_matches) > 1:
            fingerprint_matches.sort(key=lambda item: item[2], reverse=True)
            details = ", ".join(
                f"{item[0].get('id')}:{item[2]:.3f}" for item in fingerprint_matches[:5]
            )
            raise SystemExit(
                f"Community stats: ambiguous option fingerprint for {record.get('sourceQuestionId')}: {details}"
            )

    nearest = sorted(
        (
            difflib.SequenceMatcher(None, stem_key, normalize_stem(question.get("question", ""))).ratio(),
            str(question.get("id", "")),
            str(question.get("question", ""))[:120],
        )
        for question in questions
    )[-5:]
    nearest.reverse()
    debug = " | ".join(f"{qid}:{score:.3f}:{stem}" for score, qid, stem in nearest)
    raise SystemExit(
        f"Community stats: no safe canonical match for {record.get('sourceQuestionId')}; nearest={debug}"
    )


def resolved_stats() -> tuple[dict, dict]:
    payload = json.loads(STATS.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != 1:
        raise SystemExit("Community stats: unsupported sidecar schema")
    source = payload.get("source") or {}
    records = payload.get("records") or []
    if not records:
        raise SystemExit("Community stats: no source records")

    bank = load_verified_bundle(BUNDLE_PREFIX)
    if bank.get("subject") != "Biochemistry" or bank.get("bank") != "Marrow":
        raise SystemExit("Community stats: canonical Biochemistry bundle identity mismatch")
    questions = bank.get("questions") or []
    by_stem: dict[str, list[dict]] = {}
    for question in questions:
        by_stem.setdefault(normalize_stem(question.get("question", "")), []).append(question)

    resolved: dict[str, dict] = {}
    browser_by_stem: dict[str, dict] = {}
    match_methods: list[str] = []
    for record in records:
        if record.get("subject") != "Biochemistry":
            raise SystemExit("Community stats: v1 pilot currently accepts Biochemistry records only")
        question, source_to_canonical, match_method = find_canonical_question(record, questions, by_stem)
        qid = str(question.get("id", ""))
        options = question.get("options") or []
        if len(options) != 4 or [str(o.get("letter", "")) for o in options] != ["A", "B", "C", "D"]:
            raise SystemExit(f"Community stats: option contract mismatch for {qid}")
        source_pct = record.get("optionPct") or {}
        if set(source_pct) != {"A", "B", "C", "D"}:
            raise SystemExit(f"Community stats: A-D distribution missing for {qid}")
        values = [int(source_pct[letter]) for letter in "ABCD"]
        if any(value < 0 or value > 100 for value in values) or sum(values) != 100:
            raise SystemExit(f"Community stats: invalid response distribution for {qid}")

        # Remap percentages by option identity, not by source letter position.
        option_pct = {
            canonical_letter: int(source_pct[source_letter])
            for source_letter, canonical_letter in source_to_canonical.items()
        }
        if set(option_pct) != {"A", "B", "C", "D"}:
            raise SystemExit(f"Community stats: option remap incomplete for {qid}")
        correct_index = int(question.get("correctOption", 0))
        if correct_index not in (1, 2, 3, 4):
            raise SystemExit(f"Community stats: canonical correct option invalid for {qid}")
        correct_letter = "ABCD"[correct_index - 1]
        correct_pct = int(record.get("correctPct", -1))
        if correct_pct != int(option_pct[correct_letter]):
            raise SystemExit(
                f"Community stats: correctPct does not match canonical answer for {qid} "
                f"({correct_letter})"
            )
        canonical_stem_key = normalize_stem(question.get("question", ""))
        item = {
            "canonicalQuestionId": qid,
            "sourceQuestionId": str(record.get("sourceQuestionId", "")),
            "source": str(source.get("name", "")),
            "sourceVersion": str(source.get("version", "")),
            "correctPct": correct_pct,
            "optionPct": {letter: int(option_pct[letter]) for letter in "ABCD"},
        }
        if qid in resolved or canonical_stem_key in browser_by_stem:
            raise SystemExit(f"Community stats: duplicate resolved record for {qid}")
        resolved[qid] = item
        browser_by_stem[canonical_stem_key] = item
        match_methods.append(f"{qid}={match_method}")
    print("COMMUNITY_STATS_MATCH_OK " + " ".join(match_methods))
    return resolved, browser_by_stem


resolved, browser_by_stem = resolved_stats()
s = HTML.read_text(encoding="utf-8")
s = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', "", s, flags=re.S)
s = re.sub(rf'<script id="{SCRIPT_ID}">.*?</script>\s*', "", s, flags=re.S)

css = f'''<style id="{STYLE_ID}">
/* NK_COMMUNITY_STATS_V1_START — additive post-answer metadata only. */
.question-card .nk-community-option-pct{{display:inline-block;margin-left:7px;padding:2px 6px;border-radius:999px;background:#f1f2f6;color:#686f83;font-size:11px;font-weight:800;line-height:1.35;vertical-align:1px;white-space:nowrap}}
.question-card .option.correct .nk-community-option-pct{{background:#e1f5ec;color:#11835f}}
.question-card .option.wrong .nk-community-option-pct{{background:#fde8ea;color:#ba3f4d}}
.question-card .nk-community-correct-summary{{margin:9px 2px 0;color:#6c7284;font-size:12px;font-weight:560;line-height:1.4}}
.question-card .nk-community-correct-summary strong{{color:inherit;font-weight:850}}
/* NK_COMMUNITY_STATS_V1_END */
</style>'''

stats_json = json.dumps(browser_by_stem, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
script = f'''<script id="{SCRIPT_ID}">
/* NK_COMMUNITY_STATS_V1_START
   Historical response percentages are deliberately presentation-only.
   Existing correctness classes are the reveal gate, so stats cannot cue an
   answer during Practice selection or an in-progress CBT. */
(function(){{
  const BY_STEM=Object.freeze({stats_json});
  function normalize(value){{
    return String(value||'').toLowerCase().replace(/[_\\W]+/g,' ').replace(/\\s+/g,' ').trim();
  }}
  function clear(card){{
    card.querySelectorAll('.nk-community-option-pct,.nk-community-correct-summary').forEach(node=>node.remove());
    card.removeAttribute('data-nk-community-stats');
  }}
  function apply(card){{
    const stem=card.querySelector('.question-text');
    const stat=stem?BY_STEM[normalize(stem.textContent)]:null;
    if(!stat){{ clear(card); return; }}
    const revealed=!!card.querySelector('.option.correct,.option.wrong');
    if(!revealed){{ clear(card); return; }}
    const list=card.querySelector('.option-list');
    if(!list){{ clear(card); return; }}
    list.querySelectorAll('.option').forEach((option,index)=>{{
      const letterNode=option.querySelector('.option-letter');
      const letter=(letterNode?String(letterNode.textContent||'').trim().toUpperCase():String.fromCharCode(65+index));
      const pct=stat.optionPct && stat.optionPct[letter];
      const text=option.querySelector('.option-text');
      if(text && Number.isFinite(Number(pct)) && !text.querySelector('.nk-community-option-pct')){{
        const badge=document.createElement('span');
        badge.className='nk-community-option-pct';
        badge.textContent=String(pct)+'%';
        badge.setAttribute('aria-label',String(pct)+' percent selected this option');
        text.appendChild(badge);
      }}
    }});
    let summary=card.querySelector('.nk-community-correct-summary');
    if(!summary){{
      summary=document.createElement('div');
      summary.className='nk-community-correct-summary';
      summary.innerHTML='<strong>'+String(stat.correctPct)+'%</strong> of the people got this right';
      summary.title=(stat.source||'')+(stat.sourceVersion?' · '+stat.sourceVersion:'');
      list.insertAdjacentElement('afterend',summary);
    }}
    card.setAttribute('data-nk-community-stats',stat.canonicalQuestionId||'1');
  }}
  let queued=false;
  function scan(){{
    queued=false;
    document.querySelectorAll('.question-card').forEach(apply);
  }}
  function schedule(){{
    if(queued)return;
    queued=true;
    if(typeof requestAnimationFrame==='function')requestAnimationFrame(scan);else setTimeout(scan,0);
  }}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',schedule);else schedule();
  new MutationObserver(schedule).observe(document.documentElement,{{subtree:true,childList:true,attributes:true,attributeFilter:['class']}});
}})();
/* NK_COMMUNITY_STATS_V1_END */
</script>'''

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("Community stats: HTML anchors missing")
s = s.replace("</head>", css + "\n</head>", 1)
s = s.replace("</body>", script + "\n</body>", 1)
HTML.write_text(s, encoding="utf-8")
print("COMMUNITY_STATS_V1_OK resolved=" + str(len(resolved)) + " ids=" + ",".join(sorted(resolved)))
