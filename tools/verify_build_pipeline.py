#!/usr/bin/env python3
"""Validate ordering and ownership of the deterministic APK transformation chain."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/build-apk.yml"
text = WORKFLOW.read_text(encoding="utf-8")

# index.html is source: no workflow step may rewrite its code. The one data
# step fills the page's __NK_DATA_*__ tokens after the source checks and before
# anything reads the generated page.
required_order = [
    "tools/verify_product_contract.py --stage source",
    "tools/test_app_source_parity.py",
    "tools/build_app_data.py",
    "tools/build_biochem_solution_map.py",
    "tools/final_hardening.py",
    "tools/build_source_visual_metadata.py",
    "tools/improve_source_visual_assets_v1.py",
    "tools/verify_source_visual_contract.py",
    "tools/test_marrow_bank_pilot.py",
    "tools/verify_product_contract.py --stage generated",
    "tools/verify_cbt_invariants.py",
    "tools/build_web_dist.py",
    "tools/run_browser_suite.py",
]

# The full workflow must remain a strict Linux PDF/build gate, even though local
# Termux generation is intentionally skipped by the preflight.
for marker in ("runs-on: ubuntu-latest", "actions/setup-python@", "PyMuPDF Pillow",
               "tools/verification_preflight.py --require-pdf",
               "tools/build_biochem_solution_map.py", "tools/final_hardening.py",
               "tools/verify_source_visual_contract.py",
               "tools/verify_product_contract.py --stage packaged",
               "tools/verify_marrow_structured_table_browser.py",
               "tools/verify_continue_practice_browser.py",
               "tools/verify_question_presentation_browser.py",
               "tools/verify_revision_desk_browser.py",
               "tools/verify_question_search_browser.py",
               "tools/verify_practice_correction_browser.py",
               "tools/verify_learning_insights_browser.py",
               "tools/verify_app_clarity_browser.py",
               "tools/verify_refined_analysis_browser.py",
               "tools/verify_interaction_polish_browser.py",
               "tools/verify_visual_refinement_browser.py",
               "tools/verify_bank_aware_cbt_builder_browser.py",
               "tools/verify_pyq_exam_journey_browser.py",
               "tools/verify_cbt_result_analysis_browser.py",
               "tools/verify_study_journey_browser.py",
               "tools/verify_marrow_content_hygiene_browser.py",
               "NK_MARROW_STRUCTURED_TABLE_RENDERER_V1",
               "NK_QUESTION_PRESENTATION_V1_START",
               "tools/test_app_source_parity.py", "tools/build_app_data.py"):
    if marker not in text:
        raise SystemExit(f"Full Linux/PDF verification requirement missing: {marker}")
if not (text.index("PyMuPDF Pillow") < text.index("tools/verification_preflight.py --require-pdf")
        < text.index("tools/build_biochem_solution_map.py")):
    raise SystemExit("Strict PDF preflight must follow dependency installation and precede generation")

positions = []
for command in required_order:
    position = text.find(command)
    if position < 0:
        raise SystemExit(f"Required pipeline command missing: {command}")
    positions.append(position)
if positions != sorted(positions):
    raise SystemExit("Protected build commands are out of order")

commands = re.findall(r"run:\s+python3\s+(tools/[A-Za-z0-9_.-]+\.py)", text)
commands = [
    command for command in commands
    if not Path(command).name.startswith("verify_")
    and Path(command).name not in {
        "write_build_manifest.py", "configure_marrow_pilot_android.py",
        "check_marrow_image_package.py",
    }
]
duplicates = sorted({command for command in commands if commands.count(command) > 1})
if duplicates:
    raise SystemExit(f"Transformation scripts have multiple workflow owners: {duplicates}")

if text.find("Verify packaged APK") < text.find("Build debug APK"):
    raise SystemExit("Packaged verification must run after the APK build")
# A step that rewrites the app page's code would make index.html stop being source.
page_writers = sorted(set(re.findall(r"python3\s+(tools/(?:apply|install|fix|harden|remove|add|cbt)_[A-Za-z0-9_]+\.py)", text)))
if page_writers:
    raise SystemExit(f"index.html is source; these steps patch it: {page_writers}")
if "v11.1-engineering-foundation" not in text:
    raise SystemExit("Engineering branch is not protected by the build workflow")
for marker in (
    "branches: [main, 'consolidation/**'",
    "promote_production:",
    "release_sha:",
    'github.ref_name == \'main\'',
    "inputs.promote_production",
    "inputs.release_sha == github.sha",
    'test "$EXPECTED_RELEASE_SHA" = "$GITHUB_SHA"',
    "github.ref_name != 'main' && (github.ref_name != 'feature/marrow-bank-pilot'",
):
    if marker not in text:
        raise SystemExit(f"Explicit production release guard missing: {marker}")
if "github.event_name == 'workflow_dispatch' && github.ref_name != 'feature/marrow-bank-pilot'" in text:
    raise SystemExit("Branch-name-only production promotion guard must not return")

print(f"BUILD_PIPELINE_OK python_steps={len(commands)} protected_order={len(required_order)}")
