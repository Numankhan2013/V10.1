from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# The Review Solutions path must use the original in-scope QB.reviewTest(),
# which directly updates the private route state and renders the page.
# Remove the later wrapper layers that were fighting that implementation.
for script_id in ('v103-stabilize', 'v103-review-explanation-js', 'v1033-review-hardening'):
    s = re.sub(
        rf'\n?<script id="{re.escape(script_id)}">.*?</script>\n?',
        '\n',
        s,
        count=1,
        flags=re.S,
    )
s = s.replace('<!-- V1033_REVIEW_HARDENING -->', '')

# Remove the old capture-phase Review Solutions guard from the V10.2 layer.
s = re.sub(
    r'\n  function reviewSolutionsGuard\(\)\{.*?\n  reviewSolutionsGuard\(\);\n',
    '\n',
    s,
    count=1,
    flags=re.S,
)

# Make the CTA self-contained: no delegated/capture listener is required.
old = '<button class="primary-btn v102-review-action" type="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>'
new = '<button class="primary-btn v102-review-action" type="button" data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>'
if old in s:
    s = s.replace(old, new, 1)
else:
    # Idempotent fallback if the direct CTA is already present.
    s = s.replace(
        'data-v102-review-cta="1" data-review-test-id="${esc(t.id)}"',
        'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"',
        1,
    )

# In review mode, stop at the final question instead of jumping back to Q1.
s = s.replace(
    "else if(s.mode==='review'){s.index=0;render();}",
    "else if(s.mode==='review'){showToast('End of review reached.');render();}",
    1,
)

p.write_text(s, encoding='utf-8')
print('Review build patch applied.')
