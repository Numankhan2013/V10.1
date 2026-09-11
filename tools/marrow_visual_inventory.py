#!/usr/bin/env python3
"""Canonical source-recorded visual inventory for Marrow questions.

This module deliberately does not infer that a PDF image belongs to a question.
It only enumerates visuals already recorded in the normalized Marrow question
metadata, including question-time visuals and visual explanation blocks.  The
image pipeline may then source-compare those expectations against the PDF.
"""
from __future__ import annotations

from copy import deepcopy

QUESTION_VISUAL_KEYS = (
    "questionVisuals", "question_visuals", "questionFigures", "question_figures"
)
EXPLANATION_VISUAL_KEYS = ("figures", "visuals", "images")
VISUAL_ID_KEYS = ("visual_id", "visualId", "figure_id", "figureId", "image_id", "imageId")
PAGE_KEYS = ("source_pages", "sourcePages", "pages", "question_pages", "explanation_pages")
PAGE_KEYS_SINGLE = ("source_page", "sourcePage", "page")
NON_VISUAL_BLOCK_TYPES = {
    "paragraph", "text", "bullet_list", "bullets", "list", "table", "equation"
}


def _pages(value):
    pages=[]
    for key in PAGE_KEYS:
        raw=value.get(key)
        if isinstance(raw,(list,tuple)):
            pages.extend(x for x in raw if isinstance(x,int) and x>0)
    for key in PAGE_KEYS_SINGLE:
        raw=value.get(key)
        if isinstance(raw,int) and raw>0:
            pages.append(raw)
    return sorted(set(pages))


def _visual_id(value):
    for key in VISUAL_ID_KEYS:
        raw=value.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    return ""


def _role(value, default):
    role=str(value.get("role") or default).strip().lower()
    return "question" if role.startswith("question") else "explanation"


def _looks_visual_block(value):
    if _visual_id(value):
        return True
    kind=str(value.get("type") or value.get("visual_type") or "").strip().lower()
    if not kind or kind in NON_VISUAL_BLOCK_TYPES:
        return False
    return bool(_pages(value) or value.get("crop_norm") or value.get("cropNorm"))


def source_visual_expectations(question):
    """Return deduplicated source-declared visual expectations for one question."""
    qid=str(question.get("id") or question.get("question_id") or "")
    if not qid:
        raise ValueError("question missing stable id")
    subject=str(question.get("subject") or "")
    found=[]

    def add(value, default_role, origin, ordinal):
        if not isinstance(value,dict):
            return
        item=deepcopy(value)
        role=_role(item,default_role)
        pages=_pages(item)
        vid=_visual_id(item)
        title=str(item.get("title") or item.get("description") or item.get("visual_type") or item.get("type") or "Source figure")
        found.append({
            "questionId":qid,
            "subject":subject,
            "role":role,
            "order":int(item.get("order") or ordinal),
            "visualId":vid,
            "visualType":str(item.get("visual_type") or item.get("type") or "unknown"),
            "title":title,
            "sourcePages":pages,
            "origin":origin,
            "metadata":item,
        })

    for key in QUESTION_VISUAL_KEYS:
        rows=question.get(key)
        if isinstance(rows,list):
            for i,row in enumerate(rows,1):
                add(row,"question",key,i)

    structured=question.get("structuredExplanation") or question.get("structured_explanation") or {}
    if isinstance(structured,dict):
        for key in EXPLANATION_VISUAL_KEYS:
            rows=structured.get(key)
            if isinstance(rows,list):
                for i,row in enumerate(rows,1):
                    add(row,"explanation","structuredExplanation."+key,i)
        blocks=structured.get("blocks")
        if isinstance(blocks,list):
            visual_i=0
            for row in blocks:
                if isinstance(row,dict) and _looks_visual_block(row):
                    visual_i+=1
                    add(row,"explanation","structuredExplanation.blocks",visual_i)

    for key in ("visuals","figures","images"):
        rows=question.get(key)
        if isinstance(rows,list):
            for i,row in enumerate(rows,1):
                add(row,"explanation",key,i)

    dedup=[];seen=set()
    for row in found:
        if row["visualId"]:
            key=(row["role"],"id",row["visualId"])
        else:
            crop=row["metadata"].get("crop_norm") or row["metadata"].get("cropNorm") or []
            key=(row["role"],tuple(row["sourcePages"]),row["visualType"],row["title"],tuple(crop) if isinstance(crop,list) else str(crop))
        if key in seen:
            continue
        seen.add(key);dedup.append(row)
    for i,row in enumerate(dedup,1):
        token=row["visualId"] or f'{row["role"]}-{i}'
        row["id"]=f'{qid}:source-visual:{token}'
    return dedup


def _candidate_images(source, pages):
    result=[]
    source_pages=source.get("pages",[]) if isinstance(source,dict) else []
    for page in pages:
        if 1<=page<=len(source_pages):
            for image in source_pages[page-1].get("images",[]):
                if not image.get("pageBackgroundCandidate"):
                    result.append({"page":page,**image})
    return result


def enrich_audit_bindings(audit, question_map):
    """Add source-recorded visuals omitted by the legacy figure-only audit."""
    bindings=list(audit.get("bindings",[]))
    seen_ids={b.get("id") for b in bindings}
    seen_visuals=set()
    for b in bindings:
        meta=b.get("metadata") or {}
        vid=_visual_id(meta) if isinstance(meta,dict) else ""
        role=_role(meta,"explanation") if isinstance(meta,dict) else "explanation"
        if vid:
            seen_visuals.add((b.get("questionId"),role,vid))
    for qid,q in question_map.items():
        subject=q.get("subject")
        source=audit.get("sources",{}).get(subject,{})
        for expected in source_visual_expectations(q):
            identity=(qid,expected["role"],expected["visualId"])
            if expected["visualId"] and identity in seen_visuals:
                continue
            if expected["id"] in seen_ids:
                continue
            metadata=deepcopy(expected["metadata"])
            metadata.setdefault("role",expected["role"])
            metadata.setdefault("title",expected["title"])
            metadata["source_recorded_origin"]=expected["origin"]
            bindings.append({
                "id":expected["id"],
                "questionId":qid,
                "subject":subject,
                "metadata":metadata,
                "candidateImages":_candidate_images(source,expected["sourcePages"]),
                "status":"REVIEW_REQUIRED",
                "reason":"Source-recorded visual requires explicit ownership, role, fidelity and readability review",
                "sourceRecorded":True,
                "sourcePages":expected["sourcePages"],
                "role":expected["role"],
                "order":expected["order"],
                "visualId":expected["visualId"],
            })
            seen_ids.add(expected["id"])
            if expected["visualId"]:
                seen_visuals.add(identity)
    return bindings
