#!/usr/bin/env python3
"""Offline smoke tests. Historical inputs stay read-only; outputs are separate.

No model invocation, key inspection, API call, or prediction refreezing occurs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();w=a.workspace.resolve();out=a.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    exp=w/'vett_cricket_pilot_v1/experiments';checks=[]
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    def run(name,args):
        try:
            r=subprocess.run([sys.executable,'-B',*map(str,args)],cwd=w,env=env,capture_output=True,text=True,timeout=45)
            (out/(name+'.log')).write_text(r.stdout+'\nSTDERR\n'+r.stderr,encoding='utf-8')
            checks.append({'check':name,'pass':r.returncode==0,'exit_code':r.returncode})
            return r.returncode==0
        except subprocess.TimeoutExpired:
            checks.append({'check':name,'pass':False,'error':'45-second timeout'});return False

    for name,folder,script in [('r13c_scorer','v0.19_r13c_cricket_conservation','score_r13c_predictions.py'),('r14_scorer','v0.20_r14_field_independent','score_r14_predictions.py')]:
        run(name,[exp/folder/script,'--selftest','--output',out/(name+'.json')])

    r10=exp/'v0.15_mainstream_method_check';r10_data=exp/'v0.14_r10_fourth_root_implicit/instance'
    frozen=read(r10/'GPT55_PREDICTION_FREEZE.json')['prediction_sha256']
    for method,expected in frozen.items():
        p=r10/'runs_gpt55'/(method+'.prediction.json')
        checks.append({'check':'r10_frozen_'+method,'pass':sha(p)==expected})
        target=out/('r10_'+method+'.score.json')
        ok=run('r10_rescore_'+method,[r10/'score_r10_predictions.py','--gold',r10_data/'r10_private_gold.json','--evidence',r10_data/'r10_private_evidence.json','--prediction',p,'--output',target])
        if ok: checks.append({'check':'r10_identical_score_'+method,'pass':read(target)==read(r10/'scores_gpt55'/(method+'.score.json'))})

    r12=exp/'v0.17_r12_naturalized_multiroot';freeze=read(r12/'GPT55_R12_PREDICTION_FREEZE.json')
    checks.append({'check':'r12_public_frozen_hash','pass':sha(r12/'r12_public_blind.jsonl')==freeze['public_sha256']})
    for method,item in freeze['predictions'].items():
        checks.append({'check':'r12_frozen_'+method,'pass':sha(r12/item['path'])==item['sha256']})

    r15=exp/'v0.21_r15_synthetic_dualworld'
    with tempfile.TemporaryDirectory(prefix='vett-export-smoke-') as t:
        t=Path(t);copy=t/'r15_copy';shutil.copytree(r15,copy,ignore=shutil.ignore_patterns('__pycache__'))
        run('r15_scorer',[copy/'selftest_r15_scorer.py'])
        run('r15_release',[copy/'validate_r15_release.py'])
        regenerated=t/'r15_regenerated'
        run('r15_rebuild',[w/'vett_cricket_pilot_v1/scripts/build_r15_synthetic_dualworld.py','--ledger',r15/'construction/match_0031.synthetic_delivery_ledger.json','--output',regenerated])
        for name in ['public_instance.json','private_gold.json','private_evidence.json','R15_SELFTEST.json','blind/r15_blind.jsonl','PUBLIC_PREVIEW.md','PRIVATE_GOLD_PREVIEW.md']:
            p=regenerated/name
            checks.append({'check':'r15_rebuild_identical_'+name,'pass':p.exists() and sha(p)==sha(r15/name)})
    result={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks,'note':'Historical-score reproduction and mechanical tests only; no new model evaluation. R12 checks frozen file hashes, not generation provenance or rescoring.'}
    (out/'SMOKE_TEST_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__': main()
