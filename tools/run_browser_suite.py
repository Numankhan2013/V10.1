#!/usr/bin/env python3
"""Run independent browser verifiers concurrently and fail if any of them fails.

Every verifier serves build/web on its own ephemeral port and writes to its own
build/ output folder, so they are safe to run side by side. Each verifier's
output is buffered and printed as one block when it finishes, slowest first in
the queue so the pool drains evenly.
"""
import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Measured on GitHub runners; anything unlisted is assumed to be quick.
SLOW_FIRST = (
    'tools/verify_uworld_biochemistry_browser.py',
    'tools/capture_marrow_image_review.py',
    'tools/verify_marrow_bank_browser_v2.py',
    'tools/verify_marrow_explanation_refinement_browser.py',
    'tools/capture_study_ui_audit.py',
    'tools/verify_question_note_media_browser.py',
    'tools/verify_learning_insights_browser.py',
    'tools/verify_pwa_update_browser.py',
    'tools/verify_continue_practice_browser.py',
)


def run(entry, timeout):
    # "tools/x.py:--flag=value" passes arguments, so one slow verifier can be split.
    script, *extra = entry.split(':')
    started = time.monotonic()
    try:
        done = subprocess.run([sys.executable, script, *extra], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        code, out = done.returncode, done.stdout + done.stderr
    except subprocess.TimeoutExpired as error:
        code, out = 124, f'{error.stdout or ""}{error.stderr or ""}\nTIMED OUT after {timeout}s'
    return entry, code, out, time.monotonic() - started


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scripts', nargs='+')
    parser.add_argument('--jobs', type=int, default=int(os.environ.get('NK_BROWSER_JOBS') or min(4, os.cpu_count() or 2)))
    parser.add_argument('--timeout', type=int, default=900)
    args = parser.parse_args()
    missing = [entry for entry in args.scripts if not (ROOT / entry.split(':')[0]).is_file()]
    if missing:
        raise SystemExit('Missing browser verifiers: ' + ', '.join(missing))
    rank = {script: index for index, script in enumerate(SLOW_FIRST)}
    queue = sorted(dict.fromkeys(args.scripts), key=lambda entry: rank.get(entry.split(':')[0], len(rank)))
    group = os.environ.get('GITHUB_ACTIONS') == 'true'
    failed, timings, started = [], [], time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for future in as_completed([pool.submit(run, script, args.timeout) for script in queue]):
            script, code, out, seconds = future.result()
            timings.append((seconds, script, code))
            title = f'{"PASS" if code == 0 else "FAIL"} {script} ({seconds:.0f}s)'
            print(f'::group::{title}' if group else f'===== {title}', flush=True)
            print(out.rstrip(), flush=True)
            if group:
                print('::endgroup::', flush=True)
            if code:
                failed.append(script)
                if group:
                    print(f'::error title=Browser verifier failed::{script} exited {code}', flush=True)
    print(f'\nBrowser suite: {len(queue) - len(failed)}/{len(queue)} passed in {time.monotonic() - started:.0f}s with {args.jobs} workers')
    for seconds, script, code in sorted(timings, reverse=True):
        print(f'  {seconds:6.0f}s  {"ok  " if code == 0 else "FAIL"}  {script}')
    if failed:
        print('\nFAILED: ' + ', '.join(failed))
        sys.exit(1)
    print('BROWSER_SUITE_OK')


if __name__ == '__main__':
    main()
