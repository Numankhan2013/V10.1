#!/usr/bin/env python3
"""Regression contract for the additive community-response statistics layer."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
DATA = ROOT / "data/marrow/community_stats_v1.json"

payload = json.loads(DATA.read_text(encoding="utf-8"))
assert payload["schemaVersion"] == 1
assert payload["source"]["kind"] == "historical_community_response_distribution"
assert len(payload["records"]) >= 1
for record in payload["records"]:
    assert set(record["optionPct"]) == {"A", "B", "C", "D"}
    assert sum(int(record["optionPct"][letter]) for letter in "ABCD") == 100
    assert 0 <= int(record["correctPct"]) <= 100

s = HTML.read_text(encoding="utf-8")
assert s.count('id="nk-community-stats-v1-style"') == 1
assert s.count('id="nk-community-stats-v1-script"') == 1
assert s.count("NK_COMMUNITY_STATS_V1_START") == 2
assert "card.querySelector('.option.correct,.option.wrong')" in s
assert "if(!revealed){ clear(card); return; }" in s
assert ".nk-community-option-pct" in s
assert ".nk-community-correct-summary" in s
assert "of the people got this right" in s
assert "list.insertAdjacentElement('afterend',summary)" in s
assert "text.appendChild(badge)" in s
assert "option.classList" not in s[s.index('id="nk-community-stats-v1-script"'):]

# Every current source-sidecar record must survive resolution and injection
# intact. Keep this fixture-driven so changing the reviewed pilot record does
# not leave a stale question ID or percentage tuple in the regression test.
for record in payload["records"]:
    assert record["sourceQuestionId"] in s
    assert f'"correctPct":{int(record["correctPct"])}' in s
    option_pct = json.dumps(record["optionPct"], separators=(",", ":"))
    assert f'"optionPct":{option_pct}' in s

print("COMMUNITY_STATS_V1_TEST_OK hidden_until_reveal=1 baseline_option_classes_untouched=1 fixture_driven=1")
