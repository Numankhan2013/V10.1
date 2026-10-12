#!/usr/bin/env python3
"""Write each UWorld collection as its own script under assets/uworld_data/.

One file per collection keeps index.html far below the 25 MB Pages file limit.
The scripts load synchronously before the app script that reads them.
"""
from __future__ import annotations

import json

from uworld_biochemistry import ROOT
from uworld_collections import bank_records

DATA_DIR = ROOT / 'app/src/main/assets/uworld_data'


def write_collections() -> list[str]:
    records = bank_records()
    if DATA_DIR.exists():
        for old in DATA_DIR.glob('*.js'):
            old.unlink()
    DATA_DIR.mkdir(exist_ok=True)
    names = []
    for i, record in enumerate(records):
        data = json.dumps(record, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        name = f'uworld_data/collection-{i:02d}.js'
        (DATA_DIR.parent / name).write_text(f'(window.NK_UWORLD_DATA=window.NK_UWORLD_DATA||[])[{i}]={data};\n', encoding='utf-8')
        names.append(name)
    print(f'UWORLD_COLLECTIONS_WRITTEN collections={len(records)} questions={sum(len(r["questions"]) for r in records)} '
          f'topics={sum(len(r["topics"]) for r in records)}')
    return names
