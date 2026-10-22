# BUG-03-001 — UWorld question-block figures: reported as non-essential, but the finding is withdrawn

- **Area:** 03 question rendering
- **Severity:** none — the reported defect does not exist
- **Confidence:** high (in the withdrawal)
- **Status:** rejected by the lead review — the reported defect does not exist; no fix applied
- **Files:** `app/src/main/modules/uworld_biochemistry.js:88`, `app/src/main/modules/uworld_biochemistry.js:105`, `app/src/main/modules/uworld_biochemistry.js:186`, `app/src/main/modules/uworld_biochemistry.js:205`, `tools/uworld_reviewed_document.py:47`, `tools/uworld_reviewed_document.py:84`
- **Introduced by:** unknown

## What happens (as reported)

A UWorld question whose stem contains a source figure (a `question_blocks` entry of type `figure`) was reported to render that figure with `data-uworld-essential="false"`. The answer buttons for such a question are gated on `nkUworldMediaReady`, which only counts images carrying `data-uworld-essential="true"`, so the buttons would stay disabled and the question could never be answered.

**The lead review found this does not happen.** Every question-block figure carries `role: 'question'`, and the renderer's existing expression already marks it essential. The file is kept because the underlying coupling is worth recording, and because the withdrawn patch it proposed would have caused the very regression it claimed to prevent.

## Evidence

### The reported claim

The reviewer read the essential flag in `app/src/main/modules/uworld_biochemistry.js:49` as option-figures-only:

```js
const img=`<img src="${esc(nkUworldAssetUrl(node.asset))}" alt="${esc(caption)}" loading="eager" decoding="async" data-uworld-essential="${option||node.role==='question'?'true':'false'}" data-uworld-qid="${esc(q.id)}">`;
```

and concluded that question-block figures reach `nkUworldFigureMarkup` with `node.role` undefined, so the expression yields `"false"`. `nkUworldRequiredAssets` (line 205) does list question-block figures, so the two would disagree.

### Why the claim does not hold

Every question-block figure carries `role: 'question'`. This is enforced by the build, not left to chance: `tools/uworld_reviewed_document.py:84` validates each `question_blocks` node with

```python
for node in doc.get('question_blocks', []):
    validate_node(node, qid, pages, 'question', pdf_sha, page_size, ext)
```

and `validate_node` rejects any figure whose role does not match (line 47):

```python
elif kind == 'figure':
    bbox = node.get("bbox")
    if node.get("page") not in pages or node.get("role") != role or not isinstance(bbox, list) or len(bbox) != 4:
        raise ValueError("Invalid reviewed figure provenance: " + qid)
```

So a question-block figure cannot reach the app without `role: 'question'`.

Across all 85 reviewed batch files in `data/uworld/prepared/*/reviewed/` (read out of git, because the UWorld source tree is not present in this sparse checkout):

```
question_blocks node kinds: {'table': 9, 'paragraph': 11, 'figure': 496}
question-block figure roles: {'question': 496}
explanation figure roles: {'explanation': 3961}
question-block figures NOT marked role=question: 0
```

All 496 question-block figures carry `role: 'question'`; all 3,961 explanation figures carry `role: 'explanation'`.

### Runtime confirmation

Rendering a question-block figure and an explanation figure through the shipped `nkUworldFigureMarkup`:

```
question-block figure markup:
  <figure class="nk-uworld-figure"><button type="button" aria-label="Enlarge source figure" ...><img src="./uworld_data/a.png" ...>
  essential=true ? true
explanation figure essential=true ? false
```

The question-block figure is already essential and the explanation figure is correctly not — the intended behaviour.

## Learner impact

None. The reported impact (permanently unanswerable UWorld questions) does not occur: the answer buttons are gated on an image that is already marked essential, so they enable once the figure loads, exactly as for an option figure.

## Root cause

No defect. The residual observation is a coupling one: the renderer's essential flag is derived from the source record's `role` field rather than from the slot the figure is rendered into. That works today only because the build validates the two agree, so the renderer depends on a field the renderer does not control.

## Proposed fix

None applied. The reported patch is withdrawn — see the main-agent review, which shows it would have introduced the defect it claimed to fix.

If the coupling is worth hardening, the correct form is to derive the flag from the caller's slot and thread it through the figure branch of `nkUworldNodes` — which the reported patch did not do:

```diff
--- a/app/src/main/modules/uworld_biochemistry.js
+++ b/app/src/main/modules/uworld_biochemistry.js
@@ -44,9 +44,9 @@
   nkModuleSelectedRecords=function(draft){return nkUworldOriginalModuleRecords(nkUworldLegacyScope(draft));};
   // Presentation adapter only. The incumbent engine owns answer commits and FSRS.
   function nkUworldAssetUrl(asset){return (location.hostname==='qbank.local'?'/app/':'./')+asset;}
-  function nkUworldFigureMarkup(node,q,option=false){
+  function nkUworldFigureMarkup(node,q,option=false,essential=false){
     const caption=node.caption||'Source figure';
-    const img=`<img src="${esc(nkUworldAssetUrl(node.asset))}" alt="${esc(caption)}" loading="eager" decoding="async" data-uworld-essential="${option||node.role==='question'?'true':'false'}" data-uworld-qid="${esc(q.id)}">`;
+    const img=`<img src="${esc(nkUworldAssetUrl(node.asset))}" alt="${esc(caption)}" loading="eager" decoding="async" data-uworld-essential="${option||essential?'true':'false'}" data-uworld-qid="${esc(q.id)}">`;
     if(option)return `<span class="nk-uworld-option-figure">${img}</span>`;
     return `<figure class="nk-uworld-figure"><button type="button" aria-label="Enlarge source figure" onclick="window.QB.uworldFigure(${esc(JSON.stringify(String(node.asset)))})">${img}<span>${navIcon('search',16)} Enlarge</span></button>${node.caption||node.source_note?`<figcaption>${nkScientificMarkup(node.caption||'')}${node.source_note?`<span class="nk-uworld-source-note">${nkScientificMarkup(node.source_note)}</span>`:''}</figcaption>`:''}</figure>`;
   }
@@ -62,7 +62,7 @@
   function nkUworldTable(node){
     return `<figure class="nk-uworld-table">${node.caption?`<figcaption>${nkScientificMarkup(node.caption)}</figcaption>`:''}<div class="nk-uworld-table-scroll" role="region" aria-label="${esc(node.caption||'Source table')}" tabindex="0"><table><thead><tr>${node.columns.map(c=>`<th scope="col">${nkScientificMarkup(c)}</th>`).join('')}</tr></thead><tbody>${node.rows.map(row=>`<tr>${row.map((cell,i)=>i?`<td>${nkScientificMarkup(cell)}</td>`:`<th scope="row">${nkScientificMarkup(cell)}</th>`).join('')}</tr>`).join('')}</tbody></table></div></figure>`;
   }
-  function nkUworldNodes(nodes,q){
+  function nkUworldNodes(nodes,q,essentialFigures=false){
     let discussion=false,heading=false;
     const out=[];
     const blocks=nodes||[];
@@ -79,7 +79,7 @@
         out.push(`<article class="nk-uworld-choice-discussion"><h4>${nkScientificMarkup('Choice'+(/^(?:[A-I])$/.test(choice[1])?'':'s')+' '+choice[1])}</h4><p>${nkScientificMarkup(choice[2])}</p></article>`);
       }else{
         if(discussion){out.push('</section>');discussion=false;}
-        out.push(node.type==='table'?nkUworldTable(node):node.type==='figure'?nkUworldFigureMarkup(node,q):nkUworldParagraph(node.text));
+        out.push(node.type==='table'?nkUworldTable(node):node.type==='figure'?nkUworldFigureMarkup(node,q,false,essentialFigures):nkUworldParagraph(node.text));
       }
     }
     if(discussion)out.push('</section>');return out.join('');
@@ -109,7 +109,7 @@
     const imageOptions=(q.options||[]).filter(o=>o.figure);
     const tools=imageOptions.length?`<details class="nk-uworld-option-tools"><summary>Enlarge option diagrams</summary><div>${imageOptions.map(o=>`<button type="button" aria-label="Enlarge option ${esc(o.letter)}" onclick="window.QB.uworldFigure(${esc(JSON.stringify(String(o.figure.asset)))})">${esc(o.letter)} ${navIcon('search',16)}</button>`).join('')}</div></details>`:'';
     const displayQuestion=q.uworldDocument?{...q,question:q.uworldDocument.question}:q;
-    return `<div class="nk-uworld-stem">${nkUworldOriginalStem(displayQuestion)}${nkUworldNodes(q.uworldDocument?.question_blocks,q)}${tools}</div>`;
+    return `<div class="nk-uworld-stem">${nkUworldOriginalStem(displayQuestion)}${nkUworldNodes(q.uworldDocument?.question_blocks,q,true)}${tools}</div>`;
   };
   const nkUworldOriginalSupport=nkStudySupport;
   nkStudySupport=function(q,timeMs,unattempted=false,renderedSource=''){
```

The middle hunk is the one the reported patch omitted; without it the new flag is never used and every question-block figure becomes non-essential.

## Verification

- Render a question-block figure and an explanation figure through `nkUworldFigureMarkup` and assert `data-uworld-essential="true"` for the first and `"false"` for the second. That is the check that would have caught the reported finding before it was filed.
- Existing tests: `tools/test_uworld_runtime_v1.py`, `tools/verify_uworld_biochemistry_browser.py`.

## Alternatives considered

None. The defect does not exist; the reported fix is harmful.

## Main-agent review

- **Verdict:** flagged
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** REJECTED — the finding's premise is false, and the proposed patch would have introduced a regression.

The premise is that a question-block figure reaches `nkUworldFigureMarkup` with `node.role` undefined, so the expression `${option||node.role==='question'?'true':'false'}` yields "false". In fact every question-block figure carries `role: 'question'`, and the existing expression already marks it essential.

Evidence from the shipped reviewed data (all 85 reviewed batch files, read out of git because the UWorld source tree is not in this sparse checkout):

```
question_blocks node kinds: {'table': 9, 'paragraph': 11, 'figure': 496}
question-block figure roles: {'question': 496}
explanation figure roles: {'explanation': 3961}
question-block figures NOT marked role=question: 0
```

All 496 question-block figures across all 85 reviewed batches carry `role: 'question'`. This is enforced at build time, not accidental: `tools/uworld_reviewed_document.py:84` validates every `question_blocks` node with `validate_node(node, qid, pages, 'question', ...)`, and `validate_node` raises "Invalid reviewed figure provenance" unless `node.get('role') == role` (line 47). A question-block figure therefore cannot reach the app without `role: 'question'`.

Runtime confirmation on the shipped module, rendering a question-block figure and an explanation figure through the real `nkUworldFigureMarkup`:

```
question-block figure markup:
  <figure class="nk-uworld-figure"><button type="button" aria-label="Enlarge source figure" ...><img src="./uworld_data/a.png" ...>
  essential=true ? true
explanation figure essential=true ? false
```

The question-block figure is already essential and the explanation figure is correctly not, which is exactly the intended behaviour.

The proposed patch would have made things worse. It replaces `node.role==='question'` with a new `essential` argument, but the `essentialFigures` parameter it adds to `nkUworldNodes` is never read: the figure branch still calls `nkUworldFigureMarkup(node,q)` with only two arguments, so `option` is false and `essential` defaults to false. Every question-block figure would then be marked `data-uworld-essential="false"` — the exact defect the finding claims to fix, and a genuine regression that would make 496 figure-bearing UWorld questions unanswerable. The patch was applied to the working tree, tested, and reverted; `git status` is clean for that file.

The residual, real observation behind the finding is worth keeping, but it is not a bug: the renderer's essential flag is derived from the source record's `role` field rather than from the slot the figure is rendered into. That coupling works today because the build validates the two agree. A future renderer that reuses `nkUworldFigureMarkup` for a question-role figure outside `question_blocks` would have to pass the flag explicitly, so the defensive change — honouring the caller's slot rather than the source record's field — is still worth making. It should be proposed as a small robustness change, not as a fix for unanswerable questions, and it must actually thread the flag through the `nkUworldNodes` figure branch. The Proposed fix section above carries that corrected form. No fix was applied on this branch for this finding.
