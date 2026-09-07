#!/usr/bin/env python3
"""Run source/behavior checks without generating or changing app assets."""

from pathlib import Path
import subprocess
import sys

from verification_preflight import is_termux, pdf_preflight

ROOT = Path(__file__).resolve().parents[1]
# These consume artifacts produced by the full ordered PDF/app pipeline.
CI_TESTS = {
    "test_question_experience_v1.py",
    "test_session_experience_v2.py",
    "test_whole_app_vision_v1.py",
}
CI_VERIFIERS = {"verify_cbt_invariants.py", "verify_source_visual_contract.py", "verify_recall_dock_browser.py"}


def main():
    if is_termux():
        pdf_preflight()
    commands = [[sys.executable, "-m", "compileall", "-q", "tools"]]
    for path in sorted((ROOT / "tools").glob("test_*.py")):
        if path.name in CI_TESTS:
            print(f"CI_ONLY: {path.name} requires the ordered generated-app/PDF pipeline", flush=True)
        else:
            commands.append([sys.executable, str(path)])
    for path in sorted((ROOT / "tools").glob("verify_*.py")):
        if path.name == "verify_local.py":
            continue
        if path.name in CI_VERIFIERS:
            print(f"CI_ONLY: {path.name} requires generated PDF/app artifacts", flush=True)
        else:
            commands.append([sys.executable, str(path)] + (["--stage", "source"] if path.name == "verify_product_contract.py" else []))
    for directory in (ROOT / "tools", ROOT / "app/src/main/assets"):
        for pattern in ("*.js", "*.mjs"):
            commands.extend(["node", "--check", str(path)] for path in sorted(directory.glob(pattern)))
    failed = []
    for command in commands:
        print("CHECK:", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            failed.append(" ".join(command))
    if failed:
        raise SystemExit("LOCAL_CHECKS_FAILED:\n" + "\n".join(failed))
    print(f"LOCAL_CHECKS_OK checks={len(commands)}; full PDF/generated-app/APK verification remains CI-only and is NOT complete.")


if __name__ == "__main__":
    main()
