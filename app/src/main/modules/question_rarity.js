  /* Question rarity: how rare it is to get a question right, from its source's own cohort.
     Tiers are percentile "drop rates" within one source bank, never relative to a subject's
     hardest question: Legendary = hardest ~5%, Great = next ~10%, Rare = next ~30%, Easy = rest.
     Cutoffs are frozen per source (cohorts differ between banks) and recomputed only on large
     imports with tools/compute_rarity_cutoffs.py. A value is the lowest % correct that is NOT
     in the tier, so UWorld Legendary means fewer than 38% answered correctly.
     The tier is shown only after the learner has answered: callers render it in post-answer UI. */
  const NK_RARITY_CUTOFFS={
    version:'2026-10-16',
    UWorld:{legendary:38,great:46,rare:62},   // 1,984 questions: 5.1% / 10.9% / 29.8% / 54.2%
    Marrow:{legendary:26,great:37,rare:58}    // 726 Microbiology questions: 5.1% / 10.1% / 30.7% / 54.1%
  };
  const NK_RARITY_LABELS={legendary:'Legendary',great:'Great',rare:'Rare',easy:'Easy',review:'Low signal'};
  /* percent: % who answered correctly. selection: {letter: % who chose it}. correct: letter.
     Trap: one wrong option drew at least 25% of all learners and 60% of the wrong answers,
     so a shared misconception, not a knowledge gap, made it hard.
     Review: at or below chance with no dominant wrong option; often an ambiguous or miskeyed
     item, so it is never celebrated as Legendary. */
  function nkQuestionRarity(input){
    if(!input||input.percent==null||input.percent==='')return null;
    const percent=Number(input.percent);
    if(!Number.isFinite(percent))return null;
    const cut=NK_RARITY_CUTOFFS[input.source]||NK_RARITY_CUTOFFS.UWorld;
    const selection=input.selection||{};
    const wrong=Object.keys(selection).filter(k=>k!==input.correct&&Number.isFinite(Number(selection[k]))).map(k=>Number(selection[k]));
    const wrongTotal=wrong.reduce((a,b)=>a+b,0),top=wrong.length?Math.max(...wrong):0;
    const share=wrongTotal>0?top/wrongTotal:0;
    const options=Number(input.optionCount)||Object.keys(selection).length||4;
    let tier=percent<cut.legendary?'legendary':percent<cut.great?'great':percent<cut.rare?'rare':'easy';
    const trap=tier!=='easy'&&top>=25&&share>=.6;
    if(percent<=100/options&&!(share>=.5))tier='review';
    return {tier,trap,label:NK_RARITY_LABELS[tier],percent:Math.max(0,Math.min(100,Math.round(percent))),version:NK_RARITY_CUTOFFS.version};
  }
