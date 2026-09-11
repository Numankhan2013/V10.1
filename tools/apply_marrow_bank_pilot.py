#!/usr/bin/env python3
"""SHA-verified launcher for the chunked Marrow pilot transformer."""
from __future__ import annotations
import base64, hashlib, json, zlib
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

# Load the bounded Marrow Physiology pilot with the same fail-closed,
# hash-verified shard contract used after the Anatomy transport failure.
DATA=HERE.parent/"data/marrow"
PHYS_MANIFEST_PATH=DATA/"physiology_pilot_manifest.json"
if not PHYS_MANIFEST_PATH.exists():
    raise SystemExit("Marrow Physiology pilot manifest missing")
phys_manifest=json.loads(PHYS_MANIFEST_PATH.read_text(encoding="utf-8"))
phys_parts=sorted(DATA.glob("physiology_pilot.zlib.b64.part*"))
if len(phys_parts)!=int(phys_manifest.get("parts",0)):
    raise SystemExit(f"Marrow Physiology shard count mismatch: {len(phys_parts)}")
phys_b64="".join(p.read_text(encoding="utf-8").strip() for p in phys_parts)
if len(phys_b64)!=int(phys_manifest.get("base64_chars",0)):
    raise SystemExit("Marrow Physiology base64 length mismatch")
try:
    phys_compressed=base64.b64decode(phys_b64,validate=True)
except Exception as exc:
    raise SystemExit(f"Marrow Physiology base64 invalid: {exc}") from exc
if len(phys_compressed)!=int(phys_manifest.get("compressed_bytes",0)):
    raise SystemExit("Marrow Physiology compressed length mismatch")
if hashlib.sha256(phys_compressed).hexdigest()!=phys_manifest.get("compressed_sha256"):
    raise SystemExit("Marrow Physiology compressed SHA-256 mismatch")
try:
    phys_raw=zlib.decompress(phys_compressed)
except Exception as exc:
    raise SystemExit(f"Marrow Physiology zlib invalid: {exc}") from exc
if len(phys_raw)!=int(phys_manifest.get("raw_bytes",0)):
    raise SystemExit("Marrow Physiology raw length mismatch")
if hashlib.sha256(phys_raw).hexdigest()!=phys_manifest.get("raw_sha256"):
    raise SystemExit("Marrow Physiology raw SHA-256 mismatch")
phys_record=json.loads(phys_raw.decode("utf-8"))
if phys_record.get("subject")!="Physiology" or phys_record.get("bank")!="Marrow":
    raise SystemExit("Marrow Physiology identity mismatch")
if len(phys_record.get("topics",[]))!=int(phys_manifest.get("topics",0)):
    raise SystemExit("Marrow Physiology topic count mismatch")
if len(phys_record.get("questions",[]))!=int(phys_manifest.get("questions",0)):
    raise SystemExit("Marrow Physiology question count mismatch")

# The legacy Anatomy payload still owns the generated app transform. Replace only
# its MARROW_DATA declaration with a multi-record envelope before the generic
# registry rewrite; no question engine or learner flow is duplicated.
HTML=HERE.parent/"app/src/main/assets/index.html"
source=HTML.read_text(encoding="utf-8")
data_marker="  const MARROW_DATA = "
if source.count(data_marker)!=1:
    raise SystemExit(f"Marrow data declaration count: {source.count(data_marker)}")
data_start=source.index(data_marker)+len(data_marker)
data_end=source.index(";\n",data_start)
anatomy_record=json.loads(source[data_start:data_end])
multi_record={"records":[anatomy_record,phys_record]}
multi_json=json.dumps(multi_record,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
source=source[:data_start]+multi_json+source[data_end:]
HTML.write_text(source,encoding="utf-8")
print("MARROW_PHYSIOLOGY_PILOT_OK topics=4 questions=80 sha="+phys_manifest["raw_sha256"][:12])

# Generalize the pilot's one-off Anatomy MARROW_RECORD into the canonical
# subject-indexed bank registry before any downstream Marrow presentation patches.
# The current bundle remains valid; future imports may instead provide
# {"records":[...]} without changing navigation, persistence, review, FSRS, or sync.
HTML=HERE.parent/"app/src/main/assets/index.html"
source=HTML.read_text(encoding="utf-8")
legacy_marker="  const MARROW_RECORD = "
generic_marker="  const BANKS_BY_SUBJECT = Object.create(null);"
if legacy_marker in source:
    record_start=source.index(legacy_marker)
    registry_end=source.index("  let activeSubject = ",record_start)
    generic_registry=r'''  const MARROW_RECORDS = Array.isArray(MARROW_DATA.records) ? MARROW_DATA.records : [MARROW_DATA];
  const MARROW_BY_SUBJECT = Object.freeze(Object.fromEntries(
    MARROW_RECORDS
      .filter(record=>record&&record.subject)
      .map(record=>{
        const subject=String(record.subject);
        return [subject,{
          ...record,
          subject,
          bank:'Marrow',
          topics:Array.isArray(record.topics)?record.topics:[],
          questions:Array.isArray(record.questions)?record.questions:[]
        }];
      })
  ));
  const BANKS_BY_SUBJECT = Object.create(null);
  SUBJECTS.forEach(record=>{
    const subject=String(record.subject||'');
    (record.questions||[]).forEach(question=>{
      question.question=nkCleanQuestionStem(question.question);
      question.subject=question.subject||subject;
      question.bank=question.bank||'PrepLadder';
    });
    if(subject)BANKS_BY_SUBJECT[subject]=[{...record,subject,bank:'PrepLadder'}];
  });
  Object.values(MARROW_BY_SUBJECT).forEach(record=>{
    (record.questions||[]).forEach(question=>{
      question.question=nkCleanQuestionStem(question.question);
      question.subject=question.subject||record.subject;
      question.bank='Marrow';
    });
    if(!record.subject||!record.questions.length)return;
    const list=BANKS_BY_SUBJECT[record.subject]||(BANKS_BY_SUBJECT[record.subject]=[]);
    list.push(record);
  });
  function nkBankRecords(name){
    return (BANKS_BY_SUBJECT[name]||[]).slice();
  }
  function nkBankRecord(name,bank){
    const list=nkBankRecords(name);return list.find(x=>x.bank===bank)||list[0]||null;
  }
  function nkAllBankQuestions(){
    return Object.values(BANKS_BY_SUBJECT).flatMap(records=>records.flatMap(record=>
      (record.questions||[]).map(q=>({...q,subject:q.subject||record.subject,bank:q.bank||record.bank||'PrepLadder'}))
    ));
  }
'''
    source=source[:record_start]+generic_registry+source[registry_end:]
    HTML.write_text(source,encoding="utf-8")
elif generic_marker not in source:
    raise SystemExit("Marrow bank registry anchor missing after pilot transform")
print("MARROW_BANK_REGISTRY_OK runtime=subject-indexed legacy_single_bundle=compatible")


# Promote the bounded pilots into the complete source-faithful banks supplied for
# this ingestion phase. The old 62 Anatomy / 80 Physiology records remain useful
# as accepted regression/augmentation subsets, but learner navigation now reads
# these manifest-verified expanded records. No question engine is forked.
def load_expanded_bank(prefix: str, expected_subject: str):
    manifest_path=DATA/f"{prefix}_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Expanded Marrow manifest missing: {manifest_path.name}")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    parts=sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if len(parts)!=int(manifest.get("parts",0)):
        raise SystemExit(f"{expected_subject} expanded shard count mismatch: {len(parts)}")
    encoded="".join(p.read_text(encoding="utf-8").strip() for p in parts)
    if len(encoded)!=int(manifest.get("base64_chars",0)):
        raise SystemExit(f"{expected_subject} expanded base64 length mismatch")
    try:
        compressed=base64.b64decode(encoded,validate=True)
    except Exception as exc:
        raise SystemExit(f"{expected_subject} expanded base64 invalid: {exc}") from exc
    if len(compressed)!=int(manifest.get("compressed_bytes",0)):
        raise SystemExit(f"{expected_subject} expanded compressed length mismatch")
    if hashlib.sha256(compressed).hexdigest()!=manifest.get("compressed_sha256"):
        raise SystemExit(f"{expected_subject} expanded compressed SHA-256 mismatch")
    try:
        raw=zlib.decompress(compressed)
    except Exception as exc:
        raise SystemExit(f"{expected_subject} expanded zlib invalid: {exc}") from exc
    if len(raw)!=int(manifest.get("raw_bytes",0)):
        raise SystemExit(f"{expected_subject} expanded raw length mismatch")
    if hashlib.sha256(raw).hexdigest()!=manifest.get("raw_sha256"):
        raise SystemExit(f"{expected_subject} expanded raw SHA-256 mismatch")
    record=json.loads(raw.decode("utf-8"))
    if record.get("subject")!=expected_subject or record.get("bank")!="Marrow":
        raise SystemExit(f"{expected_subject} expanded identity mismatch")
    topics=record.get("topics",[])
    questions=record.get("questions",[])
    if len(topics)!=int(manifest.get("topics",0)):
        raise SystemExit(f"{expected_subject} expanded topic count mismatch")
    if len(questions)!=int(manifest.get("questions",0)):
        raise SystemExit(f"{expected_subject} expanded question count mismatch")
    ids=[str(q.get("id","")) for q in questions]
    if len(ids)!=len(set(ids)) or any(not qid.startswith("marrow__") for qid in ids):
        raise SystemExit(f"{expected_subject} expanded IDs are not unique/namespaced")
    topic_ids={str(t.get("id")) for t in topics}
    if any(str(q.get("chapterId")) not in topic_ids for q in questions):
        raise SystemExit(f"{expected_subject} expanded question/topic linkage mismatch")
    if any(len(q.get("options",[]))!=4 or q.get("correctOption") not in (1,2,3,4) or not str(q.get("question","")).strip() for q in questions):
        raise SystemExit(f"{expected_subject} expanded question shape invalid")
    expected_letters=["A","B","C","D"]
    if any([str(opt.get("letter","")).strip() for opt in q.get("options",[])]!=expected_letters for q in questions):
        raise SystemExit(f"{expected_subject} expanded option-letter contract invalid; expected uppercase A-D")
    return record,manifest

expanded_anatomy,expanded_anatomy_manifest=load_expanded_bank("anatomy_ch001_063","Anatomy")
expanded_biochemistry,expanded_biochemistry_manifest=load_expanded_bank("biochemistry_ch001_028","Biochemistry")
expanded_physiology,expanded_physiology_manifest=load_expanded_bank("physiology_ch001_043","Physiology")
expanded_records=[expanded_anatomy,expanded_biochemistry,expanded_physiology]
expanded_ids=[q["id"] for record in expanded_records for q in record["questions"]]
if len(expanded_ids)!=2711 or len(expanded_ids)!=len(set(expanded_ids)):
    raise SystemExit(f"Expanded Marrow global ID mismatch: {len(expanded_ids)}")
if not {q["id"] for q in anatomy_record.get("questions",[])}.issubset({q["id"] for q in expanded_anatomy["questions"]}):
    raise SystemExit("Accepted Anatomy pilot IDs are not a subset of expanded Anatomy")
if not {q["id"] for q in phys_record.get("questions",[])}.issubset({q["id"] for q in expanded_physiology["questions"]}):
    raise SystemExit("Accepted Physiology pilot IDs are not a subset of expanded Physiology")

source=HTML.read_text(encoding="utf-8")
if source.count(data_marker)!=1:
    raise SystemExit(f"Expanded Marrow data declaration count: {source.count(data_marker)}")
data_start=source.index(data_marker)+len(data_marker)
data_end=source.index(";\n",data_start)
expanded_json=json.dumps({"records":expanded_records},ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
source=source[:data_start]+expanded_json+source[data_end:]
HTML.write_text(source,encoding="utf-8")
print(
    "MARROW_EXPANDED_BANKS_OK "
    f"anatomy={len(expanded_anatomy['questions'])}/{len(expanded_anatomy['topics'])} "
    f"biochemistry={len(expanded_biochemistry['questions'])}/{len(expanded_biochemistry['topics'])} "
    f"physiology={len(expanded_physiology['questions'])}/{len(expanded_physiology['topics'])} "
    f"total={len(expanded_ids)}"
)

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
    const augmented=(typeof NK_MARROW_EXPLANATION_GOLD_V1!=='undefined')?NK_MARROW_EXPLANATION_GOLD_V1[String(q?.id)]:null;
    const augmentedTakeaway=String(augmented?.takeaway||'').trim();
    if(augmentedTakeaway) return augmentedTakeaway;
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


# Approved full-bank explanation architecture: preserve Marrow source wording in
# storage, apply very light presentation-only de-duplication, improve hierarchy,
# and append separately stored exam-oriented distractor rationales.
import json, re
GOLD_PATH=HERE.parent/"data/marrow/explanation_gold_pilot.json"
gold=json.loads(GOLD_PATH.read_text(encoding="utf-8"))
if len(gold.get("questions",{}))!=62:
    raise SystemExit(f"Marrow Anatomy explanation rollout question count mismatch: {len(gold.get('questions',{}))}")
if any(len(v.get("rationales",{}))!=3 for v in gold["questions"].values()):
    raise SystemExit("Every Marrow Anatomy explanation question must have exactly three distractor rationales")

# Physiology uses the same approved learner-facing grammar as Anatomy, but its
# OCR-assisted source transcription needs a separate, auditable display layer.
# The raw Marrow record above remains unchanged; this augmentation supplies only
# source-faithful cleanup, a meaningful takeaway, selective emphasis, and
# separately-authored distractor rationales.
PHYS_GOLD_MANIFEST_PATH=DATA/"explanation_physio_pilot_manifest.json"
if not PHYS_GOLD_MANIFEST_PATH.exists():
    raise SystemExit("Marrow Physiology explanation manifest missing")
phys_gold_manifest=json.loads(PHYS_GOLD_MANIFEST_PATH.read_text(encoding="utf-8"))
phys_gold_parts=sorted(DATA.glob("explanation_physio_pilot.zlib.b64.part*"))
if len(phys_gold_parts)!=int(phys_gold_manifest.get("parts",0)):
    raise SystemExit(f"Marrow Physiology explanation shard count mismatch: {len(phys_gold_parts)}")
phys_gold_b64="".join(p.read_text(encoding="utf-8").strip() for p in phys_gold_parts)
if len(phys_gold_b64)!=int(phys_gold_manifest.get("base64_chars",0)):
    raise SystemExit("Marrow Physiology explanation base64 length mismatch")
try:
    phys_gold_compressed=base64.b64decode(phys_gold_b64,validate=True)
except Exception as exc:
    raise SystemExit(f"Marrow Physiology explanation base64 invalid: {exc}") from exc
if len(phys_gold_compressed)!=int(phys_gold_manifest.get("compressed_bytes",0)):
    raise SystemExit("Marrow Physiology explanation compressed length mismatch")
if hashlib.sha256(phys_gold_compressed).hexdigest()!=phys_gold_manifest.get("compressed_sha256"):
    raise SystemExit("Marrow Physiology explanation compressed SHA-256 mismatch")
try:
    phys_gold_raw=zlib.decompress(phys_gold_compressed)
except Exception as exc:
    raise SystemExit(f"Marrow Physiology explanation zlib invalid: {exc}") from exc
if len(phys_gold_raw)!=int(phys_gold_manifest.get("raw_bytes",0)):
    raise SystemExit("Marrow Physiology explanation raw length mismatch")
if hashlib.sha256(phys_gold_raw).hexdigest()!=phys_gold_manifest.get("raw_sha256"):
    raise SystemExit("Marrow Physiology explanation raw SHA-256 mismatch")
phys_gold=json.loads(phys_gold_raw.decode("utf-8"))
phys_gold_q=phys_gold.get("questions",{})
if phys_gold.get("scope",{}).get("subject")!="Physiology" or len(phys_gold_q)!=80:
    raise SystemExit("Marrow Physiology explanation identity/count mismatch")
if set(phys_gold_q)!=set(q.get("id") for q in phys_record.get("questions",[])):
    raise SystemExit("Marrow Physiology explanation IDs do not match the pilot bank")
if any(not str(v.get("takeaway","")).strip() or not str(v.get("displayText","")).strip() for v in phys_gold_q.values()):
    raise SystemExit("Every Marrow Physiology explanation needs takeaway and clean display text")
if any(len(v.get("rationales",{}))!=3 for v in phys_gold_q.values()):
    raise SystemExit("Every Marrow Physiology explanation needs exactly three distractor rationales")
# Biochemistry explanation augmentation now uses the user-approved grammar.
# Keep batches in separate audited JSON files so rollout can proceed chapter by
# chapter without touching the raw Marrow source bundles or creating new UI.
biochem_paths=sorted(DATA.glob("explanation_biochem_*_v1.json"))
if not biochem_paths:
    raise SystemExit("Marrow Biochemistry explanation augmentation files missing")
biochem_source_q={str(q.get("id","")):q for q in expanded_biochemistry.get("questions",[])}
biochem_gold_q={}
biochem_file_counts={}
for path in biochem_paths:
    record=json.loads(path.read_text(encoding="utf-8"))
    scope=record.get("scope",{})
    questions=record.get("questions",{})
    if (
        scope.get("subject")!="Biochemistry"
        or scope.get("bank")!="Marrow"
        or scope.get("status") not in {"approved-reference","approved-rollout"}
        or not questions
    ):
        raise SystemExit(f"Marrow Biochemistry explanation batch identity/status mismatch: {path.name}")
    declared=int(scope.get("questions",0))
    if declared!=len(questions):
        raise SystemExit(f"Marrow Biochemistry explanation batch count mismatch: {path.name}")
    overlap=set(biochem_gold_q)&set(questions)
    if overlap:
        raise SystemExit(f"Marrow Biochemistry explanation batch ID collision: {path.name} {sorted(overlap)[:3]}")
    biochem_gold_q.update(questions)
    biochem_file_counts[path.name]=len(questions)

inventory=json.loads((DATA/"explanation_inventory_v1.json").read_text(encoding="utf-8"))
sample_ids={str(row.get("id","")) for row in inventory.get("biochemistryGoldSample",[])}
gold_sample=json.loads((DATA/"explanation_biochem_gold_sample_v1.json").read_text(encoding="utf-8"))
if set(gold_sample.get("questions",{}))!=sample_ids or len(sample_ids)!=20:
    raise SystemExit("Marrow Biochemistry gold-sample IDs do not match inventory")

if not set(biochem_gold_q).issubset(biochem_source_q):
    raise SystemExit("Marrow Biochemistry explanation rollout has unknown source IDs")
for qid,cfg in biochem_gold_q.items():
    if not str(cfg.get("takeaway","")).strip() or not str(cfg.get("displayText","")).strip():
        raise SystemExit(f"Marrow Biochemistry explanation missing takeaway/displayText: {qid}")
    emphasis=cfg.get("emphasis",[])
    if not (1<=len(emphasis)<=4):
        raise SystemExit(f"Marrow Biochemistry emphasis count invalid: {qid}")
    source_q=biochem_source_q[qid]
    correct=int(source_q.get("correctOption",0))
    wrong_letters={
        str(option.get("letter") or chr(64+index)).lower()
        for index,option in enumerate(source_q.get("options",[]),1)
        if index!=correct
    }
    if len(cfg.get("rationales",{}))!=3 or set(cfg.get("rationales",{}))!=wrong_letters:
        raise SystemExit(f"Marrow Biochemistry distractor rationales mismatch: {qid}")

if set(gold["questions"]) & set(phys_gold_q):
    raise SystemExit("Marrow explanation augmentation IDs collide")
approved_gold={**gold["questions"],**phys_gold_q}
if len(approved_gold)!=142:
    raise SystemExit(f"Approved Anatomy/Physiology reference count mismatch: {len(approved_gold)}")
if set(approved_gold) & set(biochem_gold_q):
    raise SystemExit("Marrow Biochemistry rollout collides with Anatomy/Physiology explanation IDs")
all_gold={**approved_gold,**biochem_gold_q}
print(
    "MARROW_BIOCHEM_EXPLANATION_BATCHES_OK "
    f"files={len(biochem_paths)} biochemistry={len(biochem_gold_q)} "
    f"rendered_total={len(all_gold)} batches={biochem_file_counts}"
)

source=HTML.read_text(encoding="utf-8")
if "const NK_MARROW_EXPLANATION_GOLD_V1=" not in source:
    renamed,n=re.subn(
        r"function\s+nkRenderMarrowExplanation\s*\(\s*q\s*\)",
        "function nkRenderMarrowExplanationBase(q)",
        source,
        count=1,
    )
    if n!=1:
        raise SystemExit(f"Marrow renderer rename count: {n}")
    source=renamed

    cfg=json.dumps(all_gold,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
    wrapper=r'''
  const NK_MARROW_EXPLANATION_GOLD_V1=__GOLD_CONFIG__;

  function nkGoldText(text,emphasis=[]){
    let html=esc(String(text||''));
    [...emphasis].sort((a,b)=>String(b).length-String(a).length).forEach(phrase=>{
      const needle=esc(String(phrase||''));
      if(needle) html=html.split(needle).join('<strong class="nk-gold-em">'+needle+'</strong>');
    });
    return html;
  }

  function nkGoldSignalWords(text){
    const stop=new Set(['the','and','for','from','that','this','with','into','are','was','were','has','have','had','its','their','during','after','before','through','about','which','when','where','then','than','only','also','known','called']);
    return String(text||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').split(/\s+/).filter(w=>w.length>2&&!stop.has(w));
  }

  function nkGoldOverlap(a,b){
    const aa=new Set(nkGoldSignalWords(a)),bb=new Set(nkGoldSignalWords(b));
    if(!aa.size||!bb.size)return 0;
    let hit=0;aa.forEach(w=>{if(bb.has(w))hit++;});
    return hit/Math.min(aa.size,bb.size);
  }

  function nkGoldConciseText(text,q){
    let blocks=String(text||'').replace(/\r/g,'').split(/\n\s*\n/).map(x=>x.trim()).filter(Boolean);
    blocks=blocks.filter(block=>{
      const flat=block.replace(/\s+/g,' ').trim();
      if(/^options?\s+[a-d](?:\s*(?:,|and|&)\s*[a-d])*\s*:/i.test(flat))return false;
      const boiler=/\b(image|figure|flowchart)\b/i.test(flat)&&/\b(given below|shown below|below shows|image below|flowchart below|figure below)\b/i.test(flat);
      const sentences=(flat.match(/[.!?]+/g)||[]).length;
      if(boiler&&flat.length<180&&sentences<=1)return false;
      return true;
    });
    if(blocks.length>1){
      const first=blocks[0].replace(/\s+/g,' ').trim();
      const takeaway=nkMarrowTakeaway(q);
      if(first.length<=280&&takeaway&&nkGoldOverlap(first,takeaway)>=0.72)blocks.shift();
    }
    return blocks.join('\n\n');
  }

  function nkRenderMarrowGoldText(text,cfg){
    const lines=String(text||'').replace(/\r/g,'').split('\n'),out=[];let para=[],items=[],ordered=false;
    const emphasis=Array.isArray(cfg?.emphasis)?cfg.emphasis:[];
    const flushPara=()=>{if(para.length){out.push('<p>'+nkGoldText(para.join(' ').replace(/\s+/g,' ').trim(),emphasis)+'</p>');para=[];}};
    const flushList=()=>{if(items.length){const tag=ordered?'ol':'ul';out.push('<'+tag+'>'+items.map(x=>'<li>'+nkGoldText(x,emphasis)+'</li>').join('')+'</'+tag+'>');items=[];ordered=false;}};
    lines.forEach(line=>{
      const t=line.trim();
      if(!t){flushPara();flushList();return;}
      const bullet=t.match(/^[•▪◦-]\s*(.+)$/),num=t.match(/^\d+[.)]\s*(.+)$/);
      if(bullet||num){flushPara();if(items.length&&ordered!==Boolean(num))flushList();ordered=Boolean(num);items.push((bullet||num)[1]);return;}
      if(/^[A-Z][A-Za-z0-9 &/()'’+\-]{2,65}:$/.test(t)){flushPara();flushList();out.push('<div class="nk-marrow-heading">'+nkGoldText(t.slice(0,-1),emphasis)+'</div>');return;}
      para.push(t);
    });
    flushPara();flushList();
    return out.join('');
  }

  function nkRenderGoldWrongOptions(q,cfg){
    const reasons=cfg?.rationales||{},correct=Number(q.correctOption);
    const rows=(Array.isArray(q.options)?q.options:[]).map((o,i)=>({o,n:i+1})).filter(x=>x.n!==correct).map(({o,n})=>{
      const key=String(o.letter||String.fromCharCode(64+n)).toLowerCase();
      const reason=reasons[key];
      if(!reason)return'';
      return '<div class="nk-gold-wrong-row"><div class="nk-gold-wrong-option"><span>'+esc(String(o.letter||String.fromCharCode(64+n)).toUpperCase())+'</span><strong>'+esc(o.text||'')+'</strong></div><p>'+esc(reason)+'</p></div>';
    }).join('');
    return rows?'<section class="nk-gold-wrong"><div class="nk-gold-wrong-title">Why the other options are wrong</div>'+rows+'</section>':'';
  }

  function nkRenderMarrowExplanation(q){
    const cfg=NK_MARROW_EXPLANATION_GOLD_V1[String(q.id)];
    if(!cfg)return nkRenderMarrowExplanationBase(q);
    const data=q.structuredExplanation||{},text=data.text||q.explanation||'',tables=Array.isArray(data.tables)?data.tables:[];
    const displayText=String(cfg?.displayText||'').trim();
    const conciseText=displayText||nkGoldConciseText(text,q);
    const trace=q.provenance||{},pages=Array.isArray(trace.explanationPages)?trace.explanationPages:[];
    return '<div class="nk-marrow-native nk-gold-explanation">'+
      nkRenderMarrowGoldText(conciseText,cfg)+
      tables.map(nkRenderMarrowTable).join('')+
      nkRenderGoldWrongOptions(q,cfg)+
      '<div class="nk-marrow-provenance">Marrow ED 8 structured transcription'+(pages.length?' · explanation page'+(pages.length===1?'':'s')+' '+pages.join(', '):'')+'. Figure metadata is preserved for later image-asset integration.</div></div>';
  }
'''.replace("__GOLD_CONFIG__",cfg)

    anchor="  function nkMarrowTakeaway(q) {"
    if source.count(anchor)!=1:
        raise SystemExit(f"Marrow gold wrapper anchor count: {source.count(anchor)}")
    source=source.replace(anchor,wrapper+"\n"+anchor,1)

    css=r'''
<style id="nk-marrow-explanation-gold-v1">
/* Approved full-bank presentation. FSRS/session footer rules intentionally untouched. */
.nk-source-section.is-marrow .nk-gold-explanation{color:#30344f}
.nk-source-section.is-marrow .nk-gold-explanation>p{margin:0 0 18px;font-size:16.5px;line-height:1.68;font-weight:440;letter-spacing:-.08px;color:#36394f}
.nk-source-section.is-marrow .nk-gold-explanation>.nk-marrow-heading{margin:24px 0 10px;font-size:17px;line-height:1.3;font-weight:820;letter-spacing:-.2px;color:#252946}
.nk-source-section.is-marrow .nk-gold-explanation>ul,.nk-source-section.is-marrow .nk-gold-explanation>ol{margin:7px 0 20px;padding-left:26px;display:grid;gap:9px}
.nk-source-section.is-marrow .nk-gold-explanation>ul li,.nk-source-section.is-marrow .nk-gold-explanation>ol li{padding-left:2px;font-size:16px;line-height:1.58;color:#393d55}
.nk-source-section.is-marrow .nk-gold-explanation>ul li::marker{color:#448fdf}
.nk-source-section.is-marrow .nk-gold-em{font-weight:780;color:#222642}
.nk-source-section.is-marrow .nk-gold-explanation .nk-marrow-table{margin:18px 0 24px;overflow-x:auto;border:1px solid #dde2ec;border-radius:14px;background:#fff;box-shadow:0 5px 18px rgba(31,39,74,.045)}
.nk-source-section.is-marrow .nk-gold-explanation table{width:100%;min-width:520px;border-collapse:collapse;font-size:14px;line-height:1.5}
.nk-source-section.is-marrow .nk-gold-explanation caption{text-align:left;padding:14px 15px 10px;font-size:16px;font-weight:820;color:#252946;background:#fff}
.nk-source-section.is-marrow .nk-gold-explanation th{padding:11px 13px;text-align:left;vertical-align:top;background:#f4f7fb;color:#343951;font-size:12px;font-weight:820;letter-spacing:.15px;border-top:1px solid #e4e8f0;border-bottom:1px solid #dfe4ed}
.nk-source-section.is-marrow .nk-gold-explanation td{padding:12px 13px;vertical-align:top;color:#41455c;border-bottom:1px solid #eceff4}
.nk-source-section.is-marrow .nk-gold-explanation tr:last-child td{border-bottom:0}
.nk-gold-wrong{margin:28px 0 2px;padding-top:20px;border-top:1px solid #e2e5ec}
.nk-gold-wrong-title{margin-bottom:12px;font-size:17px;line-height:1.3;font-weight:840;letter-spacing:-.25px;color:#292d49}
.nk-gold-wrong-row{padding:13px 0;border-bottom:1px solid #eceef3}
.nk-gold-wrong-row:last-child{border-bottom:0}
.nk-gold-wrong-option{display:flex;align-items:flex-start;gap:9px;color:#2f334c}
.nk-gold-wrong-option>span{flex:0 0 24px;height:24px;border-radius:7px;display:grid;place-items:center;background:#fff0f1;color:#b74d5a;font-size:11px;font-weight:850}
.nk-gold-wrong-option>strong{padding-top:1px;font-size:15px;line-height:1.4;font-weight:780}
.nk-gold-wrong-row>p{margin:7px 0 0 33px;font-size:14.5px;line-height:1.55;color:#5a5e73}
.nk-source-section.is-marrow .nk-gold-explanation>.nk-marrow-provenance{margin-top:25px;padding-top:3px;font-size:10.5px;line-height:1.45;color:#9a9daa}
@media(max-width:520px){
  .nk-source-section.is-marrow .nk-gold-explanation>p{font-size:16px;line-height:1.65}
  .nk-source-section.is-marrow .nk-gold-explanation>ul li,.nk-source-section.is-marrow .nk-gold-explanation>ol li{font-size:15.5px}
  .nk-gold-wrong-row>p{font-size:14px}
}
</style>
'''
    if source.count("</head>")!=1:
        raise SystemExit(f"Marrow gold CSS head anchor count: {source.count('</head>')}")
    source=source.replace("</head>",css+"</head>",1)
    HTML.write_text(source,encoding="utf-8")
    print(f"MARROW_EXPLANATION_GOLD_OK anatomy=62 physiology=80 biochemistry={len(biochem_gold_q)} enhanced={len(all_gold)} rationales={len(all_gold)*3} raw_source=preserved fsrs=untouched")
