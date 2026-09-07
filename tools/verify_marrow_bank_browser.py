#!/usr/bin/env python3
"""SHA-verified launcher for the chunked Marrow browser smoke test."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARTS=sorted(HERE.glob("marrow_pilot_browser.b64.part*"))
EXPECTED="0952872c0ef848fa8bdcf565ede432799b9b44429c9baedbcfb8694d5208013b"
if len(PARTS)!=2:
    raise SystemExit(f"Marrow browser payload parts mismatch: {len(PARTS)}")
payload=base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in PARTS),validate=True)
if hashlib.sha256(payload).hexdigest()!=EXPECTED:
    raise SystemExit("Marrow browser payload SHA-256 mismatch")
exec(compile(payload,str(Path(__file__).resolve()),"exec"),{
    "__name__":"__main__",
    "__file__":str(Path(__file__).resolve()),
    "__builtins__":__builtins__,
})
