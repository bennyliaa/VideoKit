"""Capture affected offline execution-package checks; no builds/Java/device execution."""
import hashlib,json,pathlib,subprocess,sys
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2]
if (B/'evidence/e10a-freeze.json').exists():raise RuntimeError('FROZEN_READ_ONLY')
out=B/'evidence/execution-package-checks';out.mkdir(exist_ok=False)
def row(p):raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
files=sorted([p for folder in ['tools','plan','templates'] for p in (B/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts])+sorted((R/'docs/coder').glob('D1_E10A_*_V1.0.md'));snapshot=[row(p) for p in files];save(out/'inputs.json',dict(files=snapshot));commands=[];results=[]
for label,name in [('readonly-validator','validate_package.py'),('validator-negatives','check_validator.py')]:
 argv=[sys.executable,'-X','utf8','-B',str(B/'tools'/name)];commands.append(dict(label=label,argv=argv));save(out/(label+'.command.json'),commands[-1])
 with (out/(label+'.stdout.txt')).open('xb') as stdout,(out/(label+'.stderr.txt')).open('xb') as stderr:result=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=60)
 assert result.returncode==0,(label,result.returncode);results.append(json.loads((out/(label+'.stdout.txt')).read_bytes()))
assert results[0]['status']=='PASS_PREPARATION_ONLY_NOT_EXECUTABLE' and results[0]['executionReadiness']=='PENDING_INDEPENDENT_REVIEW_NOT_AUTHORIZED' and results[1]['negativeCount']==12
assert snapshot==[row(p) for p in files]
save(B/'evidence/execution-package-validation.json',dict(schema=1,status='PASS',scope='Offline preparation binding and negative validator checks only; no bound positive现场 fixture',inputs=row(out/'inputs.json'),commands=commands,results=results,deviceCalls=0,actualIdsGenerated=0,scopeIssued=False))
print('PASS affected execution-package checks, 12 rejection cases; no execution authority')
