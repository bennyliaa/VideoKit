"""Explicit packaging only; no builds, media access or helper launches."""
import argparse, hashlib, json, zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def freeze():
    assert not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_IS_READ_ONLY'
    sources=sorted(p for folder in ('src','tools','manifest','upstream-e1b') for p in (BASE/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    source={'scope':'E1C_SOURCE_AND_UPSTREAM_RELATION','files':[record(p) for p in sources]}
    (BASE/'evidence/source-manifest.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(BASE/'artifacts/E1C-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sources:
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,10,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
    docs=[ROOT/'docs/coder'/('D1_E1C_'+name+'_V1.0.md') for name in ('DELIVERY','IMPLEMENTATION_BOUNDARY','EXECUTION_APPENDIX')]
    files=sorted([p for p in (BASE/'artifacts').rglob('*') if p.is_file()]+[p for p in (BASE/'evidence').glob('*') if p.is_file()]+docs)
    checks=sorted(p for p in (BASE/'selfcheck').rglob('*') if p.is_file());fixtures=[p for p in checks if p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out']
    fixturebytes=sum(p.stat().st_size for p in fixtures);logbytes=sum(p.stat().st_size for p in checks if p not in fixtures)+sum(p.stat().st_size for p in files if 'evidence' in p.parts)
    assert fixturebytes<=2097152 and logbytes<=4194304
    audit=json.loads((BASE/'evidence/audit.json').read_text(encoding='utf-8'));assert audit['status']=='PASS'
    result={'candidate':'D1-E1C-20261016','state':'T01_T05_FIXED_SYNTHETIC_VERIFIED_PENDING_INDEPENDENT_REVIEW','runtime':'PowerShell 7.6.5 / .NET 10.0.11 / JDK 21.0.10','files':[record(p) for p in files],'selfcheckFiles':[record(p) for p in checks],'syntheticFixtureBytes':fixturebytes,'logsAndEvidenceBytesBeforeSeal':logbytes,'upstreamFreezeSha256':sha(BASE/'upstream-e1b/freeze-summary.json'),'syntheticAssertions':audit['totalAssertions'],'integrationAssertions':audit['syntheticAssertions'],'targetedAssertions':audit['targetedAssertions'],'realMedia':'NOT_RUN','realPF':'NOT_RUN','physicalVersionGuarantee':'UNPROVEN','requiredDurability':'UNPROVEN','hostJNI':'BLOCKED','D1':'NOT_PASSED','M0':'NOT_STARTED'}
    path=BASE/'evidence/freeze-summary.json';path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'state':result['state'],'freezeSha256':sha(path),'sourceZip':record(BASE/'artifacts/E1C-source.zip'),'syntheticFixtureBytes':fixturebytes,'logsAndEvidenceBytesBeforeSeal':logbytes}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:print('INSPECT_ONLY: explicit --freeze required')
