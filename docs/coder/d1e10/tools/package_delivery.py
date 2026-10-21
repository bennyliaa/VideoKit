"""E10 local evidence capture and external-seal freeze/READ-ONLY verification. Never devices/builds."""
import argparse,datetime,hashlib,json,pathlib,subprocess,sys,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];ID='D1-20261018-E10'
DOCS=[R/f'docs/coder/D1_E10_{n}_V1.0.md' for n in ['DELIVERY','EXECUTION_RUNBOOK','FAILURE_AND_FINAL_REVIEW','ACTIVATION_INPUT_DAG']]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=sha(b))
def read(p):return json.loads(p.read_bytes())
def write(p,d):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def mutable():assert not (B/'evidence/e10-freeze.json').exists(),'FROZEN_READ_ONLY'
def inputs():return sorted([p for directory in ['tools','plan','templates','reference'] for p in (B/directory).rglob('*') if p.is_file()]+DOCS)
def check():
 mutable();out=B/'evidence/local-validation';out.mkdir(exist_ok=False);commands=[];results=[]
 write(out/'inputs.json',dict(files=[row(p) for p in inputs()]))
 for label,name in [('readonly-package','validate_package.py'),('validator-negatives','check_validator.py')]:
  argv=[sys.executable,'-X','utf8','-B',str(B/'tools'/name)];commands.append(dict(label=label,argv=argv));write(out/(label+'.command.json'),commands[-1])
  with (out/(label+'.stdout.txt')).open('xb') as stdout,(out/(label+'.stderr.txt')).open('xb') as stderr:
   p=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=60)
  assert p.returncode==0,(label,p.returncode);results.append(dict(label=label,exitCode=0,result=read(out/(label+'.stdout.txt'))))
 for x in read(out/'inputs.json')['files']:assert row(R/x['path'])==x
 write(B/'evidence/validation-results.json',dict(schema=1,status='PASS_PREPARATION_AND_VALIDATOR_ONLY',results=results,commands=commands,productionTestsReexecuted=False,builds=0,deviceCalls=0,generatedActualIdentity=0,scopeIssued=False,executionReadiness='BLOCKED_PENDING_INDEPENDENT_REVIEW_AND_COORDINATOR_DISPOSITION'))
 print('PASS local read-only checks; execution blocker remains OPEN')
def freeze():
 mutable();v=read(B/'evidence/validation-results.json');assert v['status']=='PASS_PREPARATION_AND_VALIDATOR_ONLY'
 for x in read(B/'evidence/local-validation/inputs.json')['files']:assert row(R/x['path'])==x
 files=sorted([p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['e10-freeze.json','source-manifest.json']]+DOCS)
 assert all(p.suffix not in ['.apk','.jar','.so'] for p in files),'E10_REFERENCES_FROZEN_BINARIES_ONLY'
 write(B/'evidence/source-manifest.json',dict(schema=1,candidateId=ID,files=[row(p) for p in files]));files.append(B/'evidence/source-manifest.json');archive=R/f'docs/coder/{ID}-execution-package.zip'
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 write(B/'evidence/e10-freeze.json',dict(schema=1,candidateId=ID,status='FROZEN_PREPARATION_ONLY_OPEN_STATIC_BLOCKER',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=row(archive),immutableFiles=[row(p) for p in files]+[row(archive)],sourceFiles=len(files),deviceCalls=0,builds=0,actualIdentity=None,authorization='DRAFT_NOT_ISSUED',actualMigration='NOT_RUN',activation='NOT_BUILT',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN'))
 verify()
def verify():
 seal=B/'evidence/e10-freeze.json';d=read(seal)
 for x in d['immutableFiles']:assert row(R/x['path'])==x,x['path']
 expected={x['path']:x for x in d['immutableFiles'] if x['path']!=d['archive']['path']}
 with zipfile.ZipFile(R/d['archive']['path']) as z:
  assert set(z.namelist())==set(expected)
  for name,x in expected.items():b=z.read(name);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 print(json.dumps(dict(status='PASS_READ_ONLY',seal=row(seal),archive=d['archive'],immutableVerified=len(d['immutableFiles']),mutations=0,deviceCalls=0)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['check','freeze','verify']);a=p.parse_args();globals()[a.operation]()
