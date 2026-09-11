#!/usr/bin/env python3
"""Validate ordering and ownership of the deterministic APK transformation chain."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/build-apk.yml"
text = WORKFLOW.read_text(encoding="utf-8")

required_order = [
    "tools/fix_review_build.py",
    "tools/harden_review_renderer.py",
    "tools/build_source_visual_metadata.py",
    "tools/improve_source_visual_assets_v1.py",
    "tools/install_source_visual_renderer.py",
    "tools/cbt_canonical.py",
    "tools/apply_question_ui_v2.py",
    "tools/apply_home_visual_redesign_v4.py",
    "tools/apply_home_v5_fixes.py",
    "tools/remove_legacy_streak_layer.py",
    "tools/apply_home_streak_and_header_v1.py",
    "tools/apply_home_actions_v1.py",
    "tools/apply_cbt_boundary_and_toast_fix_v1.py",
    "tools/harden_cbt_review_footer_v1.py",
    "tools/add_review_solution_grid.py",
    "tools/apply_question_experience_v1.py",
    "tools/test_question_experience_v1.py",
    "tools/apply_session_experience_v2.py",
    "tools/test_session_experience_v2.py",
    "tools/apply_whole_app_vision_v1.py",
    "tools/test_whole_app_vision_v1.py",
    "tools/apply_custom_study_modules_v1.py",
    "tools/test_custom_study_modules_v1.py",
    "tools/apply_home_command_center_v1.py",
    "tools/test_home_command_center_v1.py",
    "tools/apply_question_content_hygiene_v1.py",
    "tools/test_question_content_hygiene_v1.py",
    "tools/apply_android_secure_origin_v1.py",
    "tools/apply_cross_device_pwa_v1.py",
    "tools/test_cross_device_sync_v1.py",
    "tools/apply_fsrs_v1.py",
    "tools/test_fsrs_v1.py",
    "tools/fix_boot_syntax.py",
    "tools/apply_marrow_bank_pilot.py",
    "tools/apply_marrow_structured_table_renderer_v1.py",
    "tools/install_marrow_images.py",
    "tools/test_marrow_bank_pilot.py",
    "tools/verify_product_contract.py --stage generated",
    "tools/verify_cbt_invariants.py",
]

# The full workflow must remain a strict Linux PDF/build gate, even though local
# Termux generation is intentionally skipped by the preflight.
for marker in ("runs-on: ubuntu-latest", "actions/setup-python@", "PyMuPDF Pillow",
               "tools/verification_preflight.py --require-pdf",
               "tools/build_biochem_solution_map.py", "tools/final_hardening.py",
               "tools/verify_source_visual_contract.py",
               "tools/verify_product_contract.py --stage packaged",
               "tools/verify_marrow_structured_table_browser.py",
               "NK_MARROW_STRUCTURED_TABLE_RENDERER_V1"):
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

if text.find("tools/fix_boot_syntax.py") > text.find("Verify final JavaScript syntax"):
    raise SystemExit("Boot syntax repair must run before final JavaScript validation")
if text.find("Verify packaged APK") < text.find("Build debug APK"):
    raise SystemExit("Packaged verification must run after the APK build")
if text.find("tools/apply_marrow_bank_pilot.py") > text.find("tools/apply_marrow_structured_table_renderer_v1.py"):
    raise SystemExit("Structured-table compatibility must run after Marrow bank generation")
if text.find("tools/apply_marrow_structured_table_renderer_v1.py") > text.find("tools/install_marrow_images.py"):
    raise SystemExit("Structured-table compatibility must precede image installation")
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
