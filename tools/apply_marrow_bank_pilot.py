#!/usr/bin/env python3
"""SHA-verified launcher for the chunked Marrow pilot transformer."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARTS=sorted(HERE.glob("marrow_pilot_apply.b64.part*"))
EXPECTED="ce0798cfdd1d10952e91718f980e2c77473c0557e72cbd8bdbde48a8e61663d3"
if len(PARTS)!=10:
    raise SystemExit(f"Marrow transformer payload parts mismatch: {len(PARTS)}")
payload=base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in PARTS),validate=True)
if hashlib.sha256(payload).hexdigest()!=EXPECTED:
    raise SystemExit("Marrow transformer payload SHA-256 mismatch")

exec(compile(payload,str(Path(__file__).resolve()),"exec"),{
    "__name__":"__main__",
    "__file__":str(Path(__file__).resolve()),
    "__builtins__":__builtins__,
})

# Marrow must always preserve the existing study-support contract:
# Key takeaway + native structured detailed explanation. The shared PrepLadder
# takeaway heuristic can legitimately return an empty string, so add a
# source-derived fallback only for Marrow records.
HTML=HERE.parent/"app/src/main/assets/index.html"
source=HTML.read_text(encoding="utf-8")
helper_marker="function nkMarrowTakeaway(q)"
if helper_marker not in source:
    anchor="  function nkStudySupport(q,timeMs,unattempted=false,renderedSource='') {"
    if source.count(anchor)!=1:
        raise SystemExit(f"Marrow study-support anchor count: {source.count(anchor)}")
    helper=r'''  function nkMarrowTakeaway(q) {
    const reviewed=nkSourceTakeaway(q);
    if(reviewed) return reviewed;
    const structured=q?.structuredExplanation||{};
    const raw=String(structured.text||q?.explanation||'')
      .replace(/\r/g,'\n')
      .replace(/[•▪◦]\s*/g,' ')
      .replace(/\s+/g,' ')
      .trim();
    const sentences=(raw.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[])
      .map(x=>x.replace(/^[-–—:\s]+/,'').replace(/\s+/g,' ').trim())
      .filter(x=>x.length>=24&&x.length<=280);
    if(sentences.length) return sentences[0];
    const option=Array.isArray(q?.options)?q.options[Number(q.correctOption)-1]:null;
    const answer=String(option?.text||'').replace(/\s+/g,' ').trim();
    return answer?('Correct answer: '+answer+'.'):'';
  }

'''
    source=source.replace(anchor,helper+anchor,1)

old="    const takeaway=nkSourceTakeaway(q);"
new="    const takeaway=q.bank==='Marrow'?nkMarrowTakeaway(q):nkSourceTakeaway(q);"
if source.count(old)!=1:
    raise SystemExit(f"Marrow takeaway hook count: {source.count(old)}")
source=source.replace(old,new,1)
HTML.write_text(source,encoding="utf-8")
print("MARROW_TAKEAWAY_FALLBACK_OK source-derived")
