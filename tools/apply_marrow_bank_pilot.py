#!/usr/bin/env python3
"""SHA-verified launcher for the chunked Marrow pilot transformer."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARTS=sorted(HERE.glob("marrow_pilot_apply.b64.part*"))
EXPECTED="ce0798cfdd1d10952e91718f980e2c77473c0557e72cbd8bdbde48a8e61663d3"
if len(PARTS)!=10:
    raise SystemExit(f"Marrow transformer payload parts mismatch: {len(PARTS)}")
payload=base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in PARTS),validate=True)
if hashlib.sha256(payload).hexdigest()!=EXPECTED:
    raise SystemExit("Marrow transformer payload SHA-256 mismatch")
exec(compile(payload,str(Path(__file__).resolve()),"exec"),{
    "__name__":"__main__",
    "__file__":str(Path(__file__).resolve()),
    "__builtins__":__builtins__,
})
