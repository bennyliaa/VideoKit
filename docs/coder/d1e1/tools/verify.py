"""Read-only offline verifier; default never builds, executes helpers or opens media."""
import hashlib,json,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    freeze=json.loads((BASE/'evidence/freeze-summary.json').read_text(encoding='utf-8'))
    source=json.loads((BASE/'evidence/source-manifest.json').read_text(encoding='utf-8'))
    for r in freeze['files']+freeze['syntheticFiles']+source['files']:
        p=ROOT/r['path'];assert p.is_relative_to(ROOT) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    with zipfile.ZipFile(BASE/'artifacts/E1-source.zip') as z:
        assert set(z.namelist())=={r['path'] for r in source['files']}
        for r in source['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8'))
    rows=manifest['branches'];assert len(rows)==61 and len({r['id'] for r in rows})==61
    assert sum(r['nonquery'] for r in rows)+16+32==351
    assert sum(r['queriesNew']+r['queriesReplay'] for r in rows)==101
    assert sum(r['inputBytes'] for r in rows)+32==1573522 and sum(r['inputCalls'] for r in rows)+2==59
    assert sum(r['seconds'] for r in rows)+20+20+10+18==180
    for r in rows:assert len(r['operations'])==r['nonquery']
    for path,digest in manifest['inputs'].items():assert sha(ROOT/path)==digest
    result=json.loads((BASE/'evidence/selfcheck.json').read_text(encoding='utf-8'))
    assert result['status']=='PASS' and not result['mediaRead'] and not result['pfRun'] and not result['full61Run']
    assert sum(g.get('assertions',0) for g in result['groups'])+1==result['assertions']
    print(json.dumps({'integrity':'PASS','sourceFiles':len(source['files']),'branches':61,'syntheticAssertions':result['assertions'],
        'syntheticBytes':freeze['syntheticBytes'],'media':'NOT_RUN','implementation':freeze['state'],'freezeSha256':sha(BASE/'evidence/freeze-summary.json')}))
if __name__=='__main__':verify()
