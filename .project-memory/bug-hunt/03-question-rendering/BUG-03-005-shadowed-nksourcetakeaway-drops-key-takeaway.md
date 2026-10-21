# BUG-03-005 — A stale inline `nkSourceTakeaway` shadows the hygiene module and drops the Key takeaway on ~19% of questions

- **Area:** 03 question rendering
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/assets/index.html:1443`, `app/src/main/modules/question_content_hygiene.js:153`, `app/src/main/modules/question_content_hygiene.js:129`, `app/src/main/assets/index.html:1759`, `app/src/main/assets/index.html:1733`, `tools/test_question_content_hygiene_v1.py:35`, `tools/test_app_source_parity.py:17`
- **Introduced by:** `975c0457` "Move feature modules beside the page and include them, not copy them" (the duplicate predates it: `index.html` already held two copies of `nkSourceTakeaway` before the module was extracted, and the extraction left the older one behind)

## What happens

Every practice question shows a "Key takeaway" card under the question. The card's text is produced by `nkSourceTakeaway(q)`. The app carries two implementations of that function: the current one in the content-hygiene module, and an older copy still sitting directly in the page. Because both end up in the same JavaScript scope, the older copy wins, so the newer module implementation never runs. The older copy is worse in two ways: it never produces a takeaway when the answer's words do not appear in a sentence of the explanation (it returns an empty string and the card is not rendered at all), and it does not understand the two-column table layout that the source explanations use, so it can pick text out of the wrong column.

The learner sees a missing "Key takeaway" card on roughly one question in five, and on hundreds of others sees a takeaway that quotes the wrong table column or a truncated fragment instead of the answer's mechanism.

## Evidence

### The duplicate is real, and both copies land in the same scope

`app/src/main/assets/index.html` line 1443 defines the function inline:

```javascript
1443:  function nkSourceTakeaway(q) {
1444:    const reviewed=String(q?.keyTakeaway||q?.takeaway||'').replace(/\s+/g,' ').trim();
1445:    if(reviewed.length>=24) return reviewed;
...
1459:    const sentences=(source.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[])
...
1471:    return best&&bestScore>=needed?best:'';
1472:  }
```

`app/src/main/modules/question_content_hygiene.js` line 153 defines it again, and `tools/app_page.py` `assemble()` inlines that module at the `/* @module question_content_hygiene.js */` marker (`app/src/main/assets/index.html:103`).

Assembling the page and walking the braces of the page's `(() => { ... })()` IIFE shows both declarations at the same brace depth (2), i.e. the same function scope, with the inline copy **later** in the file:

```
$ python3 - <<'PY'
import sys; sys.path.insert(0,'tools')
from app_page import app_page
lines = app_page().split('\n')
depth=0; in_str=None; esc=False
for i,l in enumerate(lines[87:7881], start=88):
    j=0
    while j < len(l):
        c=l[j]
        if in_str:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==in_str: in_str=None
        else:
            if c in '"\'`': in_str=c
            elif c=='{': depth+=1
            elif c=='}': depth-=1
        j+=1
    if 'function nkSourceTakeaway' in l: print(i, 'brace depth', depth)
PY
255 brace depth 2
2808 brace depth 2
```

Line 255 is the module's copy (the module occupies assembled lines 103–282); line 2808 is the page's inline copy. In one scope, the **later** function declaration is the one that is bound, so the inline copy at 2808 wins and the module's implementation at 255 is unreachable.

Evaluating both in one scope reproduces the winner:

```javascript
const f = new Function(helpers + moduleFn + '\n' + inlineFn +
                       '\nreturn {fn:nkSourceTakeaway, usesTable:String(nkSourceTakeaway).includes("nkTableTakeaway")};')();
// resolved fn uses nkTableTakeaway: false
// resolved fn is the inline copy: true
```

### The two implementations really behave differently

The module version calls `nkTableTakeaway(...)` and falls back to `nkFinishTakeaway(answer)`; the inline version has neither, does not strip table-shaped rows out of the prose candidate set, and returns `''` when no sentence scores high enough.

Running both over one real question (`physiology-1-4`, from `app/src/main/assets/subjects_qbank_data.js`):

```
INLINE : "GABA mediates presynaptic inhibition/Indirect Inhibition via a G-protein that causes an increase in K+ conductance."
MODULE : "GABA."
```

and over `physiology-1-6`:

```
INLINE : ""            <- no Key takeaway is rendered at all
MODULE : "Ca2+ influx → ACh release → End-plate potential → Muscle contraction."
```

The module version is the intended one: `tools/test_question_content_hygiene_v1.py` line 35 asserts exactly the module's output,

```javascript
const takeaway=nkSourceTakeaway(q);
if(takeaway!=='Soluble fibre helps lower LDL cholesterol. This occurs by increasing bile acid excretion and interfering with bile acid reabsorption.')throw new Error(takeaway);
if(/adds bulk|bowel movements/i.test(takeaway))throw new Error('Opposite table column leaked into takeaway');
```

and the shipped app produces neither of those values for that input.

### Measured impact over every shipped question

Scanning all 10,105 questions in the shipped banks — the PrepLadder Anatomy/Physiology/Biochemistry source banks (`app/src/main/assets/qbank_data.js`, `app/src/main/assets/subjects_qbank_data.js`), the three PrepLadder text banks (`data/Prepladder/*/prepladder_*_qbank.zlib.b64.part*`), and the four Marrow banks (`tools/marrow_bank_data.py::app_marrow_records()`):

```
total questions across all banks: 10105
takeaway differs: 2354
  inline returns EMPTY, module returns text: 1940
  differ only by trailing period: 49
  differ in content: 365
  identical: 7751
```

1,940 questions is 19.2% of every question the learner can be shown.

### Why the learner sees nothing for those 1,940

`app/src/main/assets/index.html` line 1759 renders the card only when the takeaway is non-empty:

```javascript
1759:  return `<div class="nk-study-support">${time}${nkSourceCohort(q)}${takeaway?`<section class="nk-key-takeaway">...` : ''}${sourceHeader}</div>`;
```

so the inline copy's empty string removes the "Key takeaway" section outright. `nkMarrowTakeaway` (index.html line 1733) also calls `nkSourceTakeaway(q)` as its fallback, so the Marrow bank path is affected too.

### Why no test caught it

`tools/test_question_content_hygiene_v1.py` runs its behaviour assertions against `CORE.read_text()` — the module **file**, in isolation:

```python
behavior = CORE.read_text(encoding="utf-8") + r'''
...
const takeaway=nkSourceTakeaway(q);
```

and then only checks that the module's text is *present* in the assembled page:

```python
if CORE.read_text(encoding="utf-8").rstrip() not in source:
    raise SystemExit("Shipped app must carry the content hygiene core verbatim")
```

Neither assertion runs the assembled page's binding, so the test asserts the module's behaviour while the app runs the other copy.

## Learner impact

Wrong visible information, on a wide scale. The learner loses the "Key takeaway" card entirely on about 1,940 of 10,105 questions (19%) — the card that explains *why* the answer is right. On a further 365 questions the card shows worse text than intended: the inline version can pull a cell out of the opposite column of a comparison table (its own test in the repository asserts that the opposite column must not leak) or a truncated fragment ("The bile esculin test is used to differentiate enterococci (e."). Nothing is scored wrongly and nothing is lost permanently, so this is `medium`, not `high`.

## Root cause

`tools/app_page.py` `assemble()` inlines each module's source into the page at its `/* @module ... */` marker, but nothing checks that the page does not also declare a function the module declares. When the content-hygiene core was extracted into `app/src/main/modules/question_content_hygiene.js`, the older `nkSourceTakeaway` that had been sitting in `index.html` was left behind. Both end up in the page's single IIFE scope, and JavaScript's last-declaration-wins rule silently binds the older copy.

## Proposed fix

Delete the stale inline copy from the page. The module's implementation becomes the only one, and the repository's own `test_question_content_hygiene_v1.py` assertions become true of the shipped app.

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -1440,36 +1440,5 @@
     return navIcon(key==='physiology'?'heart':key==='anatomy'?'body':'dna',20);
   }
 
-  function nkSourceTakeaway(q) {
-    const reviewed=String(q?.keyTakeaway||q?.takeaway||'').replace(/\s+/g,' ').trim();
-    if(reviewed.length>=24) return reviewed;
-    const option=Array.isArray(q?.options)?q.options[Number(q.correctOption)-1]:null;
-    const answer=String(option?.text||'').replace(/\s+/g,' ').trim();
-    let source=String(q?.explanation||'').replace(/\r/g,'\n');
-    if(!answer || !source) return '';
-    source=source
-      .replace(/^\s*Correct\s+(?:Answer|answer|Option)\s*:?\s*[A-E]\)?[^\n]*\n?/i,'')
-      .replace(/^\s*Explanation\s*:?\s*/i,'')
-      .replace(/[•▪◦]\s*/g,' ')
-      .replace(/\s+/g,' ')
-      .trim();
-    const stop=new Set(['this','that','with','from','into','than','then','which','what','when','where','have','has','were','been','being','their','there','about','answer','option','correct']);
-    const tokens=answer.toLowerCase().replace(/[^a-z0-9+]+/g,' ').split(/\s+/).filter(x=>x.length>=4&&!stop.has(x));
-    if(!tokens.length) return '';
-    const sentences=(source.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[])
-      .map(x=>x.replace(/^[-–—:\s]+/,'').replace(/\s*\(Option\s+[A-E]\)\s*/ig,' ').replace(/\s+/g,' ').trim())
-      .filter(x=>x.length>=35&&x.length<=300&&/^[A-Z0-9]/.test(x));
-    let best='',bestScore=0;
-    sentences.forEach(sentence=>{
-      const lower=sentence.toLowerCase();
-      const overlap=tokens.reduce((n,t)=>n+(lower.includes(t)?1:0),0);
-      const exact=answer.length>=5&&lower.includes(answer.toLowerCase())?3:0;
-      const score=overlap+exact-(sentence.length>240?1:0);
-      if(score>bestScore){best=sentence;bestScore=score;}
-    });
-    const needed=tokens.length===1?1:2;
-    return best&&bestScore>=needed?best:'';
-  }
-
   function nkSessionHeader(q,s,mode,timerHtml='',gridAttrs='id="cr-grid" title="Question Navigator" onclick="window.QB.openQuestionNavigator()"',headerClass='practice-focus-head nk-session-head') {
     const total=Math.max(1,s.questionIds.length),position=s.index+1;
     const progress=Math.max(0,Math.min(100,Math.round(position/total*100)));```

Add the guard that would have caught it, in `tools/test_app_source_parity.py` — the file that already owns "the app page lines up with its modules":

```diff
--- a/tools/test_app_source_parity.py
+++ b/tools/test_app_source_parity.py
@@ -14,6 +14,11 @@
 from app_page import HTML, MARKER, MODULES, ROOT, assemble
 
 
+def top_level_functions(text: str) -> set[str]:
+    """Functions the page declares at the top level of its script scope."""
+    return set(re.findall(r"^  function ([A-Za-z_$][\w$]*)\s*\(", text, re.M))
+
+
 def main() -> None:
     page = HTML.read_text(encoding="utf-8")
     named = Counter(MARKER.findall(page))
@@ -23,5 +28,10 @@
     if unused or repeated:
         raise SystemExit(f"each module belongs in index.html once: unused={unused} repeated={repeated}")
     assemble(page)
+    page_functions = top_level_functions(page)
+    for path in sorted(MODULES.glob("*.js")):
+        shadowed = top_level_functions(path.read_text(encoding="utf-8")) & page_functions
+        if shadowed:
+            raise SystemExit(f"{path.name} is shadowed by the page's own copy of: {sorted(shadowed)}")
     if len(page.encode()) > 1024 * 1024:
         raise SystemExit("index.html must not embed question data or module code; use a token or a module")
     subprocess.run([sys.executable, str(ROOT / "tools/build_app_data.py"), "--check"], check=True)```

## Verification

- Reproduce the bug, then the fix:
  1. `python3 -c "import sys; sys.path.insert(0,'tools'); from app_page import app_page; print(app_page().count('function nkSourceTakeaway'))"` → `2` before the fix, `1` after.
  2. Evaluate both copies in one scope (as in Evidence) → before: the resolved function has no `nkTableTakeaway` reference; after: it does.
  3. Re-run the impact scan over the 10,105 shipped questions → the "inline returns EMPTY" count drops from 1,940 to 0 and every question's takeaway matches the module's.
- Existing test to extend: `tools/test_question_content_hygiene_v1.py` already asserts the module's output for a table-shaped explanation; add the same assertion against the **assembled** page, not just `CORE.read_text()`, so the page's effective binding is what is tested. Concretely, change its `behavior` prelude from `CORE.read_text(encoding="utf-8")` to the assembled page's script body, or add a second behaviour block built from `app_source()`.
- Add the parity guard above to `tools/test_app_source_parity.py`, which the build workflow already runs (`tools/test_app_source_parity.py` is step "Check the app page against its tested modules" in `.github/workflows/build-apk.yml`).
- Regressions to re-check: Practice feedback (the takeaway card), Review Solutions grid, Marrow structured explanations (`nkMarrowTakeaway` calls `nkSourceTakeaway` as its fallback), and the protected Practice / Timed CBT / session-review flows.

## Alternatives considered

Renaming the module's function (e.g. `nkHygieneSourceTakeaway`) and calling it explicitly would also work, but it leaves two near-identical implementations in the tree and the stale one still callable. Deleting the dead copy is smaller, removes the ambiguity permanently, and makes the existing repository test describe the shipped behaviour.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Found by the lead and independently verified: the assembled page contains two declarations of nkSourceTakeaway at the same brace depth in the page IIFE (assembled lines 255 and 2808), the later (inline, index.html:1443) wins, and the module version that the repository test asserts against never runs. Measured over all 10,105 shipped questions: 2,354 takeaways differ and 1,940 of them render no takeaway at all. The proposed fix (delete the stale inline copy) and the parity guard in test_app_source_parity.py are both correct. Approved; this is the highest-value finding in the hunt.
