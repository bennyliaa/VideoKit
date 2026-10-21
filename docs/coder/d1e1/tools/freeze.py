"""Explicit artifact packaging. No build, helpers, PF, media or network access."""
import argparse, hashlib, json, zipfile
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def sources():
    paths=sorted(p for name in ['src','tools','manifest'] for p in (BASE/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    manifest={'scope':'E1_TOOL_SOURCE_ONLY','files':[record(p) for p in paths]}
    (BASE/'evidence/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    archive=BASE/'artifacts/E1-source.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,10,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
    print(json.dumps({'sourceFiles':len(paths),'sourceZip':record(archive)}))
def seal():
    docs=[ROOT/'docs/coder'/n for n in ['D1_E1_DELIVERY_V1.0.md','D1_E1_IMPLEMENTATION_BOUNDARY_V1.0.md','D1_E1_EXECUTION_APPENDIX_V1.0.md']]
    files=[p for p in (BASE/'artifacts').rglob('*') if p.is_file()]+[p for p in (BASE/'evidence').glob('*') if p.is_file() and p.name!='freeze-summary.json']+docs
    synthetic=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()]
    assert sum(p.stat().st_size for p in synthetic)<=2097152
    assert sum(p.stat().st_size for p in files if 'evidence' in p.parts)<=4194304
    result={'candidate':'D1-E1-20261016','state':'PARTIAL_IMPLEMENTATION_NOT_READY_FOR_MEDIA_EXPERIMENT',
        'runtime':'PowerShell 7.6.5 / .NET 10.0.11; Java 21.0.10','files':[record(p) for p in sorted(files)],
        'syntheticFiles':[record(p) for p in sorted(synthetic)],'syntheticBytes':sum(p.stat().st_size for p in synthetic),
        'mediaExecution':'NOT_RUN','PF':'NOT_RUN','C14':'UNCHANGED','D1':'NOT_PASSED','M0':'NOT_STARTED'}
    (BASE/'evidence/freeze-summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'freezeSummarySha256':sha(BASE/'evidence/freeze-summary.json'),'state':result['state']}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--sources',action='store_true');parser.add_argument('--seal',action='store_true');a=parser.parse_args()
    if a.sources:sources()
    elif a.seal:seal()
    else:print('Explicit --sources or --seal required. Default does nothing.')
