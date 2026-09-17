#!/usr/bin/env python3
"""Read-only Phase 3 structural triage using the current shared JS normalizer."""
from __future__ import annotations

import argparse
import base64
import contextlib
import copy
import hashlib
import io
import json
import re
import subprocess
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NODE = r'''
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const context={window:{},SUBJECTS:[],esc:value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')};
vm.createContext(context);
for(const file of input.prepFiles)vm.runInContext(fs.readFileSync(file,'utf8'),context,{filename:file});
vm.runInContext(input.hygiene,context);
vm.runInContext(input.core,context);
const prep=[{subject:'Biochemistry',questions:context.window.QBANK_DATA.questions},...context.window.SUBJECT_QBANK_DATA.subjects];
const sourcePrep=prep.flatMap(record=>record.questions.map(q=>({...q,subject:record.subject,bank:'PrepLadder'})));
const clone=value=>JSON.parse(JSON.stringify(value));
const compact=value=>String(value??'').replace(/\s+/g,' ').trim();
const mapping=text=>[...compact(text).matchAll(/(?=\b([A-Ha-h]|[1-9]|viii|vii|vi|iv|iii|ii|i|v)\s*[-:→=]\s*\(?([A-Ha-h]|[1-9]|viii|vii|vi|iv|iii|ii|i|v)\)?\b)/gi)].map(hit=>[hit[1],hit[2]]);
const markers=text=>[...String(text).matchAll(/(?:^|\s|\|)([1-9]|[A-Ha-h]|viii|vii|vi|iv|iii|ii|i|v)[.)]\s*/g)].map(hit=>({label:hit[1],offset:hit.index,end:hit.index+hit[0].length}));
const family=label=>/^\d+$/.test(label)?'number':/^(i|ii|iii|iv|v|vi|vii|viii)$/i.test(label)?'roman':'letter';
const key=label=>family(label)+':'+label.toLowerCase();
function audit(raw,learner){
 const q=clone(learner);delete q.__nkQuestionPresentation;
 context.nkSanitizeMarrowQuestion(q);
 const before=clone(q),p=context.nkQuestionPresentationFor(q);
 const presentationOnly=context.nkQuestionPresentationFor(clone(learner));
 const matching=context.nkQuestionMatchingSource(before,p),continuation=context.nkQuestionContinuationSource(before,p);
 const generic=context.nkQuestionMatchingTable(matching||continuation,Boolean(continuation));
 const override=context.nkQuestionMatchingOverride(before);
 const completeOverride=typeof context.nkQuestionCompleteSourceOverride==='function'?context.nkQuestionCompleteSourceOverride(before,p):null;
 const appliedOverride=Boolean(p.table&&(completeOverride&&completeOverride.valid!==false||(!generic||generic.valid===false)&&override));
 const stem=String(before.question||''),rawStem=String(raw.question||'');
 const texts=p.options.map(o=>String(o.text||'')),maps=texts.map(mapping);
 const hits=markers(stem),rawHits=markers(rawStem);
 const signals=[];
 const add=(name,condition)=>{if(condition)signals.push(name);};
 add('literal-match',/\bmatch(?:ing|ed)?\b/i.test(stem+' '+rawStem));
 add('list-column',/\b(?:list|column)\s*[-:]?\s*(?:[AB12]|II?|one|two)\b/i.test(stem+' '+rawStem));
 add('letter-number-mapping',maps.some(pairs=>pairs.filter(pair=>pair.some(label=>family(label)==='number')&&pair.some(label=>family(label)==='letter')).length>=2));
 add('letter-roman-mapping',maps.some(pairs=>pairs.filter(pair=>pair.some(label=>family(label)==='roman')&&pair.some(label=>family(label)==='letter')).length>=2));
 add('row-selection',texts.length>=2&&texts.every(text=>/^\s*(?:[1-9]|[A-H]|i{1,3}|iv|v)\s*[.)]?\s*$/.test(text)));
 add('structured-combination',texts.filter(text=>/^\s*(?:[1-9]|[A-Ha-h]|iv|iii|ii|i|v)(?:\s*(?:,|&|and|[-+→])\s*(?:[1-9]|[A-Ha-h]|iv|iii|ii|i|v))+(?:\s+(?:only|are correct|are incorrect))?\s*\.?\s*$/i.test(text)).length>=2);
 add('enumerated-list',hits.length>=2||rawHits.length>=2);
 add('table-markup',/<table\b|\|[^\n]+\|[^\n]*\|/i.test(stem+' '+rawStem));
 add('row-table-wording',/\b(?:row|combination|statements?|pairs?)\b/i.test(stem)&&(/\b(?:table|columns?|following)\b/i.test(stem)||hits.length>=2));
 add('presentation-override',Boolean(override)||Boolean(completeOverride&&completeOverride.valid!==false));
 add('display-override',input.displayOverrideIds.includes(raw.id));
 add('source-reconstruction',raw.reviewStatus==='resolved_reconstruction');
 add('option-normalization',p.repaired||raw.options?.length!==p.options.length);
 add('invalid-answer-contract',!p.valid);
 add('semantic-table',Boolean(p.table));
 const selected=signals.length>0;
 if(!selected)return {id:raw.id,bank:raw.bank,subject:raw.subject,candidate:false,valid:p.valid};
 const source=matching||continuation||stem;
 const sourceHits=markers(source);
 const sourceCells=sourceHits.map((hit,index)=>({label:hit.label,value:compact(source.slice(hit.end,sourceHits[index+1]?.offset??source.length))}));
 const counts={};for(const cell of sourceCells){const k=key(cell.label);counts[k]=(counts[k]||0)+1;}
 const duplicateLabels=Object.entries(counts).filter(([,n])=>n>1).map(([label,count])=>({label,count}));
 const rows=p.table?.rows||[];
 const cells=rows.flat();
 const meaningful=cells.filter(cell=>cell&&/[\p{L}\p{N}]/u.test(String(cell.value||''))).length;
 const empty=cells.filter(cell=>cell&&!compact(cell.value)).length;
 const dash=cells.filter(cell=>!cell||/^[-–—−]+$/.test(compact(cell.value))).length;
 const sourceEmpty=sourceCells.filter(cell=>!cell.value||/^[-–—−]+$/.test(cell.value));
 const duplicateRows=rows.map((row,index)=>({index: index+1,text:JSON.stringify(row)})).filter((row,index,all)=>all.findIndex(other=>other.text===row.text)<index).map(row=>row.index);
 const groups=p.table?.groups||[];
 const labels=groups.flatMap(group=>group.map(cell=>cell.label||(/^(?:[1-9]|[A-Ha-h]|i{1,3}|iv|v)$/.test(compact(cell.value))?compact(cell.value):'')).filter(Boolean));
 const labelSet=new Set(labels.map(key));
 const coverage=maps.map((pairs,index)=>({option:index+1,pairs,missingFromRenderedGroups:[...new Set(pairs.flat().filter(label=>!labelSet.has(key(label))))],referencedLabels:[...new Set(pairs.flat())]}));
 const strong=signals.some(signal=>['list-column','letter-number-mapping','letter-roman-mapping','row-selection','structured-combination','enumerated-list','table-markup'].includes(signal))||/\b(?:row|table|columns?)\b/i.test(stem)&&signals.includes('row-table-wording')||/^\s*match\b/i.test(stem);
 const issues=[];
 if(!p.valid)issues.push('normalizer-fail-closed');
 if(strong&&!p.table)issues.push('structured-candidate-without-semantic-table');
 if(empty)issues.push('empty-rendered-cell');
 if(dash)issues.push(appliedOverride?'override-padding-dash-source-review':'missing-or-dash-rendered-cell');
 if(duplicateRows.length)issues.push('duplicate-rendered-rows');
 if(p.table&&coverage.some(item=>item.missingFromRenderedGroups.length))issues.push('answer-mapping-labels-not-in-rendered-groups');
 if(sourceEmpty.length)issues.push('empty-or-truncated-source-marker-cell');
 const cellChoiceOverlap=texts.flatMap((text,index)=>cells.some(cell=>cell&&compact(cell.value).length>4&&compact(cell.value)===compact(text))?[index+1]:[]);
 if(cellChoiceOverlap.length&&maps.some(pairs=>pairs.length>=2))issues.push('source-cell-exposed-as-choice-suspected');
 const consumed=p.supporting.flatMap(option=>mapping(option.text).filter(pair=>family(pair[0])!==family(pair[1])).length>=2?[option]:[]);
 if(consumed.length)issues.push('mapping-choice-consumed-as-support-suspected');
 const ordinary=!strong&&!p.table&&p.valid&&!signals.includes('source-reconstruction');
 const classification=!p.valid||strong&&!p.table||issues.some(issue=>['empty-rendered-cell','missing-or-dash-rendered-cell','duplicate-rendered-rows','answer-mapping-labels-not-in-rendered-groups','source-cell-exposed-as-choice-suspected','mapping-choice-consumed-as-support-suspected'].includes(issue))?'incomplete-unsafe':appliedOverride?'source-backed-override':p.table?'complete-generic-reconstruction':ordinary?'false-positive-ordinary-prose':'incomplete-unsafe';
 const unresolved=classification==='incomplete-unsafe'||dash>0||sourceEmpty.length>0||signals.includes('source-reconstruction');
 const demonstratedUnsafe=issues.some(issue=>['empty-rendered-cell','missing-or-dash-rendered-cell','duplicate-rendered-rows','answer-mapping-labels-not-in-rendered-groups'].includes(issue));
 return {hygieneChangedStem:before.question!==learner.question,presentationOnlyValid:presentationOnly.valid,presentationOnlyTable:Boolean(presentationOnly.table),hygienePresentationValidityDelta:presentationOnly.valid!==p.valid,demonstratedUnsafeStillAnswerable:demonstratedUnsafe&&p.valid,suspectedUnsafeStillAnswerable:classification==='incomplete-unsafe'&&p.valid&&!demonstratedUnsafe,id:raw.id,bank:raw.bank,subject:raw.subject,candidate:true,families:signals,classification,adjudication:unresolved?'SOURCE_REVIEW_REQUIRED':'STRUCTURAL_TRIAGE_ONLY',unresolved,unsafeStillAnswerable:classification==='incomplete-unsafe'&&p.valid,answerableByCurrentNormalizer:p.valid,failClosed:!p.valid,issues,sourcePage:raw.sourcePage??null,sourceQuestionId:raw.sourceQuestionId??null,reviewStatus:raw.reviewStatus??null,rawQuestion:rawStem,normalizedQuestion:stem,rawOptions:raw.options,normalizedOptions:p.options,correctOption:raw.correctOption,normalizedCorrectOption:q.correctOption,rawOptionCount:raw.options?.length||0,normalizedOptionCount:p.options.length,optionRuns:context.nkQuestionOptionRuns(before.options).map(run=>({indexes:run.map(item=>item.index),score:context.nkQuestionChoiceScore(run,q.correctOption)})),supporting:p.supporting,table:p.table,genericRejected:generic?.valid===false,overrideAvailable:Boolean(override),overrideApplied:appliedOverride,displayOverrideApplied:input.displayOverrideIds.includes(raw.id),renderedCells:{total:cells.length,meaningful,empty,dash,groupLengths:groups.map(group=>group.length),unequalGroups:new Set(groups.map(group=>group.length)).size>1,duplicateRows},sourceMarkers:{cells:sourceCells,duplicateLabels,emptyOrTruncatedCells:sourceEmpty,truncatedFinalRowSuspected:sourceEmpty.some(cell=>cell===sourceCells[sourceCells.length-1])},answerMappingCoverage:coverage,sourceCellChoiceOverlap:cellChoiceOverlap,mappingChoicesConsumedAsSupport:consumed};
}
const assert=require('assert');
const fixture=(question,options)=>({id:'audit-fixture',bank:'PrepLadder',subject:'Fixture',question,options:options.map((text,index)=>({letter:'ABCD'[index],text})),correctOption:1});
for(const [question,options,expected] of [
 ['Which of the following statements is correct?',['First statement','Second statement','Third statement','Fourth statement'],'false-positive-ordinary-prose'],
 ['Match: 1. Alpha a. One 2. Beta b. Two',['1-a, 2-b','1-b, 2-a','1-a, 2-a','1-b, 2-b'],'complete-generic-reconstruction'],
 ['Match: 1. Alpha a. One 2. Beta b. —',['1-a, 2-b','1-b, 2-a','1-a, 2-a','1-b, 2-b'],'incomplete-unsafe'],
 ['Column A Column B',['A-1, B-2','A-2, B-1','A-1, B-1','A-2, B-2'],'incomplete-unsafe']
]){const q=fixture(question,options);assert.equal(audit(q,q).classification,expected);}
assert.deepEqual(mapping('1-A-i, 2-B-ii'),[['1','A'],['A','i'],['2','B'],['B','ii']]);
const raw=[...sourcePrep,...input.rawMarrow];
const learners=new Map([...sourcePrep,...input.marrow].map(q=>[q.id,q]));
const result=raw.map(q=>audit(q,learners.get(q.id)));
process.stdout.write(JSON.stringify({records:result,prepRaw:sourcePrep}));
'''


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def packed(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_marrow() -> tuple[list, dict]:
    records, hashes = [], {}
    for prefix in ("anatomy_ch001_063", "biochemistry_ch001_028", "physiology_ch001_043"):
        parent = ROOT / "data/marrow"
        manifest = json.loads((parent / f"{prefix}_manifest.json").read_text())
        parts = sorted(parent.glob(f"{prefix}.zlib.b64.part*"))
        encoded = "".join(path.read_text().strip() for path in parts)
        compressed = base64.b64decode(encoded, validate=True)
        raw = zlib.decompress(compressed)
        for actual, expected in ((len(parts), manifest["parts"]), (len(encoded), manifest["base64_chars"]), (len(compressed), manifest["compressed_bytes"]), (len(raw), manifest["raw_bytes"]), (sha(compressed), manifest["compressed_sha256"]), (sha(raw), manifest["raw_sha256"])):
            if actual != expected:
                raise ValueError(f"Manifest mismatch: {prefix}: {actual} != {expected}")
        record = json.loads(raw)
        if len(record["questions"]) != manifest["questions"]:
            raise ValueError(f"Question count mismatch: {prefix}")
        records.append(record)
        hashes[prefix] = sha(raw)
    return records, hashes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-dir", type=Path, help="Optional generated assets containing index.html and both PrepLadder data scripts; never executes browser code")
    parser.add_argument("--output", type=Path, default=ROOT / "build/question-fidelity")
    parser.add_argument("--check", action="store_true", help="Compare deterministic reports without writing")
    args = parser.parse_args()
    records, hashes = load_marrow()
    raw_marrow = [copy.deepcopy(q) for record in records for q in record["questions"]]
    owner_path = ROOT / "tools/apply_marrow_bank_pilot.py"
    owner = owner_path.read_text()
    start = owner.index('CONTENT_OVERRIDES_PATH=')
    end = owner.index('expanded_ids=', start)
    namespace = {"DATA": ROOT / "data/marrow", "json": json, "hashlib": hashlib, "expanded_records": records}
    with contextlib.redirect_stdout(io.StringIO()) as captured:
        exec(compile(owner[start:end], str(owner_path), "exec"), namespace)
    marrow = [q for record in records for q in record["questions"]]
    generated = None
    if args.generated_dir:
        html_path = args.generated_dir / "index.html"
        html = html_path.read_text()
        matches = re.findall(r"const MARROW_DATA = (.*?);\n", html)
        if len(matches) != 1:
            raise ValueError("Expected one generated MARROW_DATA envelope")
        envelope = json.loads(matches[0])
        marrow = [q for record in envelope.get("records", [envelope]) for q in record["questions"]]
        generated = {"htmlSha256": sha(html_path.read_bytes()), "envelopeComparison": "exact-stem-options-answer", "differentIds": []}
        expected = {q["id"]: q for record in records for q in record["questions"]}
        for q in marrow:
            if q["id"] not in expected or any(q.get(key) != expected[q["id"]].get(key) for key in ("question", "options", "correctOption")):
                generated["differentIds"].append(q["id"])
        if set(expected) != {q["id"] for q in marrow}:
            raise ValueError("Generated Marrow IDs differ from canonical 2711 scope")
    assets = args.generated_dir or ROOT / "app/src/main/assets"
    files = [assets / "qbank_data.js", assets / "subjects_qbank_data.js"]
    core_paths = [ROOT / "tools/question_presentation_core.js", ROOT / "tools/question_content_hygiene_core.js"]
    tracked_inputs = files + core_paths + [owner_path, ROOT / "data/marrow/content_hygiene_overrides_v1.json", Path(__file__)]
    input_hashes = {str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path): sha(path.read_bytes()) for path in tracked_inputs}
    payload = {"prepFiles": [str(path) for path in files], "core": core_paths[0].read_text(), "hygiene": core_paths[1].read_text(), "rawMarrow": raw_marrow, "marrow": marrow, "displayOverrideIds": sorted(namespace["override_questions"])}
    result = subprocess.run(["node", "-e", NODE], input=json.dumps(payload), text=True, capture_output=True, check=True, cwd=ROOT)
    evaluated = json.loads(result.stdout)
    all_rows = evaluated["records"]
    if Counter(row["bank"] for row in all_rows) != {"PrepLadder": 2686, "Marrow": 2711} or len({row["id"] for row in all_rows}) != 5397:
        raise ValueError("Full 5397-question unique learner scope required")
    raw_by_id = {q["id"]: q for q in evaluated["prepRaw"] + raw_marrow}
    for row in all_rows:
        q = raw_by_id[row["id"]]
        row["canonicalSourceFingerprint"] = sha(packed({key: q.get(key) for key in ("id", "question", "options", "correctOption", "sourcePage", "sourceQuestionId")}))
    candidates = [row for row in all_rows if row["candidate"]]
    summary = {}
    for bank in ("PrepLadder", "Marrow"):
        scope = [row for row in all_rows if row["bank"] == bank]
        subset = [row for row in candidates if row["bank"] == bank]
        summary[bank] = {"questions": len(scope), "candidates": len(subset), "classifications": dict(sorted(Counter(row["classification"] for row in subset).items())), "families": dict(sorted(Counter(family for row in subset for family in row["families"]).items())), "failClosed": sum(row["failClosed"] for row in subset), "unsafeStillAnswerable": sum(row["unsafeStillAnswerable"] for row in subset), "sourceReviewRequired": sum(row["unresolved"] for row in subset), "newlyRepairedByAudit": 0, "demonstratedUnsafeStillAnswerable": sum(row["demonstratedUnsafeStillAnswerable"] for row in subset), "suspectedUnsafeStillAnswerable": sum(row["suspectedUnsafeStillAnswerable"] for row in subset)}
    limitations = ["Phase 3 remains OPEN: automatic structural triage is not authoritative-source adjudication. No medical/scientific correctness audit or repairs performed.", "All 5397 IDs scanned. Candidate retrieval is intentionally broad and heuristic; absence of a signal is not proof of source fidelity. Enumerated lists and row-wording hits include ordinary prose false positives pending review.", "Default Marrow path uses manifest-verified canonical shards, the exact bounded display-override block from apply_marrow_bank_pilot.py, current nkSanitizeMarrowQuestion and current nkQuestionPresentationFor. This is NOT raw Marrow claimed runtime-equivalent, nor a full generated pipeline/browser execution.", "Optional --generated-dir reads the actual MARROW_DATA envelope and PrepLadder scripts, comparing canonical stem/options/answer. It still executes CURRENT source normalization, not the artifact's entire startup or rendered UI. HTML hash alone does not certify build provenance.", "Answerable means presentation.valid in current normalization, not verified clickable UI. Unsafe includes suspected/unadjudicated structured candidates; separate evidence is listed per ID.", "Null table metrics are zero/not observed, not a clean source-table verdict. Marker diagnostics can overcount prose/option labels; repeated labels are duplicate-block signals, not proof of corrupt rows. Prefix-only truncation without a label cannot be proven automatically.", "Unequal source-backed groups can be legitimate many-to-one/category/image structures. Padding dashes are reported for review, not automatically condemned as paired-data loss. Image-owned labels require separate generated/source verification.", "Mapping coverage compares explicit dash/colon/arrow/equal label pairs only. Other shorthand/row/combination formats are retained in the inventory for manual adjudication; none are inferred medically.", "No core, existing test/browser, canonical data, or project-memory files are changed. Parent owns source repairs and representative regression additions. Browser/PDF/package checks remain GitHub-only."]
    report = {"schemaVersion": 1, "phase": 3, "status": "OPEN_SOURCE_REVIEW_REQUIRED", "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(), "inputSha256": input_hashes, "canonicalShardSha256": hashes, "displayOverrideOutput": captured.getvalue().strip(), "generatedEvidence": generated, "fingerprintContract": "SHA256 UTF-8 sorted compact JSON of id/question/options/correctOption/sourcePage/sourceQuestionId; source before hygiene/presentation mutations", "summary": summary, "limitations": limitations, "unresolvedIds": [row["id"] for row in candidates if row["unresolved"]], "unsafeStillAnswerableIds": [row["id"] for row in candidates if row["unsafeStillAnswerable"]], "candidates": candidates, "scopeInventory": [{key: row[key] for key in ("id", "bank", "subject", "candidate", "canonicalSourceFingerprint")} for row in all_rows]}
    lines = ["# Phase 3 question-structure audit", "", "**OPEN — source review/adjudication required; not Phase 3 complete.**", "", f"Input HEAD: `{report['head']}`; branch: `{report['branch']}`.", "", "## Counts", "", "```json", json.dumps(summary, indent=2), "```", "", "## Scope and limitations", ""]
    lines.extend(f"- {limitation}" for limitation in limitations)
    lines += ["", "## Reproduce", "", "```sh", "python3 tools/audit_question_structure.py", "python3 tools/audit_question_structure.py --check", "python3 tools/audit_question_structure.py --generated-dir build/web --output build/question-fidelity/generated", "```", "", "The generated command requires a current GitHub-generated artifact. It does not launch a browser.", "", "## Unresolved IDs", "", ", ".join(f"`{value}`" for value in report["unresolvedIds"]), "", "## Unsafe/suspected candidates still answerable by source normalizer", "", ", ".join(f"`{value}`" for value in report["unsafeStillAnswerableIds"]), "", "## Detailed candidate inventory", ""]
    for row in candidates:
        lines += [f"### {row['id']} — {row['classification']}", "", f"- Bank/subject: {row['bank']} / {row['subject']}; source page: {row['sourcePage']}; status: {row['adjudication']}.", f"- Families: {', '.join(row['families'])}.", f"- Fingerprint: `{row['canonicalSourceFingerprint']}`.", f"- Choices raw → normalized: {row['rawOptionCount']} → {row['normalizedOptionCount']}; canonical correctOption: {row['correctOption']}; fail closed: {row['failClosed']}; unsafe still answerable: {row['unsafeStillAnswerable']}.", f"- Issues: {', '.join(row['issues']) or 'No automated structural issue observed; source not adjudicated.'}", "", "```json", json.dumps({key: row[key] for key in ("rawQuestion", "normalizedQuestion", "rawOptions", "normalizedOptions", "supporting", "table", "renderedCells", "sourceMarkers", "answerMappingCoverage", "optionRuns")}, ensure_ascii=False, indent=2), "```", ""]
    output = {"structure-audit.json": json.dumps(report, ensure_ascii=False, indent=2) + "\n", "structure-audit.md": "\n".join(lines) + "\n"}
    if any(sha(path.read_bytes()) != input_hashes[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)] for path in tracked_inputs):
        raise ValueError("Inputs changed during audit; rerun after parent edit settles")
    if args.check:
        for name, content in output.items():
            if (args.output / name).read_text() != content:
                raise SystemExit(f"AUDIT_REPORT_STALE {name}")
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, content in output.items():
            (args.output / name).write_text(content)
    print("QUESTION_STRUCTURE_AUDIT_OK " + json.dumps(summary, sort_keys=True))
    print(f"REPORTS {args.output}/structure-audit.json {args.output}/structure-audit.md phase3=OPEN")


if __name__ == "__main__":
    main()
