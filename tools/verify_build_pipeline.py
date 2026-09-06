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
    "tools/apply_question_content_hygiene_v1.py",
    "tools/test_question_content_hygiene_v1.py",
    "tools/fix_boot_syntax.py",
    "tools/verify_product_contract.py --stage generated",
    "tools/verify_cbt_invariants.py",
]

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
    and Path(command).name != "write_build_manifest.py"
]
duplicates = sorted({command for command in commands if commands.count(command) > 1})
if duplicates:
    raise SystemExit(f"Transformation scripts have multiple workflow owners: {duplicates}")

if text.find("tools/fix_boot_syntax.py") > text.find("Verify final JavaScript syntax"):
    raise SystemExit("Boot syntax repair must run before final JavaScript validation")
if text.find("Verify packaged APK") < text.find("Build debug APK"):
    raise SystemExit("Packaged verification must run after the APK build")
if "v11.1-engineering-foundation" not in text:
    raise SystemExit("Engineering branch is not protected by the build workflow")

print(f"BUILD_PIPELINE_OK python_steps={len(commands)} protected_order={len(required_order)}")
