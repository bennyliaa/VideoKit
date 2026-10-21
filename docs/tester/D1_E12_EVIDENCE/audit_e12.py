"""Independent local byte/traceability audit. Does not import candidate code."""
from pathlib import Path
import hashlib,json,re,zipfile
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def check(name,ok,detail=None):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
def verify(row,label):
    p=ROOT/row['path'];b=p.read_bytes()
    check(label,len(b)==row['bytes'] and sha(b)==row['sha256'],row['path'])
sealpath=ROOT/'docs/coder/d1e12/e12-freeze.json'
seal=json.loads(sealpath.read_text(encoding='utf-8'))
check('E12 external seal',sha(sealpath.read_bytes())=='6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640')
check('46 immutable rows',len(seal['immutableFiles'])==46)
for row in seal['immutableFiles']:verify(row,'immutable')
verify(seal['archive'],'ZIP pin')
with zipfile.ZipFile(ROOT/seal['archive']['path']) as z:
    names=z.namelist()
    expected={r['path']:r for r in seal['immutableFiles'] if r['path']!=seal['archive']['path']}
    check('45 ZIP members exact set',len(names)==45 and len(set(names))==45 and set(names)==set(expected))
    for n in names:
        b=z.read(n);r=expected[n]
        check('ZIP member',len(b)==r['bytes'] and sha(b)==r['sha256'],n)
pins=json.loads((ROOT/'docs/coder/d1e12/input-pins.json').read_text(encoding='utf-8'))['inputs']
check('31 inputs',len(pins)==31)
for row in pins:
    verify(row,'original input')
    ref=ROOT/'docs/coder/d1e12/reference'/row['path']
    check('reference equals original',ref.read_bytes()==(ROOT/row['path']).read_bytes(),row['id'])
for prior in seal['priorFreezes']:
    verify(prior['seal'],'prior seal')
    obj=json.loads((ROOT/prior['seal']['path']).read_text(encoding='utf-8'))
    lists=[v for v in obj.values() if isinstance(v,list) and len(v)==prior['verifiedRows'] and all(isinstance(r,dict) and {'path','bytes','sha256'}<=r.keys() for r in v)]
    check('prior row list located',len(lists)==1,prior['verifiedRows'])
    if len(lists)==1:
        for row in lists[0]:verify(row,'prior immutable')
u=(ROOT/pins[0]['path']).read_text(encoding='utf-8').splitlines()
rows=json.loads((ROOT/'docs/coder/d1e12/requirement-rows.json').read_text(encoding='utf-8'))
ranges=[(941,947),(951,957),(961,965),(969,975),(979,986),(990,996),(1000,1008),(1012,1019),(1025,1035),(1056,1067),(1090,1097),(1103,1112)]
expectedlines=[i for a,b in ranges for i in range(a,b+1)]
check('99 exact original line coverage',len(rows)==99 and sorted(r['line'] for r in rows)==expectedlines)
for r in rows:check('requirement original text',r['text']==re.sub(r'^-\s+','',u[r['line']-1]).strip(),r['id'])
check('unique 99 IDs',len(set(r['id'] for r in rows))==99)
matrix=(ROOT/'docs/coder/D1_E12_REQUIREMENT_EVIDENCE_MATRIX_V1.0.md').read_text(encoding='utf-8')
for r in rows:check('matrix row present',r['id']+' / U:'+str(r['line']) in matrix,r['id'])
check('13 P0 source rows',all('| U:'+str(i)+' ' in matrix for i in range(73,86)))
check('11 native gate rows',all('| J'+str(i).zfill(2)+' |' in matrix for i in range(1,12)))
names=[Path(s.strip()).name for s in u[1075:1085]]
check('10 design names',len(names)==10 and all('| §30 '+s+' |' in matrix for s in names),names)
check('milestone and API parallel precondition mapped',all(s in matrix for s in ['§28 VK-M0','§28 VK-M1–M3','§28 VK-M4','§28 VK-M7','§28并行前提']))
extra=['docs/coder/d1e11/src/com/videokit/spike/e4/E9DeploymentGate.java','docs/coder/d1e11/upstream-c14/src/com/videokit/spike/c14/AsyncReadBridge.java','docs/coder/d1e11/upstream-c14/src/com/videokit/spike/c14/LeaseRegistry.java','docs/coder/d1e11/android/com/videokit/spike/e4/E11ActivationLifetime.java','docs/coder/d1e11/android/com/videokit/spike/e4/E4CodecService.java','docs/coder/d1e11/upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java']
supplement=[dict(path=p,bytes=len((ROOT/p).read_bytes()),sha256=sha((ROOT/p).read_bytes())) for p in extra]
result=dict(atUtc=datetime.now(timezone.utc).isoformat(),scope='LOCAL_READ_ONLY_NO_DEVICE_NO_BUILD_NO_CANDIDATE_EXECUTION',status='PASS' if all(c['passed'] for c in checks) else 'FAIL',checks=len(checks),failed=[c for c in checks if not c['passed']],details=checks,supplementalSourcePins=supplement)
(OUT/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','checks','failed']},ensure_ascii=False))
