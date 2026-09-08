from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# This is a Home-only presentation patch. Do not touch the shared shell,
# question renderer, CBT/Practice flows, or navigation APIs.
if 'id="nk-home-streak-header-v1"' in s:
    print('Home streak/header patch already present; no-op.')
    raise SystemExit(0)

# Insert a compact streak directly beneath the Home greeting. currentStreak(),
# dayKey(), and state.attempts are existing canonical data/functions already
# used by the application's streak implementation; no duplicate persistence is
# introduced here.
needle = '            <p>What are you working on today?</p>\n          </div>'
replacement = '''            <p>What are you working on today?</p>
            <div class="nk-home-streak" aria-label="Study streak">
              <div class="nk-home-streak-copy">
                <span class="nk-home-streak-flame" aria-hidden="true">🔥</span>
                <div><strong>${currentStreak()}</strong><span> day${currentStreak()===1?'':'s'} streak</span></div>
              </div>
              <div class="nk-home-streak-week" aria-hidden="true">${(()=>{const days=new Set();for(const a of Object.values(state.attempts||{}))for(const x of a||[])if(x.ts)days.add(dayKey(new Date(x.ts)));const now=new Date(),names=['S','M','T','W','T','F','S'];return Array.from({length:7},(_,i)=>{const d=new Date(now);d.setDate(d.getDate()-(6-i));const done=days.has(dayKey(d));return `<span class="nk-home-streak-day ${done?'done':''} ${i===6?'today':''}">${done?'✓':names[d.getDay()]}</span>`}).join('')})()}</div>
              <span class="nk-home-streak-spark" aria-hidden="true"></span>
            </div>
          </div>'''
if needle not in s:
    raise SystemExit('Home greeting target not found; refusing ambiguous patch.')
s = s.replace(needle, replacement, 1)

css = '''<style id="nk-home-streak-header-v1">
/* Home-only chrome: the shared QBank shell/header is intentionally hidden on
   Home so the greeting owns the visual hierarchy. Other routes are untouched. */
body:has(.nk-home-v4) .topbar{display:none!important}
.nk-home-v4-head{position:relative}
/* Match the Home composition's chiseled, edge-aligned geometry: no pill, no
   floating inset, no excessive whitespace. The streak owns the full content axis. */
.nk-home-streak{position:relative;display:flex;align-items:center;justify-content:space-between;gap:14px;margin:10px 0 0;width:100%;box-sizing:border-box;min-height:66px;padding:9px 13px;border:1px solid #e0e3ea;border-radius:3px;background:#fff;box-shadow:none;overflow:hidden;animation:nkStreakIn .5s cubic-bezier(.2,.75,.25,1) both}
.nk-home-streak:before{content:"";position:absolute;inset:0;background:linear-gradient(105deg,rgba(255,196,74,.09),rgba(255,255,255,0) 58%);pointer-events:none}
.nk-home-streak-copy{position:relative;display:flex;align-items:center;gap:9px;z-index:1}.nk-home-streak-flame{display:grid;place-items:center;width:34px;height:34px;border-radius:4px;background:#fff4d8;font-size:18px;animation:nkFlamePulse 1.8s ease-in-out infinite}.nk-home-streak-copy div{display:flex;align-items:baseline;gap:4px;white-space:nowrap}.nk-home-streak-copy strong{font-size:19px;line-height:1;font-weight:900;letter-spacing:-.5px;color:#303145}.nk-home-streak-copy div span{font-size:10.5px;font-weight:750;color:#777a88}.nk-home-streak-week{position:relative;display:flex;gap:6px;z-index:1}.nk-home-streak-day{width:23px;height:23px;display:grid;place-items:center;border-radius:3px;background:#eff0f4;color:#9699a5;font-size:7.5px;font-weight:850}.nk-home-streak-day.done{background:#fff0c9;color:#c27d16}.nk-home-streak-day.today{box-shadow:inset 0 0 0 2px rgba(61,101,216,.18)}.nk-home-streak-spark{position:absolute;width:6px;height:18px;border-radius:2px;right:8px;top:8px;background:#d9b24d;opacity:.5;animation:nkSpark 2.4s ease-in-out infinite}
@keyframes nkStreakIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}@keyframes nkFlamePulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}@keyframes nkSpark{0%,100%{transform:translate(0,0) scale(.7);opacity:.2}50%{transform:translate(-3px,3px) scale(1);opacity:.65}}
@media(max-width:560px){.nk-home-streak{width:100%;min-height:64px;margin-top:9px;padding:8px 10px;gap:8px}.nk-home-streak-week{gap:4px}.nk-home-streak-day{width:21px;height:21px}.nk-home-streak-copy strong{font-size:18px}.nk-home-streak-flame{width:32px;height:32px}}
@media(prefers-reduced-motion:reduce){.nk-home-streak,.nk-home-streak-flame,.nk-home-streak-spark{animation:none!important}}
</style>'''
s = s.replace('</head>', css + '\n</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('Home streak/header v2 applied: streak is full-width, square/chiseled, aligned to the Home content axis, with subtle motion; shared routes untouched.')
