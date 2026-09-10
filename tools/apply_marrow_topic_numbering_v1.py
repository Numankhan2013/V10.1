#!/usr/bin/env python3
"""Apply learner-facing Marrow topic numbering in configured taxonomy order.

Source chapter IDs remain immutable. This patch only changes the number printed on
Marrow topic cards so reordered learner indexes are numbered 1..N in their
configured visible order.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app" / "src" / "main" / "assets" / "index.html"
TAXONOMY = ROOT / "data" / "marrow" / "topic_index_taxonomy.json"


def visible_order(config: dict) -> list[str]:
    topics = config.get("topics", [])
    order: list[str] = []
    for section in config.get("sectionOrder", []):
        order.extend(str(item["id"]) for item in topics if item.get("section") == section)
    known = set(order)
    order.extend(str(item["id"]) for item in topics if str(item["id"]) not in known)
    return order


def main() -> None:
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))["subjects"]
    arranged = {subject: visible_order(config) for subject, config in taxonomy.items()}

    source = HTML.read_text(encoding="utf-8")
    helper_name = "nkMarrowVisibleTopicSerial"
    if helper_name not in source:
        anchor = "  function topics() {"
        if source.count(anchor) != 1:
            raise SystemExit(f"Marrow topic-numbering anchor count: {source.count(anchor)}")
        payload = json.dumps(arranged, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
        helper = f'''  const NK_MARROW_VISIBLE_TOPIC_ORDER = {payload};\n  function {helper_name}(chapter) {{\n    const ids=NK_MARROW_VISIBLE_TOPIC_ORDER[String(activeSubject||'')]||[];\n    const index=ids.indexOf(String(chapter?.id||''));\n    return index>=0?index+1:CHAPTERS.findIndex(v=>String(v.id)===String(chapter?.id))+1;\n  }}\n\n'''
        source = source.replace(anchor, helper + anchor, 1)

    old = "serial=CHAPTERS.findIndex(v=>String(v.id)===String(c.id))+1;"
    new = "serial=(typeof activeBank!=='undefined'&&activeBank==='Marrow')?nkMarrowVisibleTopicSerial(c):CHAPTERS.findIndex(v=>String(v.id)===String(c.id))+1;"
    if old in source:
        if source.count(old) != 1:
            raise SystemExit(f"Topic serial expression count: {source.count(old)}")
        source = source.replace(old, new, 1)
    elif new not in source:
        raise SystemExit("Topic serial expression not found")

    HTML.write_text(source, encoding="utf-8")
    phys = arranged.get("Physiology", [])
    expected = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '31', '32', '33', '26', '27', '28', '29', '30', '19', '20', '21', '22', '23', '24', '25', '34', '35', '36', '37', '38', '39', '40', '41', '42', '10', '11', '12', '13', '14', '15', '16', '17', '18', '43']
    if phys != expected:
        raise SystemExit(f"Physiology arranged topic order mismatch: {phys}")
    print("MARROW_TOPIC_NUMBERING_OK physiology_visible=43 learner_serials=1-43 source_ids=preserved")


if __name__ == "__main__":
    main()
