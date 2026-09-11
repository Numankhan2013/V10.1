#!/usr/bin/env python3
"""Measure Marrow image coverage against the authoritative PDF.

Subject-level completion is placement-based, not registry-count based. Every
non-background PDF image placement that occurs on a canonical question or
explanation page must be explicitly accounted for. A placement may be released,
held for review, or rejected with evidence; an unaccounted placement prevents a
subject from being called image-complete.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from marrow_images import DATA, ROOT, RELEASE_STATUSES, questions
from marrow_visual_inventory import source_image_occurrences, source_visual_expectations


def _region(value):
    return tuple(round(float(x),3) for x in (value or []))


def registry_rows(registry):
    rows=[]
    for asset in registry.get("assets",[]):
        asset_status=asset.get("status","REVIEW_REQUIRED")
        asset_source=asset.get("source") or {}
        for binding in asset.get("bindings",[]):
            binding_source=binding.get("source") or asset_source
            binding_status=binding.get("status",asset_status)
            rows.append({
                "subject":asset.get("subject"),"questionId":binding.get("questionId"),
                "role":binding.get("role","explanation"),"page":binding_source.get("page"),
                "xref":binding_source.get("xref"),"region":_region(binding_source.get("region")),
                "assetId":asset.get("id"),"assetStatus":asset_status,"bindingStatus":binding_status,
                "notes":((binding.get("qa") or {}).get("notes") or (asset.get("qa") or {}).get("notes") or ""),
            })
    return rows


def classify_occurrence(occurrence, rows):
    owner_keys={(o["questionId"],o["role"]) for o in occurrence.get("candidateOwners",[])}
    region=_region(occurrence.get("region"))
    matches=[r for r in rows if r["subject"]==occurrence["subject"] and
             r.get("page")==occurrence.get("page") and r.get("xref")==occurrence.get("xref") and
             r.get("region")==region and (not owner_keys or (r["questionId"],r["role"]) in owner_keys)]
    if not matches:
        return "UNACCOUNTED",[]
    released=[r for r in matches if r["assetStatus"] in RELEASE_STATUSES and r["bindingStatus"] in RELEASE_STATUSES]
    if released: return "RELEASED",released
    rejected=[r for r in matches if r["bindingStatus"]=="REJECTED" or r["assetStatus"]=="REJECTED"]
    if rejected: return "REJECTED",rejected
    return "REVIEW_REQUIRED",matches


def classify_metadata(expected, rows):
    candidates=[r for r in rows if r["questionId"]==expected["questionId"] and r["role"]==expected["role"]]
    pages=set(expected["sourcePages"])
    if pages:
        candidates=[r for r in candidates if r.get("page") in pages]
    if not candidates: return "UNACCOUNTED",[]
    released=[r for r in candidates if r["assetStatus"] in RELEASE_STATUSES and r["bindingStatus"] in RELEASE_STATUSES]
    if released:return "RELEASED",released
    rejected=[r for r in candidates if r["bindingStatus"]=="REJECTED" or r["assetStatus"]=="REJECTED"]
    if rejected:return "REJECTED",rejected
    return "REVIEW_REQUIRED",candidates


def build_report(subject=None):
    qmap=questions()
    registry=json.loads((DATA/"images/registry.json").read_text())
    audit_path=ROOT/"build/marrow-images/audit.json"
    if not audit_path.exists():
        raise SystemExit("Run `python3 tools/marrow_images.py audit` before coverage.")
    audit=json.loads(audit_path.read_text())
    rows=registry_rows(registry)

    occurrences=source_image_occurrences(audit,qmap,subject)
    occurrence_results=[]
    for occurrence in occurrences:
        status,matches=classify_occurrence(occurrence,rows)
        occurrence_results.append({**occurrence,"coverageStatus":status,
            "registryMatches":[{"assetId":m["assetId"],"questionId":m["questionId"],"role":m["role"],
                                "assetStatus":m["assetStatus"],"bindingStatus":m["bindingStatus"]} for m in matches]})

    metadata=[]
    for q in qmap.values():
        if subject and q.get("subject")!=subject:continue
        metadata.extend(source_visual_expectations(q))
    metadata_results=[]
    for item in metadata:
        status,matches=classify_metadata(item,rows)
        metadata_results.append({
            "id":item["id"],"questionId":item["questionId"],"subject":item["subject"],"role":item["role"],
            "visualId":item["visualId"],"visualType":item["visualType"],"title":item["title"],
            "sourcePages":item["sourcePages"],"origin":item["origin"],"coverageStatus":status,
            "registryMatches":[{"assetId":m["assetId"],"assetStatus":m["assetStatus"],"bindingStatus":m["bindingStatus"]} for m in matches],
        })

    names=sorted({r["subject"] for r in occurrence_results} | ({subject} if subject else set()))
    summary={}
    for name in names:
        subset=[r for r in occurrence_results if r["subject"]==name]
        counts=Counter(r["coverageStatus"] for r in subset)
        meta=[r for r in metadata_results if r["subject"]==name]
        meta_counts=Counter(r["coverageStatus"] for r in meta)
        summary[name]={
            "sourceImagePlacements":len(subset),
            "uniqueSourceImageStreams":len({r["streamSha256"] for r in subset}),
            "releasedPlacements":counts.get("RELEASED",0),
            "reviewRequiredPlacements":counts.get("REVIEW_REQUIRED",0),
            "rejectedPlacements":counts.get("REJECTED",0),
            "unaccountedPlacements":counts.get("UNACCOUNTED",0),
            "metadataVisualsRetained":len(meta),
            "metadataVisualsUnaccounted":meta_counts.get("UNACCOUNTED",0),
            "complete":counts.get("UNACCOUNTED",0)==0,
        }
    return {"schemaVersion":2,"subject":subject,"summary":summary,
            "sourceImagePlacements":occurrence_results,"retainedMetadataVisuals":metadata_results}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--subject",choices=("Anatomy","Biochemistry","Physiology"))
    parser.add_argument("--output",type=Path,default=ROOT/"build/marrow-images/coverage.json")
    parser.add_argument("--check-complete",action="store_true",help="Fail if any source PDF image placement is unaccounted for")
    args=parser.parse_args()
    report=build_report(args.subject)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report["summary"],indent=2))
    if args.check_complete:
        missing=sum(v["unaccountedPlacements"] for v in report["summary"].values())
        if missing:
            raise SystemExit(f"MARROW_IMAGE_COVERAGE_INCOMPLETE unaccounted_placements={missing}")
        print("MARROW_IMAGE_COVERAGE_COMPLETE")

if __name__=="__main__":main()
