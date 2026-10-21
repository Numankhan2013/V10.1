# BUG-04-001 — Revision browse search only matches the full typed phrase

- **Area:** 04 navigation & UI
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/modules/revision_desk.js:118`, `app/src/main/modules/revision_desk.js:124`, `app/src/main/modules/revision_desk.js:130-135`
- **Introduced by:** unknown

## What happens

On the Revision "Mistakes"/"Bookmarks" browse screens, typing more than one word (for example "anatomy prep") shows no results even when questions match both words separately. Only a single contiguous phrase is tested against each question.

## Evidence

`nkRevisionBrowsePage` computes one `term` and hides a row unless `raw.includes(term)`:

```
const query=nkRevisionBrowseQueries[kind]||'',term=query.trim().toLowerCase();let shown=0;
...
const id=encodeURIComponent(String(q.id)),raw=(meta+' '+(q.question||'')).toLowerCase(),search=esc(raw),hidden=Boolean(term)&&!raw.includes(term);
```

`nkFilterRevisionBrowse` does the same single-string test:

```
const term=String(value||'').trim().toLowerCase();let shown=0;
document.querySelectorAll('.nk-revision-item').forEach(item=>{item.hidden=Boolean(term)&&!item.dataset.revisionSearch.includes(term);if(!item.hidden)shown++;});
```

By contrast, `question_search.js` splits the query into words and requires every word (`words.every(word=>entry.text.includes(word))`), so the inconsistency is visible.

## Learner impact

A learner who types two words while browsing saved mistakes/bookmarks gets a false "No questions match your search" result; the workaround is to search one word at a time. No data loss.

## Root cause

The browse filter uses substring containment of the entire trimmed query instead of tokenising it like the question search screen.

## Proposed fix

Tokenise the query in both the server-rendered browse page and the live filter, requiring every word.

```diff
--- a/app/src/main/modules/revision_desk.js
+++ b/app/src/main/modules/revision_desk.js
@@ -115,13 +115,13 @@
     if(!['wrong','bookmarks'].includes(kind))return nkRevisionDeskPage();
     const account=String(typeof nkAuth!=='undefined'&&nkAuth?.uid||'local');
     if(account!==nkRevisionBrowseAccount){nkRevisionBrowseQueries={wrong:'',bookmarks:''};nkRevisionBrowseAccount=account;}
-    const query=nkRevisionBrowseQueries[kind]||'',term=query.trim().toLowerCase();let shown=0;
+    const query=nkRevisionBrowseQueries[kind]||'',term=query.trim().toLowerCase(),terms=term.split(/\s+/).filter(Boolean);let shown=0;
     const data=nkRevisionDeskData(),rows=kind==='wrong'?data.wrong:data.bookmarked;
     const title=kind==='wrong'?'Mistakes':'Bookmarks';
     return shell('<main class="nk-app-v114 nk-revision-browse"><header class="nk-v3-page-hero"><button class="nk-back-link" onclick="window.QB.nav(\'quick-revision\')">'+navIcon('back',17)+' Revision</button><div class="nk-kicker">'+esc(nkRevisionScopeLabel())+'</div><h1>'+title+'</h1><p>'+fmtNum(rows.length)+' questions · search by question, subject, bank, or topic.</p></header><label class="nk-revision-search"><span aria-hidden="true">'+navIcon('search',20)+'</span><input type="search" value="'+esc(query)+'" aria-label="Search questions" placeholder="Search questions, subjects, banks" oninput="window.QB.nkFilterRevisionBrowse(this.value)"></label><section class="nk-revision-browse-list">'
       +(rows.length?rows.map(q=>{
         const topic=q.chapter||q.topic||'',meta=[q.subject||'',q.bank||'',topic].filter(Boolean).join(' · ');
-        const id=encodeURIComponent(String(q.id)),raw=(meta+' '+(q.question||'')).toLowerCase(),search=esc(raw),hidden=Boolean(term)&&!raw.includes(term);if(!hidden)shown++;
+        const id=encodeURIComponent(String(q.id)),raw=(meta+' '+(q.question||'')).toLowerCase(),search=esc(raw),hidden=Boolean(terms.length)&&!terms.every(word=>raw.includes(word));if(!hidden)shown++;
         return '<article class="nk-revision-item"'+(hidden?' hidden':'')+' data-revision-search="'+search+'"><small>'+esc(meta)+'</small><p>'+esc(q.question||'Question text unavailable')+'</p><button type="button" onclick="window.QB.nkOpenRevisionQuestion(\''+id+'\')">Open question '+navIcon('chevron',16)+'</button></article>';
       }).join(''):nkAppEmpty(kind==='wrong'?'refresh':'bookmark',kind==='wrong'?'No mistakes to review':'No bookmarks yet',kind==='wrong'?'Incorrect answers from every subject and bank will appear here.':'Bookmarks from every subject and bank will appear here.'))
       +'</section><p class="nk-revision-no-match" role="status"'+(shown||!rows.length?' hidden':'')+'>No questions match your search.</p></main>','quick-revision');
@@ -129,7 +129,7 @@
 
   function nkFilterRevisionBrowse(value){
     if(['wrong','bookmarks'].includes(route.id))nkRevisionBrowseQueries[route.id]=String(value||'');
-    const term=String(value||'').trim().toLowerCase();let shown=0;
-    document.querySelectorAll('.nk-revision-item').forEach(item=>{item.hidden=Boolean(term)&&!item.dataset.revisionSearch.includes(term);if(!item.hidden)shown++;});
+    const term=String(value||'').trim().toLowerCase(),terms=term.split(/\s+/).filter(Boolean);let shown=0;
+    document.querySelectorAll('.nk-revision-item').forEach(item=>{const haystack=item.dataset.revisionSearch||'';item.hidden=Boolean(terms.length)&&!terms.every(word=>haystack.includes(word));if(!item.hidden)shown++;});
     const empty=document.querySelector('.nk-revision-no-match');if(empty)empty.hidden=shown>0;
   }
 ```

## Verification

- Manual: open Revision → Mistakes, type "anatomy prep"; matching rows stay visible; unrelated rows hide; empty message appears only when no row matches all words.
- Existing test: `python3 tools/test_revision_desk_v1.py` should be extended to assert multi-word filtering hides non-matching rows.

## Alternatives considered

Splitting only in the live filter would leave the initial server-rendered `hidden` attributes wrong on first paint; both sites must change together.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified revision_desk.js: the browse page and nkFilterRevisionBrowse both test raw.includes(term) with the whole trimmed query, while question_search.js tokenises and requires every word. The diff tokenises both paths. Approved.
/root/bug-hunt/base/.project-memory/bug-hunt/04-navigation-ui/BUG-04-002-notes-search-whole-phrase-only.md