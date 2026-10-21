import sys
if sys.argv[1:]!=['pack']:raise SystemExit('Explicit pack only')
from pathlib import Path
import json,zipfile,subprocess
from package_delivery import B,R,pin,check
E=B/'evidence';archive=R/'docs/coder/D1-20261018-E13E-source.zip';seal=E/'e13e-freeze.json';assert not archive.exists() and not seal.exists()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior=[]
for name,expected in [
 ('d1e11/evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5'),
 ('d1e11/revision-r1/evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3'),
 ('d1e12/e12-freeze.json','6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640'),
 ('d1e13/evidence/e13-freeze.json','3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0'),
 ('d1e13a/evidence/e13a-freeze.json','24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6'),
 ('d1e13b/evidence/e13b-freeze.json','e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e'),
 ('d1e13c/evidence/e13c-freeze.json','14358fdb7e7900de669e76965c4ecce5b008eb8daea216b9abaa7f7891e45762'),
 ('d1e13d/evidence/e13d-freeze.json','acc83e5aff9288099c1f324fb24394316dedfd83272cce66cd8299a215b66365')]:
 p=R/'docs/coder'/name;assert pin(p)['sha256']==expected;rows=json.loads(p.read_text(encoding='utf-8'))['immutableFiles']
 for row in rows:check(row)
 prior.append(dict(seal=pin(p),immutableRowsVerified=len(rows)))
write(E/'prior-seals-readonly-verification.json',dict(status='PASS',priorSeals=prior,oldBuildOrTestsRerun=0,deviceCalls=0))
files=[]
for folder in ['src','android','upstream-c14','binding','checks','gradle','app/src','fixture/src','tools','evidence','reference','release','artifacts/D1-20261018-E13E/delivery-final']:
 files += [p for p in (B/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=seal]
for root in [B,B/'app',B/'fixture']:
 files += [p for p in root.iterdir() if p.is_file() and (p.suffix in ['.kts','.properties','.lockfile'] or p.name in ['gradlew','gradlew.bat']) and p.name!='fixture-signing.p12']
files += [R/'docs/coder'/name for name in ['D1_E13E_LIFECYCLE_DELIVERY_V1.0.md','D1_E13E_IMPLEMENTATION_CONTRACT_V1.0.md','D1_E13E_SELF_CHECK_REPORT_V1.0.md','D1_E13E_ORIGINAL_TASK_DISPOSITION_PLAN_V1.0.md']]
files += [R/'docs/milestones/D1_E13E_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13E_TESTER_REQUIREMENTS_V1.0.md']
files=sorted(set(files));rows=[pin(p) for p in files]
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
write(seal,dict(schema=1,candidate='D1-20261018-E13E',archive=pin(archive),immutableFiles=rows+[pin(archive)],priorSeals=prior,actualScope=None,actualOnce=None,deviceCalls=0))
def snapshot():
 return [pin(p) for p in sorted(B.rglob('*')) if p.is_file() and not any(part in ['.checks','.gradle','build','__pycache__'] for part in p.parts)]+[pin(archive)]
before=snapshot();results=[]
for args in [[],['verify','--seal-sha',pin(seal)['sha256']],['--help'],['pack','--help']]:
 cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py'),*args];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);results.append(dict(argv=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
after=snapshot();assert before==after,'READONLY_ENTRY_MUTATION'
receipt=dict(status='PASS_E13E_FINAL_READONLY_VERIFICATION',archive=pin(archive),externalSeal=pin(seal),archiveEntries=len(files),immutableRows=len(rows)+1,readOnlyFilesBeforeAfter=len(before),verifications=results,priorSeals=prior,hostJar=json.loads((E/'host-jar-manifest.json').read_text())['jar'],deviceCalls=0,actualScope=None,D1='NOT_PASSED',M0='NOT_STARTED')
write(R/'docs/coder/D1_E13E_FINAL_READONLY_VERIFICATION_V1.0.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ['verifications','priorSeals']},ensure_ascii=False))
