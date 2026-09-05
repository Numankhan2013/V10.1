#!/usr/bin/env python3
"""Repair the generated Home/Topics JavaScript before APK packaging.

The Topics row template must close its nested template literal before the
Array.map callback closes. A missing backtick is a WebView boot-blocking
syntax error, so fail loudly unless the exact defect is present.
"""
from pathlib import Path

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")
old = "</button>;}).join('')}</div>"
new = "</button>`;}).join('')}</div>"
count = s.count(old)
if count != 1:
    raise SystemExit(f"boot syntax repair expected exactly 1 malformed Topics template, found {count}")
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("BOOT_SYNTAX_REPAIRED=1")
