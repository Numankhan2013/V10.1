#!/usr/bin/env python3
"""Repair the known WebView boot-blocking Topics template defect, if present.

This step is intentionally idempotent: later hardening passes may already have
normalized the template, in which case no edit is required. A separate syntax
verification step remains authoritative.
"""
from pathlib import Path

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")
old = "</button>;}).join('')}</div>"
new = "</button>`;}).join('')}</div>"
count = s.count(old)
if count:
    if count != 1:
        raise SystemExit(f"boot syntax repair found {count} malformed Topics templates; refusing ambiguous edit")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
    print("BOOT_SYNTAX_REPAIRED=1")
else:
    print("BOOT_SYNTAX_REPAIRED=0 (no known malformed template present)")
