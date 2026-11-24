#!/usr/bin/env python3
"""Read-only historical snapshot builder; all new output goes into delivery/zip.

No old experiment is regenerated or overwritten. Standard library only.
"""
from __future__ import annotations
import argparse
import ast
import collections
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import stat
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path

ARCHIVE_ROOT = 'VETT_COMPLETE_RESEARCH_ARCHIVE_20260903'
TEXT_EXT = {'.py','.js','.mjs','.cjs','.md','.txt','.json','.jsonl','.sh','.yaml','.yml','.toml'}

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def dump(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def link(path):
    return urllib.parse.quote(path, safe='/._-')

def collect(workspace, delivery):
    scope=json.loads((delivery/'manifests/EXPORT_SCOPE.json').read_text())
    files=[]; dirs=[]
    for name in scope['source_roots']:
        p=workspace/name
        if not p.exists(): raise RuntimeError('Missing source root: '+str(p))
        if p.is_symlink(): raise RuntimeError('Unresolved symlink: '+str(p))
        if p.is_file(): files.append((p,'workspace_snapshot/'+name))
        else:
            dirs.append('workspace_snapshot/'+name)
            for q in sorted(p.rglob('*')):
                rel='workspace_snapshot/'+q.relative_to(workspace).as_posix()
                if q.is_symlink(): raise RuntimeError('Unresolved symlink: '+str(q))
                if q.is_dir(): dirs.append(rel)
                elif q.is_file(): files.append((q,rel))
                else: raise RuntimeError('Unsupported source type: '+str(q))
    remote=workspace/scope['remote_snapshots_directory']
    for item in scope['saved_artifacts']:
        p=remote/item['path'].lstrip('/')
        if not p.is_file(): raise RuntimeError('Missing saved snapshot: '+str(p))
        if item.get('size_bytes') is not None and p.stat().st_size!=item['size_bytes']:
            raise RuntimeError('Saved snapshot size differs: '+str(p))
        files.append((p,'saved_artifact_snapshots/'+p.relative_to(remote).as_posix()))
    return scope, sorted(files,key=lambda x:x[1]), sorted(set(dirs))

def audit(workspace, delivery):
    (delivery/'docs').mkdir(parents=True,exist_ok=True)
    scope, files, dirs=collect(workspace,delivery)
    manifest=[]; syntax=[]; json_errors=[]; imported=collections.defaultdict(set)
    secrets=[]; path_refs=[]; source_packages=[]; nested_entries=[]
    secret_rx=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}')
    for n,(p,rel) in enumerate(files):
        s=p.stat(); record={'path':rel,'bytes':s.st_size,'sha256':sha(p),'mtime_ns':s.st_mtime_ns,'mode':stat.S_IMODE(s.st_mode)}
        manifest.append(record)
        if p.suffix.lower() in TEXT_EXT:
            raw=p.read_bytes()
            if secret_rx.search(raw): secrets.append(rel)
            if p.name.startswith('.env') or p.name in ('id_rsa','id_ed25519'): secrets.append(rel)
            if rel.startswith('workspace_snapshot/') and not any(x in rel for x in ('__pycache__','stage.','_verify_','verify_v04')):
                try: text=raw.decode('utf-8-sig')
                except UnicodeDecodeError: text=''
                if p.suffix=='.py':
                    try:
                        tree=ast.parse(text)
                        for node in ast.walk(tree):
                            if isinstance(node,ast.Import):
                                for a in node.names: imported[a.name.split('.')[0]].add(rel)
                            if isinstance(node,ast.ImportFrom) and node.module: imported[node.module.split('.')[0]].add(rel)
                    except SyntaxError as e: syntax.append({'path':rel,'line':e.lineno,'error':e.msg})
                if p.suffix in ('.json','.jsonl'):
                    try:
                        if p.suffix=='.json': json.loads(text)
                        else:
                            for ln,t in enumerate(text.splitlines(),1):
                                if t.strip(): json.loads(t)
                    except (ValueError,UnicodeError) as e: json_errors.append({'path':rel,'error':str(e)[:240]})
                for m in re.finditer(r'/workspace/scratch/6024409549bb/[^\s\"\'<>`\)\]]+',text):
                    value=m.group(0).rstrip('.,;:')
                    path_refs.append({'referencing_file':rel,'literal':value,'exists_in_current_workspace':Path(value).exists()})
        if p.suffix.lower()=='.zip':
            try:
                with zipfile.ZipFile(p) as z:
                    bad=z.testzip(); entries=z.infolist()
                    unsafe=[i.filename for i in entries if i.filename.startswith('/') or '..' in Path(i.filename).parts]
                    for i in entries:
                        nested_entries.append({'archive':rel,'member':i.filename,'bytes':i.file_size,'crc32':f'{i.CRC:08x}','directory':i.is_dir()})
                    source_packages.append({'path':rel,'members':len(entries),'uncompressed_bytes':sum(i.file_size for i in entries),'crc_pass':bad is None,'bad_member':bad,'unsafe_member_paths':unsafe})
            except (zipfile.BadZipFile,RuntimeError) as e: source_packages.append({'path':rel,'crc_pass':False,'error':str(e)})
        if n and n%500==0: print('Inventoried',n,'files',flush=True)
    if secrets: raise RuntimeError('Credential-pattern review required in: '+json.dumps(sorted(set(secrets))))
    by_hash=collections.defaultdict(list)
    by_name=collections.defaultdict(list)
    for x in manifest:
        by_hash[x['sha256']].append(x['path'])
        by_name[Path(x['path']).name].append(x)
    reconciliation=[]
    for item in scope['saved_artifacts']:
        candidates=by_name[item['name']]
        remote_record=next(x for x in candidates if x['path'].startswith('saved_artifact_snapshots/'))
        locals_=[x for x in candidates if x['path'].startswith('workspace_snapshot/')]
        reconciliation.append({'name':item['name'],'saved_path':remote_record['path'],'saved_sha256':remote_record['sha256'],'local_matches':[{'path':x['path'],'same_bytes':x['sha256']==remote_record['sha256']} for x in locals_],'status':'MATCHED_LOCAL_BYTES' if any(x['sha256']==remote_record['sha256'] for x in locals_) else ('DIFFERENT_VERSION_PRESERVED' if locals_ else 'RECOVERED_ADDITIONAL_ARTIFACT')})
    experiments=[]
    exp_root=workspace/'vett_cricket_pilot_v1/experiments'
    for d in sorted(exp_root.iterdir(),key=lambda p:tuple(int(x) for x in re.match(r'v([0-9.]+)',p.name).group(1).strip('.').split('.')) if re.match(r'v([0-9.]+)',p.name) else (999,)):
        if not d.is_dir(): continue
        selected=[x for x in manifest if x['path'].startswith('workspace_snapshot/vett_cricket_pilot_v1/experiments/'+d.name+'/')]
        keypaths=[x['path'] for x in selected if re.search(r'(REPORT|SELFTEST|ITERATION|HISTORY|RESULT|FREEZE|FAIL|AUDIT|VALIDATION|README|MANIFEST|PROTOCOL|SCORE)',Path(x['path']).name,re.I) and Path(x['path']).suffix in ('.md','.json','.txt')]
        predictions=[x['path'] for x in selected if 'prediction' in Path(x['path']).name.lower()]
        experiments.append({'experiment':d.name,'path':'workspace_snapshot/vett_cricket_pilot_v1/experiments/'+d.name,'files':len(selected),'bytes':sum(x['bytes'] for x in selected),'key_files':keypaths,'prediction_artifacts':predictions})
    early=[x for x in scope['source_roots'] if x.startswith('2026-') or x.startswith('blind_') or x=='text2table_dataset_blueprint_v1']
    package_versions={}
    for name in ('numpy','scipy','sympy','jsonschema','requests','pandas','pypdf'):
        try: package_versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: package_versions[name]=None
    audit_result={'scope_status':'COMPLETE_FOR_ENUMERATED_EXISTING_FILES','source_roots':len(scope['source_roots']),'source_files':sum(x['path'].startswith('workspace_snapshot/') for x in manifest),'saved_snapshots':len(scope['saved_artifacts']),'all_payload_files':len(manifest),'all_payload_bytes':sum(x['bytes'] for x in manifest),'unique_content_hashes':len(by_hash),'empty_and_nonempty_directories_preserved':len(dirs),'experiments':len(experiments),'historical_zip_files':len(source_packages),'historical_zip_crc_failures':sum(not x['crc_pass'] for x in source_packages),'json_parse_issue_count':len(json_errors),'python_syntax_issue_count':len(syntax),'high_confidence_credential_pattern_count':len(secrets),'saved_reconciliation':dict(collections.Counter(x['status'] for x in reconciliation)),'limitations':scope['limitations']}
    dump(delivery/'manifests/PAYLOAD_MANIFEST.json',{'algorithm':'sha256','files':manifest,'directories':dirs})
    dump(delivery/'manifests/SOURCE_AUDIT.json',audit_result)
    dump(delivery/'manifests/SAVED_SNAPSHOT_RECONCILIATION.json',reconciliation)
    dump(delivery/'manifests/HISTORICAL_ZIP_AUDIT.json',source_packages)
    with (delivery/'manifests/HISTORICAL_ZIP_MEMBERS.jsonl').open('w',encoding='utf-8') as f:
        for x in nested_entries: f.write(json.dumps(x,ensure_ascii=False)+'\n')
    dump(delivery/'manifests/EXPERIMENT_INDEX.json',experiments)
    dump(delivery/'manifests/STATIC_CODE_AUDIT.json',{'python_syntax_issues':syntax,'json_parse_issues':json_errors,'absolute_path_references':path_refs,'imports':{k:sorted(v) for k,v in sorted(imported.items())},'note':'Static parsing only; no historical code was run. JSON issues may be deliberate mutation fixtures.'})
    dump(delivery/'manifests/ENVIRONMENT_OBSERVED.json',{'python':sys.version,'platform':platform.platform(),'packages':package_versions,'note':'Current observed environment, not a historical dependency lock and not a guarantee all generators run.'})
    dump(delivery/'manifests/DUPLICATE_CONTENT_GROUPS.json',[{'sha256':h,'paths':p} for h,p in by_hash.items() if len(p)>1])
    lines=['# 全版本文件入口索引','','按现有目录生成；文件保留旧名称。实验性质和可发表边界见维护文档。','','## 前期试点','']
    for p in early: lines.append(f'- [{p}](../{link("workspace_snapshot/"+p)})')
    lines+=['','## 实验目录','']
    for e in experiments:
        lines += [f'### {e["experiment"]}','','文件数：'+str(e['files'])+'；预测相关文件：'+str(len(e['prediction_artifacts']))+'。','']
        for f in e['key_files']: lines.append(f'- [{Path(f).name}](../{link(f)})')
        lines.append('')
    (delivery/'docs/02_VERSION_FILE_INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    docs=['# 原始文档全集索引','','以下逐项链接覆盖工作区与已保存快照中的Markdown、文本和PDF文档。','','| 文件 | 字节 |','| --- | ---: |']
    for r in manifest:
        if Path(r['path']).suffix.lower() in ('.md','.txt','.pdf'):
            docs.append(f'| [{r["path"]}](../{link(r["path"])}) | {r["bytes"]} |')
    (delivery/'docs/09_DOCUMENT_CATALOG.md').write_text('\n'.join(docs)+'\n',encoding='utf-8')
    print(json.dumps(audit_result,ensure_ascii=False,indent=2),flush=True)
    return files,dirs,audit_result

def make_archive(workspace,delivery,output):
    if output.exists(): raise RuntimeError('Refusing to overwrite archive: '+str(output))
    scope,files,dirs=collect(workspace,delivery)
    expected=json.loads((delivery/'manifests/PAYLOAD_MANIFEST.json').read_text())['files']
    expected_by={x['path']:x for x in expected}
    if set(expected_by)!={r for _,r in files}: raise RuntimeError('Payload scope changed after audit')
    for p,rel in files:
        if sha(p)!=expected_by[rel]['sha256']: raise RuntimeError('Source changed after audit: '+rel)
    # New maintenance files are hashed too. The manifest cannot hash itself.
    all_inputs=files+[(p,p.relative_to(delivery).as_posix()) for p in sorted(delivery.rglob('*')) if p.is_file() and p.name!='FULL_MANIFEST.json']
    records=[{'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)} for p,rel in all_inputs]
    dump(delivery/'manifests/FULL_MANIFEST.json',{'algorithm':'sha256','archive_root':ARCHIVE_ROOT,'files':records,'self_exclusion':'manifests/FULL_MANIFEST.json is covered by archive CRC and the external ZIP SHA256.'})
    all_inputs.append((delivery/'manifests/FULL_MANIFEST.json','manifests/FULL_MANIFEST.json'))
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for d in dirs: z.writestr(ARCHIVE_ROOT+'/'+d+'/',b'')
        for n,(p,rel) in enumerate(all_inputs):
            z.write(p,ARCHIVE_ROOT+'/'+rel)
            if n and n%500==0: print('Archived',n,'files',flush=True)
    print(json.dumps({'archive':str(output),'files':len(all_inputs),'bytes':output.stat().st_size,'sha256':sha(output)},indent=2),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=['audit','build'])
    ap.add_argument('--workspace',type=Path,required=True)
    ap.add_argument('--delivery',type=Path,required=True)
    ap.add_argument('--archive',type=Path)
    a=ap.parse_args()
    if a.mode=='audit': audit(a.workspace.resolve(),a.delivery.resolve())
    else:
        if not a.archive: ap.error('--archive required')
        make_archive(a.workspace.resolve(),a.delivery.resolve(),a.archive.resolve())

if __name__=='__main__': main()
