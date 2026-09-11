#!/usr/bin/env python3
"""Fail-closed visual discovery helpers for the Marrow image pipeline.

Visual metadata is useful but not complete: some normalized records have dropped
question-time visuals and some canonical records never named every source figure.
Therefore source completeness is anchored to non-background PDF image placements
on canonical question/explanation pages. Metadata only enriches those placements;
it never decides whether a source image exists.
"""
from __future__ import annotations

from collections import defaultdict
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
    """Return deduplicated visual metadata that survived normalization."""
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
            "questionId":qid,"subject":subject,"role":role,
            "order":int(item.get("order") or ordinal),"visualId":vid,
            "visualType":str(item.get("visual_type") or item.get("type") or "unknown"),
            "title":title,"sourcePages":pages,"origin":origin,"metadata":item,
        })

    for key in QUESTION_VISUAL_KEYS:
        rows=question.get(key)
        if isinstance(rows,list):
            for i,row in enumerate(rows,1): add(row,"question",key,i)

    structured=question.get("structuredExplanation") or question.get("structured_explanation") or {}
    if isinstance(structured,dict):
        for key in EXPLANATION_VISUAL_KEYS:
            rows=structured.get(key)
            if isinstance(rows,list):
                for i,row in enumerate(rows,1): add(row,"explanation","structuredExplanation."+key,i)
        blocks=structured.get("blocks")
        if isinstance(blocks,list):
            visual_i=0
            for row in blocks:
                if isinstance(row,dict) and _looks_visual_block(row):
                    visual_i+=1;add(row,"explanation","structuredExplanation.blocks",visual_i)

    for key in ("visuals","figures","images"):
        rows=question.get(key)
        if isinstance(rows,list):
            for i,row in enumerate(rows,1): add(row,"explanation",key,i)

    dedup=[];seen=set()
    for row in found:
        if row["visualId"]:
            key=(row["role"],"id",row["visualId"])
        else:
            crop=row["metadata"].get("crop_norm") or row["metadata"].get("cropNorm") or []
            key=(row["role"],tuple(row["sourcePages"]),row["visualType"],row["title"],tuple(crop) if isinstance(crop,list) else str(crop))
        if key in seen: continue
        seen.add(key);dedup.append(row)
    for i,row in enumerate(dedup,1):
        token=row["visualId"] or f'{row["role"]}-{i}'
        row["id"]=f'{qid}:source-visual:{token}'
    return dedup


def question_page_owners(question):
    """Recover source page ownership even when visual metadata was dropped."""
    qid=str(question.get("id") or question.get("question_id") or "")
    subject=str(question.get("subject") or "")
    provenance=question.get("provenance") or {}
    source=question.get("source") or {}
    question_pages=(provenance.get("questionPages") or provenance.get("question_pages") or source.get("question_pages") or [])
    explanation_pages=(provenance.get("explanationPages") or provenance.get("explanation_pages") or source.get("explanation_pages") or [])
    rows=[]
    for role,pages in (("question",question_pages),("explanation",explanation_pages)):
        for page in pages or []:
            if isinstance(page,int) and page>0:
                rows.append({"questionId":qid,"subject":subject,"role":role,"page":page})
    return rows


def source_image_occurrences(audit, question_map, subject=None):
    """Enumerate every non-background PDF image placement on owned source pages.

    Multiple question/solution owners on one page are preserved as candidates;
    ambiguous ownership is review work, never a reason to make the image vanish.
    """
    owners=defaultdict(list)
    for q in question_map.values():
        if subject and q.get("subject")!=subject: continue
        for row in question_page_owners(q):
            key=(row["subject"],row["page"])
            if not any(x["questionId"]==row["questionId"] and x["role"]==row["role"] for x in owners[key]):
                owners[key].append(row)
    occurrences=[]
    for subj,source in audit.get("sources",{}).items():
        if subject and subj!=subject: continue
        for page_record in source.get("pages",[]):
            page=page_record.get("page")
            candidate_owners=owners.get((subj,page),[])
            if not candidate_owners: continue
            seen_placements=set()
            for image in page_record.get("images",[]):
                if image.get("pageBackgroundCandidate"): continue
                region=tuple(image.get("region") or [])
                placement=(image.get("xref"),region)
                if placement in seen_placements: continue
                seen_placements.add(placement)
                occurrences.append({
                    "id":f'{subj}:page:{page}:xref:{image.get("xref")}:'+','.join(map(str,region)),
                    "subject":subj,"page":page,"xref":image.get("xref"),
                    "region":list(region),"streamSha256":image.get("streamSha256"),
                    "width":image.get("width"),"height":image.get("height"),
                    "filter":image.get("filter"),"mask":image.get("mask"),
                    "candidateOwners":deepcopy(candidate_owners),
                })
    occurrences.sort(key=lambda r:(r["subject"],r["page"],r["xref"] or 0,tuple(r["region"])))
    return occurrences


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
    """Merge surviving metadata plus unambiguous PDF placements into staging."""
    bindings=list(audit.get("bindings",[]))
    seen_ids={b.get("id") for b in bindings}
    seen_visuals=set()
    for b in bindings:
        meta=b.get("metadata") or {}
        vid=_visual_id(meta) if isinstance(meta,dict) else ""
        role=_role(meta,"explanation") if isinstance(meta,dict) else "explanation"
        if vid: seen_visuals.add((b.get("questionId"),role,vid))

    for qid,q in question_map.items():
        subject=q.get("subject")
        source=audit.get("sources",{}).get(subject,{})
        for expected in source_visual_expectations(q):
            identity=(qid,expected["role"],expected["visualId"])
            if expected["visualId"] and identity in seen_visuals: continue
            if expected["id"] in seen_ids: continue
            metadata=deepcopy(expected["metadata"])
            metadata.setdefault("role",expected["role"]);metadata.setdefault("title",expected["title"])
            metadata["source_recorded_origin"]=expected["origin"]
            bindings.append({
                "id":expected["id"],"questionId":qid,"subject":subject,
                "metadata":metadata,"candidateImages":_candidate_images(source,expected["sourcePages"]),
                "status":"REVIEW_REQUIRED","reason":"Source-recorded visual requires explicit ownership, role, fidelity and readability review",
                "sourceRecorded":True,"sourcePages":expected["sourcePages"],"role":expected["role"],
                "order":expected["order"],"visualId":expected["visualId"],
            })
            seen_ids.add(expected["id"])
            if expected["visualId"]: seen_visuals.add(identity)

    # Metadata can be incomplete. Add PDF placements with one unambiguous owner
    # so bounded staging can still discover them. Ambiguous placements remain in
    # source_image_occurrences() and the coverage report until human/source review.
    for occurrence in source_image_occurrences(audit,question_map):
        owners=occurrence["candidateOwners"]
        if len(owners)!=1: continue
        owner=owners[0]
        oid='pdf-occurrence:'+occurrence['id']
        if oid in seen_ids: continue
        image={
            "page":occurrence["page"],"xref":occurrence["xref"],"region":occurrence["region"],
            "streamSha256":occurrence["streamSha256"],"width":occurrence["width"],"height":occurrence["height"],
            "filter":occurrence["filter"],"mask":occurrence["mask"],"pageBackgroundCandidate":False,
        }
        bindings.append({
            "id":oid,"questionId":owner["questionId"],"subject":occurrence["subject"],
            "metadata":{"role":owner["role"],"title":"Unaccounted source PDF image placement","source_recorded_origin":"pdf-page-provenance"},
            "candidateImages":[image],"status":"REVIEW_REQUIRED",
            "reason":"PDF image occurs on a canonical question/solution page and must be explicitly released, held or rejected",
            "sourceRecorded":False,"sourceOccurrence":True,"sourcePages":[occurrence["page"]],
            "role":owner["role"],"order":1,"visualId":"",
        })
        seen_ids.add(oid)
    return bindings
