#!/usr/bin/env python3
"""Assemble the app page and write the question data into it.

app/src/main/assets/index.html is the app's source: markup, styles and scripts,
edited directly. Its larger features live in app/src/main/modules/ and are put
in place at their `/* @module <file> */` markers (tools/app_page.py). Data it
embeds is generated from data/ and replaced here, each at a
`__NK_DATA_<NAME>__` token, so a data change never needs a code change:

  SUBJECT_QBANK_DATA, QBANK_DATA   assets/subjects_qbank_data.js, qbank_data.js
  MARROW_DATA                      data/marrow expanded banks + reviewed overrides,
                                   plus the PrepLadder Microbiology, Pathology and
                                   Pharmacology text banks
  MARROW_EXPLANATION_GOLD          data/marrow approved explanation batches
  MARROW_TOPIC_TAXONOMY            data/marrow/topic_index_taxonomy.json
  MARROW_VISIBLE_TOPIC_ORDER       the same taxonomy, in learner order
  TOPIC_SECTIONS                   data/topic_sections.json
  UWORLD_SCRIPTS                   one <script> per UWorld collection file

It also writes the generated data files those tokens point at (UWorld
collections, Marrow figures). Every token must be replaced; any token left over
fails the build.

  python3 tools/build_app_data.py            # assemble and fill index.html in place
  python3 tools/build_app_data.py --check    # list the tokens without writing
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from app_page import assemble

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
HTML = ASSETS / "index.html"
TOKEN = re.compile(r"__NK_DATA_([A-Z_]+?)__")


def js_json(value, ascii_only: bool = False) -> str:
    """JSON that is safe inside an inline <script>."""
    return json.dumps(value, ensure_ascii=ascii_only, separators=(",", ":")).replace("</", "<\\/")


def asset_script(name: str) -> str:
    return (ASSETS / name).read_text(encoding="utf-8").strip()


def marrow_data() -> str:
    from marrow_bank_data import app_marrow_records, validate_biochemistry_batches
    records = app_marrow_records()
    validate_biochemistry_batches(records[1])
    # PrepLadder Microbiology, Pathology and Pharmacology have structured text
    # explanations, so they travel with the Marrow records; the app files them
    # under PrepLadder by their bank.
    from build_prepladder_microbiology_bank import app_record
    from build_prepladder_pathology_bank import app_record as pathology_record
    from build_prepladder_pharmacology_bank import app_record as pharmacology_record
    return js_json({"records": records + [app_record(), pathology_record(), pharmacology_record()]})


def marrow_explanation_gold() -> str:
    from marrow_bank_data import canonical_source_questions, merged_explanations
    return js_json(merged_explanations(canonical_source_questions()))


def marrow_taxonomy() -> dict:
    return json.loads((ROOT / "data/marrow/topic_index_taxonomy.json").read_text(encoding="utf-8"))["subjects"]


def marrow_topic_taxonomy() -> str:
    runtime = {subject: {"sectionOrder": cfg["sectionOrder"], "topics": {str(topic["id"]): topic for topic in cfg["topics"]}}
               for subject, cfg in marrow_taxonomy().items()}
    return json.dumps(runtime, separators=(",", ":"))


def marrow_visible_topic_order() -> str:
    def visible(config: dict) -> list[str]:
        topics = config.get("topics", [])
        order = [str(item["id"]) for section in config.get("sectionOrder", []) for item in topics if item.get("section") == section]
        known = set(order)
        return order + [str(item["id"]) for item in topics if str(item["id"]) not in known]
    return js_json({subject: visible(config) for subject, config in marrow_taxonomy().items()})


def topic_sections() -> str:
    return json.dumps(json.loads((ROOT / "data/topic_sections.json").read_text())["sections"], separators=(",", ":"))


def uworld_scripts() -> str:
    from uworld_app_data import write_collections
    return "".join(f'<script src="{name}"></script>\n' for name in write_collections())


def release_marrow_figures() -> None:
    from marrow_images import release
    release(ROOT / "data/marrow/images/registry.json")
    from microbiology_visuals import release as release_microbiology
    release_microbiology()
    from build_prepladder_microbiology_bank import release as release_prepladder_microbiology
    release_prepladder_microbiology()
    from build_prepladder_pathology_bank import release as release_prepladder_pathology
    release_prepladder_pathology()
    from build_prepladder_pharmacology_bank import release as release_prepladder_pharmacology
    release_prepladder_pharmacology()


BUILDERS = {
    "SUBJECT_QBANK_DATA": lambda: asset_script("subjects_qbank_data.js"),
    "QBANK_DATA": lambda: asset_script("qbank_data.js"),
    "MARROW_DATA": marrow_data,
    "MARROW_EXPLANATION_GOLD": marrow_explanation_gold,
    "MARROW_TOPIC_TAXONOMY": marrow_topic_taxonomy,
    "MARROW_VISIBLE_TOPIC_ORDER": marrow_visible_topic_order,
    "TOPIC_SECTIONS": topic_sections,
    "UWORLD_SCRIPTS": uworld_scripts,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report the tokens in index.html without writing")
    args = parser.parse_args()
    page = assemble(HTML.read_text(encoding="utf-8"))
    found = TOKEN.findall(page)
    unknown = sorted(set(found) - set(BUILDERS))
    missing = sorted(set(BUILDERS) - set(found))
    if unknown or missing:
        raise SystemExit(f"index.html data tokens do not match the builders: unknown={unknown} missing={missing}")
    if args.check:
        print("APP_DATA_TOKENS_OK " + " ".join(f"{name}x{found.count(name)}" for name in BUILDERS))
        return
    release_marrow_figures()
    values = {name: build() for name, build in BUILDERS.items()}
    page = TOKEN.sub(lambda m: values[m.group(1)], page)
    HTML.write_text(page, encoding="utf-8")
    print(f"APP_DATA_OK tokens={len(found)} kb={len(page.encode()) / 1024:.0f}")


if __name__ == "__main__":
    main()
