#!/usr/bin/env python3
"""Verify placement and low-drift contracts for harness-neutral project memory."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / ".project-memory"
CANONICAL = [
    "README.md",
    "STATE.md",
    "PRODUCT.md",
    "ARCHITECTURE.md",
    "DECISIONS.md",
    "ROADMAP.md",
    "SESSION_LOG.md",
]
ADAPTERS = [
    ROOT / "CLAUDE.md",
    ROOT / "GEMINI.md",
    ROOT / ".cursorrules",
    ROOT / ".cursor/rules/project-memory.mdc",
    ROOT / ".github/copilot-instructions.md",
]


def fail(message: str) -> None:
    raise SystemExit(f"PROJECT_MEMORY_ERROR: {message}")


def main() -> None:
    agents = ROOT / "AGENTS.md"
    if not agents.is_file():
        fail("AGENTS.md must be at repository root")
    agent_text = agents.read_text(encoding="utf-8")
    for name in CANONICAL:
        path = MEMORY / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            fail(f"missing or empty .project-memory/{name}")
        if f".project-memory/{name}" not in agent_text and name != "README.md":
            fail(f"AGENTS.md does not route to {name}")

    state = (MEMORY / "STATE.md").read_text(encoding="utf-8")
    if re.search(r"(?mi)^\s*-?\s*HEAD\s*:\s*`?[0-9a-f]{7,40}", state):
        fail("STATE.md must resolve live HEAD from Git, not hardcode a self-staling hash")
    for term in ("build-verified", "device-verified", "accepted baseline", "Known problems", "Next step"):
        if term.lower() not in state.lower():
            fail(f"STATE.md is missing required handoff concept: {term}")
    if len(state.splitlines()) > 150:
        fail("STATE.md is too long; move history to SESSION_LOG.md")

    for adapter in ADAPTERS:
        if not adapter.is_file():
            fail(f"missing thin harness adapter: {adapter.relative_to(ROOT)}")
        text = adapter.read_text(encoding="utf-8")
        if "AGENTS.md" not in text or ".project-memory/STATE.md" not in text:
            fail(f"adapter does not route to canonical memory: {adapter.relative_to(ROOT)}")
        if len(text) > 700:
            fail(f"adapter contains too much duplicated knowledge: {adapter.relative_to(ROOT)}")

    markdown_files = [ROOT / "AGENTS.md", *(MEMORY / name for name in CANONICAL), *ADAPTERS]
    broken = []
    for document in markdown_files:
        if document.suffix not in {".md", ".mdc"}:
            continue
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#")):
                continue
            resolved = (document.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                broken.append(f"{document.relative_to(ROOT)} -> {target}")
    if broken:
        fail("broken local links: " + ", ".join(broken))

    for workflow_name in ("build-apk.yml", "engineering-gate.yml"):
        workflow = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
        if "python3 tools/verify_project_memory.py" not in workflow:
            fail(f"memory verification is not wired into {workflow_name}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    legacy = (ROOT / "memory.md").read_text(encoding="utf-8")
    state_commit = re.search(r"Accepted product commit:\s*`([0-9a-f]{7,40})`", state)
    readme_commit = re.search(r"Accepted product commit:\s*`([0-9a-f]{7,40})`", readme)
    if not state_commit or not readme_commit or state_commit.group(1) != readme_commit.group(1):
        fail("accepted product commit is not aligned between STATE.md and README.md")
    engineering = (ROOT / "docs/ENGINEERING_BASELINE.md").read_text(encoding="utf-8")
    if state_commit.group(1) not in "\n".join(legacy.splitlines()[:12]):
        fail("legacy memory.md header is not aligned with the accepted product commit")
    engineering_commit = re.search(r"Accepted product commit:\s*`([0-9a-f]{7,40})`", engineering)
    if not engineering_commit or engineering_commit.group(1) != state_commit.group(1):
        fail("accepted product commit is not aligned with ENGINEERING_BASELINE.md")

    print(
        f"PROJECT_MEMORY_OK canonical={len(CANONICAL)} adapters={len(ADAPTERS)} "
        f"state_lines={len(state.splitlines())}"
    )


if __name__ == "__main__":
    main()
