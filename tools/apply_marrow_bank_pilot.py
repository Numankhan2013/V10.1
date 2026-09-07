#!/usr/bin/env python3
"""Verified loader for the Marrow bank pilot transformer payload."""
from __future__ import annotations
import base64, hashlib, zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARTS=sorted(HERE.glob("apply_marrow_bank_pilot.py.zlib.b64.part*"))
EXPECTED="ce0798cfdd1d10952e91718f980e2c77473c0557e72cbd8bdbde48a8e61663d3"
if len(PARTS)!=3:
    raise SystemExit(f"Marrow transformer payload parts mismatch: {len(PARTS)}")
payload="".join(p.read_text(encoding="utf-8").strip() for p in PARTS)
source=zlib.decompress(base64.b64decode(payload,validate=True))
if hashlib.sha256(source).hexdigest()!=EXPECTED:
    raise SystemExit("Marrow transformer payload SHA-256 mismatch")
exec(compile(source,str(Path(__file__)),"exec"),{"__name__":"__main__","__file__":str(Path(__file__))})
