#!/usr/bin/env python3
"""Report all hard learner-visible violations in active Marrow v2 overrides.

Unlike the fail-fast validator, this diagnostic accumulates every issue so legacy
partial overrides can be repaired as one finite batch. It is read-only with
respect to source and active overrides; only a derived report is written.
"""
from __future__ import annotations

import base64
import json
import re
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
V2 = DATA / "content_hygiene_overrides_v2"
OUT = DATA / "content_audit_effective" / "v2_validator_issues.json"
BANKS = {
    "Anatomy": "anatomy_ch001_063",
    "Biochemistry": "biochemistry_ch001_028",
    "Physiology": "physiology_ch001_043",
}
SERIALIZED = ("[object Object]", '{\"text\"', '{\"type\"', '\"content\":', "```")
BRAND_LINE = re.compile(r"(?im)^\s*(?:©?\s*MARROW|Sold by\s+@\w+)\s*$")


def load(prefix: str) -> dict:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    raw = zlib.decompress(base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in parts)))
    return json.loads(raw.decode("utf-8"))


def main() -> None:
    source_by_id = {
        str(q["id"]): q
        for prefix in BANKS.values()
        for q in load(prefix).get("questions", [])
    }
    issues: list[dict] = []
    checked = 0
    for path in sorted(V2.glob("**/*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for qid, override in (payload.get("questions") or {}).items():
            checked += 1
            source = source_by_id[qid]
            question = str(override.get("question", source.get("question", ""))).strip()
            explanation = str(override.get("explanation", source.get("explanation", ""))).strip()
            if "options" in override:
                options = [str(v).strip() for v in override["options"]]
                correct_answer = options[int(source["correctOption"]) - 1]
            else:
                options = [str(o.get("text", "")) for o in source.get("options", [])]
                correct_answer = str(source.get("correctAnswerText", ""))
            fields = [("question", question), ("explanation", explanation), ("correctAnswerText", correct_answer)]
            fields.extend((f"option_{chr(65+i)}", value) for i, value in enumerate(options))
            for field, value in fields:
                reasons = []
                if any(marker in value for marker in SERIALIZED):
                    reasons.append("serialized_or_code_marker")
                brand_matches = [m.group(0).strip() for m in BRAND_LINE.finditer(value)]
                if brand_matches:
                    reasons.append("standalone_source_brand_line")
                if not reasons:
                    continue
                prov = source.get("provenance") or {}
                issues.append({
                    "id": qid,
                    "subject": source.get("subject"),
                    "chapterId": str(source.get("chapterId")),
                    "chapter": source.get("chapter"),
                    "questionNumber": source.get("questionNumber"),
                    "field": field,
                    "reasons": reasons,
                    "brandMatches": brand_matches,
                    "questionPages": prov.get("questionPages") or [],
                    "explanationPages": prov.get("explanationPages") or [],
                    "activeOverrideFile": str(path.relative_to(ROOT)),
                    "fieldPreview": value[:600],
                })
    counts = Counter(i["field"] for i in issues)
    payload = {
        "schemaVersion": 1,
        "derivedOnly": True,
        "activeOverridesChecked": checked,
        "issueCount": len(issues),
        "questionCount": len({i['id'] for i in issues}),
        "byField": dict(sorted(counts.items())),
        "issues": sorted(issues, key=lambda i: (str(i["subject"]), int(i["chapterId"]), int(i.get("questionNumber") or 0), i["field"])),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MARROW_V2_VALIDATOR_ISSUE_REPORT_OK", json.dumps({k: payload[k] for k in ("activeOverridesChecked", "issueCount", "questionCount", "byField")}, sort_keys=True))


if __name__ == "__main__":
    main()
