#!/usr/bin/env python3
"""Print question-rarity cutoffs from each source's real cohort data.

Rarity tiers are percentile "drop rates" within one source bank:
Legendary = hardest 5%, Great = next 10%, Rare = next 30%, Easy = the rest.
Each cutoff is the lowest whole % correct that falls outside the tier.
Run after a large import, then copy the numbers into
app/src/main/modules/question_rarity.js (NK_RARITY_CUTOFFS) by hand, so a
change in tiers is always a reviewed source change.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SHARES = {"legendary": 0.05, "great": 0.15, "rare": 0.45}


def cutoffs(values: list[float]) -> dict[str, int]:
    values = sorted(values)
    n = len(values)
    out = {}
    for tier, share in SHARES.items():
        # smallest integer t such that the share of values below t is >= share
        t = 0
        while t <= 100 and sum(v < t for v in values) / n < share:
            t += 1
        out[tier] = t
    return out


def uworld_values() -> list[float]:
    from uworld_collections import bank_records
    out = []
    for record in bank_records():
        for q in record["questions"]:
            stats = (q.get("uworldDocument") or {}).get("statistics") or (q.get("uworldSource") or {}).get("statistics") or {}
            if stats.get("answered_correctly_percent") is not None:
                out.append(float(stats["answered_correctly_percent"]))
    return out


def marrow_values() -> list[float]:
    seen, out = set(), []
    for path in sorted(glob.glob(str(ROOT / "data/marrow/**/source/*.jsonl"), recursive=True)):
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("id") in seen or row.get("peer_accuracy_percentage") is None:
                continue
            seen.add(row.get("id"))
            out.append(float(row["peer_accuracy_percentage"]))
    return out


def main():
    for name, load in (("UWorld", uworld_values), ("Marrow", marrow_values)):
        try:
            values = load()
        except (FileNotFoundError, OSError) as error:
            print(f"{name}: source data unavailable ({error})")
            continue
        if not values:
            print(f"{name}: no cohort percentages found")
            continue
        cut = cutoffs(values)
        n = len(values)
        shares = [sum(v < cut["legendary"] for v in values), sum(cut["legendary"] <= v < cut["great"] for v in values),
                  sum(cut["great"] <= v < cut["rare"] for v in values), sum(v >= cut["rare"] for v in values)]
        print(f"{name}: n={n} cutoffs={json.dumps(cut)} tiers%=" + "/".join(f"{100 * s / n:.1f}" for s in shares))


if __name__ == "__main__":
    main()
