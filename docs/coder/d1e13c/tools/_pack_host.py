"""Explicit new host overlay pack; never loaded by default verify/help."""
import sys
if sys.argv[1:]!=['pack']:raise SystemExit('Explicit pack required')
from pathlib import Path
import json,zipfile,subprocess,hashlib
from package_delivery import B,R,pin,check
E=B/'evidence';archive=R/'docs/coder/D1-20261018-E13C-host.zip';sealpath=E/'e13c-freeze.json'
assert not archive.exists() and not sealpath.exists(),'FROZEN_OR_ALREADY_PACKED'
prior=[]
for path,expected in [
 ('d1e11/evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5'),
 ('d1e11/revision-r1/evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3'),
 ('d1e12/e12-freeze.json','6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640'),
 ('d1e13/evidence/e13-freeze.json','3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0'),
 ('d1e13a/evidence/e13a-freeze.json','24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6'),
 ('d1e13b/evidence/e13b-freeze.json','e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e')]:
 p=R/'docs/coder'/path;assert pin(p)['sha256']==expected
 rows=json.loads(p.read_text(encoding='utf-8'))['immutableFiles']
 for row in rows:check(row)
 prior.append({'seal':pin(p),'immutableRowsVerified':len(rows)})
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(E/'prior-seals-readonly-verification.json',{'status':'PASS','priorSeals':prior,'deviceCalls':0,'oldSuitesRerun':0})
write(E/'final-summary.json',{'status':'READY_FOR_INDEPENDENT_HOST_REVIEW','changedProductionSources':2,'hostCompileAttempts':1,'helperGroups':8,'publicCliAttempts':8,'exactJarUnknownCheck':True,'unknownCustodianLimit':'finite retention substitute only; actual original supervisor in-flight close custody separately verified','apkBuilds':0,'nativeBuilds':0,'deviceCalls':0,'realOnceWrites':0,'actualScope':None,'D1':'NOT_PASSED','M0':'NOT_STARTED'})
files=[]
for folder in ['tools','checks','evidence','reference','release','artifacts']:
 files.extend(p for p in (B/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=sealpath)
files += [R/'docs/coder/D1_E13C_HOST_FIX_DELIVERY_V1.0.md',R/'docs/milestones/D1_E13C_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13C_TESTER_REQUIREMENTS_V1.0.md']
files=sorted(set(files));rows=[pin(p) for p in files]
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
write(sealpath,{'schema':1,'candidate':'D1-20261018-E13C-HOST-ONLY','archive':pin(archive),'immutableFiles':rows+[pin(archive)],'priorSeals':prior,'deviceCalls':0,'actualScope':None,'actualOnce':None})
def snapshot():return [pin(p) for p in sorted(B.rglob('*')) if p.is_file() and '.checks' not in p.parts and '__pycache__' not in p.parts]+[pin(archive)]
before=snapshot();verifications=[]
for args in [[],['verify','--seal-sha',pin(sealpath)['sha256']],['--help'],['pack','--help']]:
 cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py'),*args]
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60)
 verifications.append({'argv':cmd,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});assert result.returncode==0,result.stderr
after=snapshot();assert before==after,'READONLY_MUTATION'
receipt={'status':'PASS_E13C_FINAL_READONLY_VERIFICATION','archive':pin(archive),'externalSeal':pin(sealpath),'archiveEntries':len(files),'immutableRows':len(rows)+1,'readOnlyFilesBeforeAfter':len(before),'verifications':verifications,'priorSeals':prior,'hostJar':json.loads((E/'host-jar-manifest.json').read_text())['jar'],'apkBuilds':0,'nativeBuilds':0,'deviceCalls':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
write(R/'docs/coder/D1_E13C_FINAL_READONLY_VERIFICATION_V1.0.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k not in ['verifications','priorSeals']},ensure_ascii=False))
