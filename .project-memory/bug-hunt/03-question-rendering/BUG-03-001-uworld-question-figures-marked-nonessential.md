# BUG-03-001 — UWorld question-block figures are marked non-essential, so questions that need them can never be answered

- **Area:** 03 question rendering
- **Severity:** high
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/modules/uworld_biochemistry.js:88`, `app/src/main/modules/uworld_biochemistry.js:105`, `app/src/main/modules/uworld_biochemistry.js:186`, `app/src/main/modules/uworld_biochemistry.js:205`
- **Introduced by:** unknown

## What happens

A UWorld question whose stem contains a source figure (a `question_blocks` entry of type `figure`) renders that figure with `data-uworld-essential="false"`. The answer buttons for that question are gated on `nkUworldMediaReady`, which only counts images carrying `data-uworld-essential="true"`. Because the figure is required (it is included in `nkUworldRequiredAssets`) but never counted as ready, the buttons stay disabled and the question cannot be answered even after the image loads successfully.

## Evidence

`nkUworldRequiredAssets` (line 205) includes question-block figures:

```js
function nkUworldRequiredAssets(q){return [...(q?.uworldDocument?.question_blocks||[]).filter(n=>n.type==='figure'),...(q.options||[]).map(o=>o.figure).filter(Boolean)].map(n=>n.asset);}
```

`nkUworldMediaReady` (line 208) only accepts essential images:

```js
const images=[...document.querySelectorAll('img[data-uworld-essential="true"]')].filter(img=>img.dataset.uworldQid===String(q.id));
return required.every(asset=>images.some(img=>img.getAttribute('src').split('?')[0].endsWith(asset)&&img.complete&&img.naturalWidth>0));
```

But `nkUworldFigureMarkup` (line 186) marks a figure essential only for option figures:

```js
const img=`<img src="${esc(nkUworldAssetUrl(node.asset))}" alt="${esc(caption)}" loading="eager" decoding="async" data-uworld-essential="${option||node.role==='question'?'true':'false'}" data-uworld-qid="${esc(q.id)}">`;
```

Question-block figures are rendered through `nkUworldNodes(q.uworldDocument?.question_blocks,q)` (line 105) with no `essential` argument, so `option` is falsy and `node.role` is undefined, yielding `"false"`. Explanation figures correctly stay non-essential, but they are not in `nkUworldRequiredAssets`, so the mismatch only affects question-block figures.

## Learner impact

For any UWorld question whose stem includes a figure, answering is permanently disabled (or, in a test, the question is filtered out by `nkUworldEligible` only if invalid; valid diagram questions become unanswerable). This is a wrong/blocked flow, not cosmetic.

## Root cause

The essential flag in `nkUworldFigureMarkup` is derived from the `option` parameter plus a `node.role` property that is never set on question-block nodes. The renderer never communicates that a figure belongs to the question stem (as opposed to the explanation), so the media-readiness gate cannot see it.

## Proposed fix

Thread an `essentialFigures` flag through `nkUworldNodes` and pass `true` for question-block rendering; keep explanation rendering non-essential.

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
@@ -109,6 +109,6 @@
     const imageOptions=(q.options||[]).filter(o=>o.figure);
     const tools=imageOptions.length?`<details class="nk-uworld-option-tools"><summary>Enlarge option diagrams</summary><div>${imageOptions.map(o=>`<button type="button" aria-label="Enlarge option ${esc(o.letter)}" onclick="window.QB.uworldFigure(${esc(JSON.stringify(String(o.figure.asset)))})">${esc(o.letter)} ${navIcon('search',16)}</button>`).join('')}</div></details>`:'';
     const displayQuestion=q.uworldDocument?{...q,question:q.uworldDocument.question}:q;
-    return `<div class="nk-uworld-stem">${nkUworldOriginalStem(displayQuestion)}${nkUworldNodes(q.uworldDocument?.question_blocks,q)}${tools}</div>`;
+    return `<div class="nk-uworld-stem">${nkUworldOriginalStem(displayQuestion)}${nkUworldNodes(q.uworldDocument?.question_blocks,q,true)}${tools}</div>`;
   };
   const nkUworldOriginalSupport=nkStudySupport;
   nkStudySupport=function(q,timeMs,unattempted=false,renderedSource=''){```

## Verification

- Render a UWorld question whose `uworldDocument.question_blocks` contains a figure; confirm `img[data-uworld-essential="true"]` is present and `nkUworldMediaReady(q)` becomes true after load, enabling options.
- Existing `tools/test_uworld_runtime_v1.py` should be extended with a case where `question_blocks` contains a figure and assert `nkUworldMediaReady` true once the image is complete.

## Alternatives considered

Marking every figure essential would also gate explanation figures and block answering on explanation images that are not required; threading the flag keeps the explanation path non-blocking.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified uworld_biochemistry.js:49 (data-uworld-essential is true only for option figures or node.role==='question'), :82 (question-block figures render through nkUworldFigureMarkup(node,q) with no essential argument), :123 (nkUworldMediaReady counts only img[data-uworld-essential="true"]) and the required-asset list, which does include question_blocks figures. The mismatch is real and the fix makes the stem figure essential. Approved: a question whose stem needs a figure is otherwise permanently unanswerable.
