#!/usr/bin/env python3
"""Install conservative learner-facing Marrow text sanitation and source-footer cleanup."""

from pathlib import Path

HTML = Path("app/src/main/assets/index.html")


def context(source: str, needle: str, radius: int = 550) -> str:
    index = source.find(needle)
    if index < 0:
        return "<not found>"
    return source[max(0, index-radius):min(len(source), index+len(needle)+radius)].replace("\n", "\\n")


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    probes = [
        "MARROW_DATA",
        "MARROW_BY_SUBJECT",
        "BANKS_BY_SUBJECT",
        "activeBank",
        "bank==='Marrow'",
        'bank==="Marrow"',
        "nkAllBankQuestions",
        "marrow__PHYS",
        "marrow__BIO",
        "marrow__ANAT",
        "sourceQuestionId",
    ]
    counts = {probe: source.count(probe) for probe in probes}
    interesting = [probe for probe in probes if counts[probe]]
    details = " | ".join(f"{probe}={counts[probe]} ctx={context(source, probe)}" for probe in interesting[:6])
    raise SystemExit(f"CURRENT_MARROW_RUNTIME_PROBES counts={counts} :: {details}")


if __name__ == "__main__":
    main()
