#!/usr/bin/env python3
"""Install chapter-scoped reviewed Marrow content overrides into the build owner.

The patch is deliberately narrow and idempotent. It leaves the immutable ED8
bundles untouched and layers reviewed learner-display text only after the
existing verified v1 Ch5/Ch7 override stage.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "apply_marrow_bank_pilot.py"
START = "# NK_MARROW_CONTENT_OVERRIDES_V2_START"
END = "# NK_MARROW_CONTENT_OVERRIDES_V2_END"

INSERT = r'''
# NK_MARROW_CONTENT_OVERRIDES_V2_START
# Chapter-scoped reviewed display cleanup. Every file is source-fingerprinted
# against the exact immutable source fields before mutation. V1 Ch5/Ch7 IDs are
# intentionally excluded from v2 so the accepted baseline remains unchanged.
CONTENT_OVERRIDES_V2_DIR=DATA/"content_hygiene_overrides_v2"
v2_files=sorted(CONTENT_OVERRIDES_V2_DIR.glob("**/*.json")) if CONTENT_OVERRIDES_V2_DIR.exists() else []
v2_seen_ids=set()
v2_applied_questions=0
v2_applied_explanations=0
for override_path in v2_files:
    payload=json.loads(override_path.read_text(encoding="utf-8"))
    if payload.get("schemaVersion")!=2:
        raise SystemExit(f"Marrow v2 override schema mismatch: {override_path}")
    subject=str(payload.get("subject") or "")
    chapter_id=str(payload.get("chapterId") or "")
    questions=payload.get("questions") or {}
    if not subject or not chapter_id or not isinstance(questions,dict) or not questions:
        raise SystemExit(f"Marrow v2 override identity/content invalid: {override_path}")
    ids=set(questions)
    if ids & set(override_questions):
        raise SystemExit(f"Marrow v2 overrides overlap accepted v1 IDs: {override_path}")
    if ids & v2_seen_ids:
        raise SystemExit(f"Marrow v2 duplicate stable IDs across files: {override_path}")
    if not ids.issubset(expanded_source_by_id):
        raise SystemExit(f"Marrow v2 override has unknown stable IDs: {override_path}")
    for qid in ids:
        source_q=expanded_source_by_id[qid]
        if str(source_q.get("subject"))!=subject or str(source_q.get("chapterId"))!=chapter_id:
            raise SystemExit(f"Marrow v2 override escaped declared subject/chapter: {override_path} {qid}")
    source_payload_v2=[{
        "id":qid,
        "question":expanded_source_by_id[qid].get("question"),
        "options":[option.get("text") for option in expanded_source_by_id[qid].get("options",[])],
        "explanation":expanded_source_by_id[qid].get("explanation"),
    } for qid in sorted(ids)]
    fingerprint_v2=hashlib.sha256(json.dumps(
        source_payload_v2,ensure_ascii=False,separators=(",",":"),sort_keys=True
    ).encode("utf-8")).hexdigest()
    if fingerprint_v2!=payload.get("sourceFingerprint"):
        raise SystemExit(
            f"Marrow v2 source fingerprint mismatch: {override_path} {fingerprint_v2}"
        )
    for qid,override in questions.items():
        if not isinstance(override,dict) or not override:
            raise SystemExit(f"Marrow v2 empty override: {override_path} {qid}")
        question=expanded_source_by_id[qid]
        if "question" in override:
            clean_question=override.get("question")
            if not isinstance(clean_question,str) or not clean_question.strip():
                raise SystemExit(f"Marrow v2 question override invalid: {qid}")
            question["question"]=clean_question.strip()
        if "options" in override:
            clean_options=override.get("options")
            if not isinstance(clean_options,list) or len(clean_options)!=4 or any(
                not isinstance(value,str) or not value.strip() for value in clean_options
            ):
                raise SystemExit(f"Marrow v2 option override invalid: {qid}")
            for option,value in zip(question.get("options",[]),clean_options):
                option["text"]=value.strip()
            correct_option=int(question.get("correctOption",0))
            if correct_option not in (1,2,3,4):
                raise SystemExit(f"Marrow v2 answer index invalid: {qid}")
            question["correctAnswerText"]=clean_options[correct_option-1].strip()
        if "explanation" in override:
            clean_explanation=override.get("explanation")
            if not isinstance(clean_explanation,str) or not clean_explanation.strip():
                raise SystemExit(f"Marrow v2 explanation override invalid: {qid}")
            clean_explanation=clean_explanation.strip()
            question["explanation"]=clean_explanation
            structured=question.get("structuredExplanation")
            if isinstance(structured,dict):
                structured["text"]=clean_explanation
                blocks=structured.get("blocks")
                if isinstance(blocks,list):
                    paragraph_indexes=[
                        index for index,block in enumerate(blocks)
                        if isinstance(block,dict) and str(block.get("type") or "").lower()=="paragraph"
                    ]
                    if paragraph_indexes:
                        first=paragraph_indexes[0]
                        blocks[first]={**blocks[first],"text":clean_explanation}
                        blocks[first].pop("content",None)
                        for index in reversed(paragraph_indexes[1:]):
                            del blocks[index]
                    else:
                        blocks.insert(0,{"type":"paragraph","text":clean_explanation})
            v2_applied_explanations+=1
        v2_applied_questions+=1
    v2_seen_ids.update(ids)
print(
    "MARROW_CONTENT_HYGIENE_OVERRIDES_V2_OK "
    f"files={len(v2_files)} questions={v2_applied_questions} explanations={v2_applied_explanations}"
)
# NK_MARROW_CONTENT_OVERRIDES_V2_END
'''


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1:
            raise SystemExit("v2 override marker pair is malformed")
        print("MARROW_CONTENT_OVERRIDES_V2_PATCH_ALREADY_INSTALLED")
        return
    anchor = 'print(\n    "MARROW_CONTENT_HYGIENE_OVERRIDES_OK "\n    f"questions={len(override_questions)} source={source_fingerprint[:12]}"\n)\nexpanded_ids=[q["id"] for record in expanded_records for q in record["questions"]]\n'
    if text.count(anchor) != 1:
        raise SystemExit(f"v2 override patch anchor mismatch: {text.count(anchor)}")
    replacement = anchor[:-len('expanded_ids=[q["id"] for record in expanded_records for q in record["questions"]]\n')] + INSERT + '\nexpanded_ids=[q["id"] for record in expanded_records for q in record["questions"]]\n'
    TARGET.write_text(text.replace(anchor, replacement), encoding="utf-8")
    print("MARROW_CONTENT_OVERRIDES_V2_PATCH_OK")


if __name__ == "__main__":
    main()
