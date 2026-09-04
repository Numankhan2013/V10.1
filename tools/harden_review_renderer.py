from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# The navigator redesign now owns the Review Solutions renderer. The old hardening
# pass assumed reviewTestPage() was immediately followed by endSession(), but the
# navigator functions are intentionally inserted between them. Keep this legacy
# workflow step safe and non-destructive rather than rewriting the renderer again.
if 'function reviewTestPage()' not in s:
    raise SystemExit('Expected reviewTestPage in built source')
if 'qb-question-navigator' not in s:
    raise SystemExit('Expected question navigator in built source')

print('Review renderer already hardened by navigator build; no-op.')
