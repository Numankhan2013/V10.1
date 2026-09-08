#!/usr/bin/env python3
"""Repair the known WebView boot-blocking Topics template defect, if present.

The V11 Home/Topics composition contains a nested template literal. Some
build passes already normalize it, so this repair is deliberately idempotent.
The subsequent Node syntax check is authoritative.
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
    print("BOOT_SYNTAX_REPAIRED=0")
