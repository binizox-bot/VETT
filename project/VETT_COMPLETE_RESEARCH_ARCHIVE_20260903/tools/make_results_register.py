#!/usr/bin/env python3
"""Make an evidence-linked handoff table without changing historical scores."""
import argparse
import hashlib
import json
from pathlib import Path

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def ref(w,p): return 'workspace_snapshot/'+p.relative_to(w).as_posix()

ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--delivery',type=Path,required=True)
a=ap.parse_args();w=a.workspace.resolve();d=a.delivery.resolve();e=w/'vett_cricket_pilot_v1/experiments'
p10=e/'v0.15_mainstream_method_check/GPT55_R10_RESULTS.json';pdec=e/'v0.15_mainstream_method_check/GPT55_R10_ERROR_DECOMPOSITION.json'
p12=e/'v0.17_r12_naturalized_multiroot/GPT55_R12_RESULTS.json'
r10=load(p10);dec=load(pdec);r12=load(p12)
records=[]
lines=['# 结果证据登记与可引用表','','这里只集中展示有冻结预测档案的R10/R12关键矩阵。全部其他结果、消融、失败与机械检查见本页末尾的结果文件全集索引及原始JSON。','',
'历史文件声明的模型平台为GPT-5.5；本次检查可验证文件与评分一致性，不重新认证历史服务端模型身份或上下文隔离。','',
'## R10六方法冻结预测','','| 方法 | 严格正确/336 | 严格错误率 | 核心标量错误/232 |','| --- | ---: | ---: | ---: |']
for m,v in r10['methods'].items():
    core=dec['methods'][m]['scalar_core']
    wrong=v['gold_cells']-v['correct']
    lines.append(f'| {m} | {v["correct"]}/{v["gold_cells"]} | {wrong/v["gold_cells"]:.2%} | {core["errors"]}/{core["gold"]} |')
    records.append({'experiment':'R10','method':m,'provenance_kind':'FROZEN_PREDICTION_RESCORE','model_declared':r10.get('model'),'gold_cells':v['gold_cells'],'correct':v['correct'],'errors':wrong,'rate_unit':'fraction','error_rate':wrong/v['gold_cells'],'core_errors':core['errors'],'core_total':core['gold'],'source':ref(w,p10),'decomposition_source':ref(w,pdec),'note':'Archive export rescored all six predictions exactly; no new generation.'})
lines+=['',f'来源：[完整成绩](../{ref(w,p10)})；[误差分解](../{ref(w,pdec)})。严格错误受复合字段和无证据Referee影响。','',
'## R12四方法冻结预测','','| 方法 | 规范值正确/317 | 规范值错误率 | 事实内容错误率（原报告） |','| --- | ---: | ---: | ---: |']
for m,v in r12['methods'].items():
    s=v['aggregate'];errors=s['total']-s['correct']
    lines.append(f'| {m} | {s["correct"]}/{s["total"]} | {errors/s["total"]:.2%} | {s.get("fact_content_error_rate",0):.2f}% |')
    records.append({'experiment':'R12','method':m,'provenance_kind':'HISTORICAL_MODEL_RUN','model_declared':'GPT-5.5 per archived report','gold_cells':s['total'],'correct':s['correct'],'errors':errors,'rate_unit':'fraction','error_rate':errors/s['total'],'source':ref(w,p12),'note':'Archive export checked prediction/public frozen hashes only. Direct branch historical protocol caveat retained.'})
lines+=['',f'来源：[完整成绩](../{ref(w,p12)})；[最终报告与Direct限制说明](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_FINAL_REPORT.md)。','',
'## 其余结果文件全集','','这个索引按文件名检索出结果、评分、自测、消融、审计、决策与冻结资料，保留目录上下文。文件名含方法名并不自动获得模型实测资格。','']
tokens=('result','score','selftest','audit','decision','freeze','ablation','history','iteration','fail')
evidence_files=[]
for p in sorted(e.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in ('.json','.jsonl','.md','.txt'): continue
    if not any(x in p.name.lower() for x in tokens): continue
    rp=ref(w,p);h=hashlib.sha256(p.read_bytes()).hexdigest()
    evidence_files.append({'path':rp,'sha256':h,'bytes':p.stat().st_size})
    lines.append(f'- [{p.relative_to(e).as_posix()}](../{rp})')
(d/'docs/08_RESULT_EVIDENCE_REGISTER.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(d/'manifests/RESULT_EVIDENCE_REGISTER.json').write_text(json.dumps({'normalized_headline_records':records,'all_result_evidence_files':evidence_files,'rate_normalization':'Derived from integer correct/total. Original files remain unchanged.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'headline_records':len(records),'result_evidence_files':len(evidence_files)}))
