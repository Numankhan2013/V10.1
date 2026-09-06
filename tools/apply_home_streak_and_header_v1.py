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
.nk-home-streak{position:relative;display:flex;align-items:center;gap:12px;margin-top:12px;width:max-content;max-width:100%;padding:7px 10px 7px 8px;border:1px solid #e3e5ed;border-radius:14px;background:rgba(255,255,255,.86);box-shadow:0 5px 18px rgba(43,48,74,.055);overflow:hidden;animation:nkStreakIn .5s cubic-bezier(.2,.75,.25,1) both}
.nk-home-streak:before{content:"";position:absolute;inset:0;background:linear-gradient(105deg,rgba(255,196,74,.12),rgba(255,255,255,0) 58%);pointer-events:none}
.nk-home-streak-copy{position:relative;display:flex;align-items:center;gap:8px;z-index:1}.nk-home-streak-flame{display:grid;place-items:center;width:31px;height:31px;border-radius:10px;background:#fff4d8;font-size:17px;animation:nkFlamePulse 1.8s ease-in-out infinite}.nk-home-streak-copy div{display:flex;align-items:baseline;gap:4px;white-space:nowrap}.nk-home-streak-copy strong{font-size:19px;line-height:1;font-weight:900;letter-spacing:-.5px;color:#303145}.nk-home-streak-copy div span{font-size:10.5px;font-weight:750;color:#777a88}.nk-home-streak-week{position:relative;display:flex;gap:5px;z-index:1}.nk-home-streak-day{width:21px;height:21px;display:grid;place-items:center;border-radius:50%;background:#eff0f4;color:#9699a5;font-size:7.5px;font-weight:850}.nk-home-streak-day.done{background:#fff0c9;color:#c27d16}.nk-home-streak-day.today{box-shadow:0 0 0 2px rgba(61,101,216,.14)}.nk-home-streak-spark{position:absolute;width:7px;height:7px;border-radius:50%;right:7px;top:6px;background:#d9b24d;opacity:.5;animation:nkSpark 2.4s ease-in-out infinite}
@keyframes nkStreakIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}@keyframes nkFlamePulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}@keyframes nkSpark{0%,100%{transform:translate(0,0) scale(.7);opacity:.25}50%{transform:translate(-3px,4px) scale(1);opacity:.7}}
@media(max-width:560px){.nk-home-streak{width:100%;box-sizing:border-box;justify-content:space-between;padding:7px 9px}.nk-home-streak-week{gap:4px}.nk-home-streak-day{width:20px;height:20px}.nk-home-streak-copy strong{font-size:18px}}
@media(prefers-reduced-motion:reduce){.nk-home-streak,.nk-home-streak-flame,.nk-home-streak-spark{animation:none!important}}
</style>'''
s = s.replace('</head>', css + '\n</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('Home streak/header v1 applied: streak directly under greeting, animated micro-graphics, Home-only topbar removal; all shared routes untouched.')
