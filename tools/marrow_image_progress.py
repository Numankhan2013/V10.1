#!/usr/bin/env python3
"""Generate deterministic rollout counts from the reviewed Marrow registry."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from marrow_images import DATA,binding_is_released,validate

DEFAULT_OUTPUT=DATA/'images/progress.json'

def build_progress(value):
    assets=Counter();methods=Counter();kinds=Counter();subjects=defaultdict(Counter)
    bindings=Counter();roles=Counter();released_questions=defaultdict(set);batches=defaultdict(Counter)
    for asset in value['assets']:
        assets[asset['status']]+=1;methods[asset['method']]+=1;kinds[asset['kind']]+=1
        subjects[asset['subject']]['assets']+=1
        if asset['status'] in {'PASS','SOURCE_LIMITED'}:subjects[asset['subject']]['approvedAssets']+=1
        for binding in asset['bindings']:
            status=binding.get('status',asset['status']);bindings[status]+=1
            batch=binding.get('reviewBatch',asset.get('reviewBatch','pilot'))
            batches[batch]['bindings']+=1
            if binding_is_released(asset,binding):
                roles[binding['role']]+=1;released_questions[asset['subject']].add(binding['questionId'])
                batches[batch]['releasedBindings']+=1
            elif status=='REJECTED':batches[batch]['rejectedBindings']+=1
            else:batches[batch]['pendingBindings']+=1
    all_released=set().union(*released_questions.values()) if released_questions else set()
    return {
        'schemaVersion':1,
        'assets':{'total':len(value['assets']),'byStatus':dict(sorted(assets.items())),
                  'byKind':dict(sorted(kinds.items())),'byMethod':dict(sorted(methods.items()))},
        'bindings':{'total':sum(bindings.values()),'byStatus':dict(sorted(bindings.items())),
                    'releasedByRole':dict(sorted(roles.items())),
                    'releasedQuestionCount':len(all_released)},
        'subjects':{s:{**dict(sorted(subjects[s].items())),
                       'releasedQuestions':len(released_questions[s])} for s in sorted(subjects)},
        'batches':{b:dict(sorted(c.items())) for b,c in sorted(batches.items())}
    }

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    value=validate(DATA/'images/registry.json');progress=build_progress(value)
    rendered=json.dumps(progress,indent=2,sort_keys=False)+'\n'
    if args.check:
        assert args.output.read_text()==rendered,'Marrow image progress report is stale'
        print('MARROW_IMAGE_PROGRESS_OK',progress['bindings']['releasedQuestionCount'])
    else:
        args.output.write_text(rendered);print(rendered,end='')

if __name__=='__main__':main()
