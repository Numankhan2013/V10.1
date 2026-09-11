#!/usr/bin/env python3
"""Measure source-recorded Marrow visual coverage against the image registry.

A visual is complete only when every source-recorded question/explanation visual
is accounted for by a registry binding.  PASS/SOURCE_LIMITED means released;
REVIEW_REQUIRED or REJECTED remains accounted but not learner-facing.  Missing
registry coverage is UNACCOUNTED and must prevent subject-level completion.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from marrow_images import DATA, ROOT, RELEASE_STATUSES, questions
from marrow_visual_inventory import source_visual_expectations


def binding_rows(registry):
    rows=[]
    for asset in registry.get("assets",[]):
        asset_status=asset.get("status","REVIEW_REQUIRED")
        asset_page=(asset.get("source") or {}).get("page")
        for binding in asset.get("bindings",[]):
            source=binding.get("source") or {}
            rows.append({
                "questionId":binding.get("questionId"),
                "role":binding.get("role","explanation"),
                "page":source.get("page",asset_page),
                "assetId":asset.get("id"),
                "assetStatus":asset_status,
                "bindingStatus":binding.get("status",asset_status),
                "notes":((binding.get("qa") or {}).get("notes") or (asset.get("qa") or {}).get("notes") or ""),
            })
    return rows


def classify(expected, rows):
    candidates=[r for r in rows if r["questionId"]==expected["questionId"] and r["role"]==expected["role"]]
    pages=set(expected["sourcePages"])
    if pages:
        page_matches=[r for r in candidates if r.get("page") in pages]
        if page_matches:
            candidates=page_matches
        elif candidates:
            return "UNACCOUNTED",[]
    if not candidates:
        return "UNACCOUNTED",[]
    released=[r for r in candidates if r["assetStatus"] in RELEASE_STATUSES and r["bindingStatus"] in RELEASE_STATUSES]
    if released:
        return "RELEASED",released
    rejected=[r for r in candidates if r["bindingStatus"]=="REJECTED" or r["assetStatus"]=="REJECTED"]
    if rejected:
        return "REJECTED",rejected
    return "REVIEW_REQUIRED",candidates


def build_report(subject=None):
    qmap=questions()
    registry=json.loads((DATA/"images/registry.json").read_text())
    rows=binding_rows(registry)
    expected=[]
    for q in qmap.values():
        if subject and q.get("subject")!=subject:
            continue
        expected.extend(source_visual_expectations(q))
    results=[]
    for item in expected:
        status,matches=classify(item,rows)
        results.append({
            "id":item["id"],"questionId":item["questionId"],"subject":item["subject"],
            "role":item["role"],"order":item["order"],"visualId":item["visualId"],
            "visualType":item["visualType"],"title":item["title"],"sourcePages":item["sourcePages"],
            "origin":item["origin"],"coverageStatus":status,
            "registryMatches":[{"assetId":m["assetId"],"assetStatus":m["assetStatus"],"bindingStatus":m["bindingStatus"],"page":m["page"]} for m in matches],
        })
    by_subject={}
    for name in sorted({r["subject"] for r in results} | ({subject} if subject else set())):
        subset=[r for r in results if r["subject"]==name]
        counts=Counter(r["coverageStatus"] for r in subset)
        roles=Counter(r["role"] for r in subset)
        by_subject[name]={
            "expectedVisuals":len(subset),
            "questionVisuals":roles.get("question",0),
            "explanationVisuals":roles.get("explanation",0),
            "released":counts.get("RELEASED",0),
            "reviewRequired":counts.get("REVIEW_REQUIRED",0),
            "rejected":counts.get("REJECTED",0),
            "unaccounted":counts.get("UNACCOUNTED",0),
            "complete":counts.get("UNACCOUNTED",0)==0,
        }
    return {"schemaVersion":1,"subject":subject,"summary":by_subject,"visuals":results}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--subject",choices=("Anatomy","Biochemistry","Physiology"))
    parser.add_argument("--output",type=Path,default=ROOT/"build/marrow-images/coverage.json")
    parser.add_argument("--check-complete",action="store_true",help="Fail if any source-recorded visual is unaccounted for")
    args=parser.parse_args()
    report=build_report(args.subject)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report["summary"],indent=2))
    if args.check_complete:
        missing=sum(v["unaccounted"] for v in report["summary"].values())
        if missing:
            raise SystemExit(f"MARROW_IMAGE_COVERAGE_INCOMPLETE unaccounted={missing}")
        print("MARROW_IMAGE_COVERAGE_COMPLETE")

if __name__=="__main__":
    main()
