"""Read-only integrity checks. Never builds or runs helpers or accesses test_media."""
import hashlib,json,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    freeze=json.loads((BASE/'evidence/freeze-summary.json').read_text(encoding='utf-8'));source=json.loads((BASE/'evidence/source-manifest.json').read_text(encoding='utf-8'))
    for r in freeze['files']+freeze['selfcheckFiles']+source['files']:
        p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve()) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    with zipfile.ZipFile(BASE/'artifacts/E1C-source.zip') as z:
        assert set(z.namelist())=={r['path'] for r in source['files']}
        for r in source['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8'));rows=manifest['branches']
    assert len(rows)==61 and sum(r['nonquery'] for r in rows)+48==351
    assert sum(r['queriesNew']+r['queriesReplay'] for r in rows)==101
    assert sum(r['inputBytes'] for r in rows)+32==1573522 and sum(r['inputCalls'] for r in rows)+2==59
    assert sum(r['seconds'] for r in rows)+20+20+10+18==180
    assert manifest['executionOrder'][-2:]==['P10-D','P10-C'] and not manifest['experimentEnabled']
    baselines=json.loads((BASE/'upstream-e1b/preserved-baselines.json').read_text(encoding='utf-8'))
    for r in baselines['files']:assert sha(ROOT/r['path'])==r['sha256']
    for path,digest in manifest['inputs'].items():assert sha(ROOT/path)==digest
    audit=json.loads((BASE/'evidence/audit.json').read_text(encoding='utf-8'));negative=json.loads((BASE/audit['targetedEvidence']).read_text(encoding='utf-8'))
    assert audit['status']==negative['status']=='PASS' and audit['syntheticAssertions']+negative['assertions']==freeze['syntheticAssertions']
    assert manifest['schema']==3 and set(manifest['fixes'])=={'T01','T02','T03','T04','T05'}
    print(json.dumps({'integrity':'PASS','state':freeze['state'],'sourceFiles':len(source['files']),'frozenFiles':len(freeze['files']),'selfcheckFiles':len(freeze['selfcheckFiles']),'syntheticAssertions':freeze['syntheticAssertions'],'preservedBaselines':len(baselines['files']),'freezeSha256':sha(BASE/'evidence/freeze-summary.json'),'media':'NOT_RUN'}))
if __name__=='__main__':verify()
