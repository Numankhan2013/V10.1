"""Question rarity: per-source percentile tiers, trap and low-signal rules, post-answer chip."""
import json, subprocess
from pathlib import Path
from app_page import app_source
ROOT = Path(__file__).resolve().parents[1]
core = (ROOT / 'app/src/main/modules/question_rarity.js').read_text()
script = core + r'''
const r=(o)=>nkQuestionRarity(o);
const cases={
  legendary:r({source:'UWorld',percent:37,correct:'A',selection:{A:37,B:30,C:20,D:13}}),
  great:r({source:'UWorld',percent:38,correct:'A',selection:{A:38,B:20,C:22,D:20}}),
  rare:r({source:'UWorld',percent:61,correct:'A',selection:{A:61,B:13,C:13,D:13}}),
  easy:r({source:'UWorld',percent:62,correct:'A',selection:{A:62,B:30,C:4,D:4}}),
  trap:r({source:'UWorld',percent:40,correct:'C',selection:{A:5,B:45,C:40,D:10}}),
  review:r({source:'UWorld',percent:24,correct:'A',selection:{A:24,B:26,C:25,D:25},optionCount:4}),
  chanceTrap:r({source:'UWorld',percent:17,correct:'A',selection:{A:17,B:54,C:10,D:10,E:9},optionCount:5}),
  marrow:r({source:'Marrow',percent:25,correct:'A',selection:{A:25,B:60,C:10,D:5}}),
  marrowGreat:r({source:'Marrow',percent:30,correct:'A',selection:{A:30,B:40,C:20,D:10}}),
  missing:r({source:'UWorld',percent:null})
};
console.log(JSON.stringify(cases));
'''
out = json.loads(subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True).stdout)
assert out['legendary']['tier'] == 'legendary' and out['great']['tier'] == 'great'
assert out['rare']['tier'] == 'rare' and out['easy']['tier'] == 'easy' and not out['easy']['trap']
assert out['trap']['tier'] == 'great' and out['trap']['trap'] is True
assert out['review']['tier'] == 'review' and out['review']['label'] == 'Low signal'
assert out['chanceTrap']['tier'] == 'legendary' and out['chanceTrap']['trap'] is True
assert out['marrow']['tier'] == 'legendary' and out['marrowGreat']['tier'] == 'great'
assert out['missing'] is None
page = app_source()
assert page.count('function nkQuestionRarity(') == 1
assert page.index('function nkQuestionRarity(') < page.index('function nkUworldStatistics(')
assert 'data-nk-tier="${rarity.tier}"' in page
feel = (ROOT / 'app/src/main/assets/redesign/nk-feel.js').read_text()
assert "c.getAttribute('data-nk-tier')" in feel and 'nkr-tier' in feel
assert '@media (prefers-reduced-motion: reduce)' in page and '.is-legendary' in page
print('QUESTION_RARITY_OK tiers/trap/low-signal/per-source/post-answer')
