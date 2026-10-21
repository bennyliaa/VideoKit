"""Default verify/help are read-only. Only explicit pack writes this metadata overlay."""
from pathlib import Path
import argparse,hashlib,json,shlex,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def pin(p):raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def verify(expected=None):
    path=B/'evidence/e13b-freeze.json'
    if not path.is_file():return {'status':'NOT_FROZEN','writes':0},2
    sealpin=pin(path)
    if expected:assert sealpin['sha256']==expected,'EXTERNAL_SEAL_SHA'
    seal=json.loads(path.read_text());rows=seal['immutableFiles'];assert len(rows)==len({x['path'] for x in rows})
    for row in rows:check(row)
    members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
    with zipfile.ZipFile(R/seal['archive']['path']) as z:
        assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
        for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    for base in seal['priorSeals']:
        check(base['seal'])
        for row in json.loads((R/base['seal']['path']).read_text())['immutableFiles']:check(row)
    reuse=json.loads((B/'release/overlay-binding.json').read_text())
    for row in reuse['baseArtifacts']:check(row)
    jar_manifest=R/'docs/coder/d1e13a/evidence/host-jar-manifest.json';data=json.loads(jar_manifest.read_text());check(data['jar'])
    with zipfile.ZipFile(R/data['jar']['path']) as z:
        assert len(z.namelist())==len(data['classes'])==len(set(z.namelist()))
        assert set(z.namelist())=={r['entry'] for r in data['classes']}
        for row in data['classes']:raw=z.read(row['entry']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    m=json.loads((B/'release/metadata/three-client-manifest.json').read_text())
    assert len(m['clients'])==3 and m['budgetPcTotal']==48 and m['budgetTextTotal']==2097152
    reader=(B/'tools/processes_reader.sh').read_text()
    for c in m['clients']:
        check(c['script']);script=(R/c['script']['path']).read_text();assert shlex.split(c['argv'][-1])==[script]
        assert script.count(reader)==1 and script.count('if dumpsys activity processes 2>&1;')==1
        assert 'dumpsys activity instrumentation' not in script and 'awk ' not in script
        assert c['recordOutputUpperBound']<=65536 and c['originalPcClients']==1
    return {'status':'PASS_E13B_STRICT_READONLY_VERIFY','writes':0,'archive':seal['archive'],'externalSeal':sealpin,'archiveEntries':len(members),'immutableRows':len(rows),'baseJarClasses':len(data['classes']),'priorSeals':seal['priorSeals'],'baseArtifactsReused':4,'productBuilds':0,'deviceCalls':0},0
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
    if a.mode=='pack':
        if a.seal_sha:p.error('--seal-sha belongs to verify')
        import runpy
        runpy.run_path(str(B/'tools/_pack_overlay.py'),run_name='__main__');return
    result,code=verify(a.seal_sha);print(json.dumps(result,ensure_ascii=False));raise SystemExit(code)
if __name__=='__main__':main()
