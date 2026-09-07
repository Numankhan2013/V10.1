#!/usr/bin/env python3
"""Write public Firebase/PWA runtime configuration from environment variables."""

from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app/src/main/assets/qbank-config.js"


def main() -> None:
    config = {
        "apiKey": os.environ.get("QBANK_FIREBASE_API_KEY", "").strip(),
        "projectId": os.environ.get("QBANK_FIREBASE_PROJECT_ID", "").strip(),
        "anatomyPdfUrl": os.environ.get("QBANK_ANATOMY_PDF_URL", "").strip(),
    }
    OUT.write_text(
        "/* Generated public client configuration; authorization is enforced by Firebase rules. */\n"
        "window.NK_QBANK_FIREBASE_CONFIG = "
        + json.dumps(config, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    status = "configured" if config["apiKey"] and config["projectId"] else "disabled"
    print(f"QBANK_RUNTIME_CONFIG_OK firebase={status}")


if __name__ == "__main__":
    main()
