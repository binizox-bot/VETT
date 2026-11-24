#!/usr/bin/env python3
"""Independently verify every stored file against FULL_MANIFEST (stdlib only)."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

def digest(stream):
    h=hashlib.sha256()
    for chunk in iter(lambda:stream.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def verify_zip(path):
    problems=[]
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        manifests=[n for n in names if n.endswith('/manifests/FULL_MANIFEST.json')]
        if len(manifests)!=1: raise ValueError('Expected exactly one full manifest')
        mf=manifests[0]; root=mf[:-len('manifests/FULL_MANIFEST.json')]
        m=json.loads(z.read(mf))
        expected={root+x['path'] for x in m['files']}|{mf}
        actual={i.filename for i in z.infolist() if not i.is_dir()}
        if expected!=actual: problems.append({'file_set_difference':sorted(expected^actual)})
        if len(names)!=len(set(names)): problems.append('duplicate_archive_paths')
        for x in m['files']:
            name=root+x['path']
            if name not in actual: continue
            with z.open(name) as f: got=digest(f)
            if got!=x['sha256'] or z.getinfo(name).file_size!=x['bytes']: problems.append({'mismatch':x['path']})
        bad=z.testzip()
        if bad: problems.append({'crc_failure':bad})
    with path.open('rb') as f: archive_hash=digest(f)
    return {'status':'PASS' if not problems else 'FAIL','archive_file':path.name,'archive_bytes':path.stat().st_size,'archive_sha256':archive_hash,'hash_verified_files':len(m['files']),'archive_regular_files':len(actual),'manifest_self_exclusion':1,'problems':problems}

def verify_folder(path):
    m=json.loads((path/'manifests/FULL_MANIFEST.json').read_text())
    problems=[]
    for x in m['files']:
        p=path/x['path']
        if not p.is_file(): problems.append({'missing':x['path']});continue
        with p.open('rb') as f: got=digest(f)
        if got!=x['sha256'] or p.stat().st_size!=x['bytes']: problems.append({'mismatch':x['path']})
    return {'status':'PASS' if not problems else 'FAIL','hash_verified_files':len(m['files']),'problems':problems}

ap=argparse.ArgumentParser();ap.add_argument('target',type=Path);ap.add_argument('--output',type=Path)
a=ap.parse_args();result=verify_folder(a.target) if a.target.is_dir() else verify_zip(a.target)
text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
if a.output: a.output.write_text(text,encoding='utf-8')
print(text,end='');raise SystemExit(0 if result['status']=='PASS' else 1)
