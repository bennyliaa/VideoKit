"""Read-only verify/help by default. Explicit pack seals the exact K binding; never runs launch/dispatch."""
from pathlib import Path
import argparse,json,hashlib,zipfile,subprocess,sys,re,uuid
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';S=E/'e13k-freeze.json';Z=R/'docs/coder/D1-20261018-E13K-source.zip'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(r):assert pin(R/r['path'])=={k:r[k] for k in ['path','bytes','sha256']},r['path']
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prior():
 p=R/'docs/coder/d1e13j-r1/evidence/e13j-r1-freeze.json';assert pin(p)['sha256']=='b6251eaf359ef3bf64233735b248568282c56aa470f7790c9e070a28ea8c86d3';s=json.loads(p.read_text());groups=s['priorSeals']+[dict(seal=pin(p),immutableRowsVerified=len(s['immutableFiles']))]
 for g in groups:
  check(g['seal'])
  for r in json.loads((R/g['seal']['path']).read_text(encoding='utf-8'))['immutableFiles']:check(r)
 return groups
def verify(expected=None):
 assert S.exists(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_SHA'
 s=json.loads(S.read_text());rows=s['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for r in rows:check(r)
 members={r['path']:r for r in rows if r['path']!=s['archive']['path']}
 with zipfile.ZipFile(R/s['archive']['path']) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for n,r in members.items():b=z.read(n);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 release=B/'release/read-only-release.json';raw=release.read_bytes();record=json.loads(raw);f=record['fields'];digest=pin(release)['sha256'];review='f9e5a63acf2aea2fc51c9c71ec50ceba5ed080cdded46676cd7fd9cec6374583';runtime='116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef'
 assert f==dict(budget='262144',kind='e13jFixedReadOnlyRelease',requests='2',review=review,scope=runtime,serial='HA1Q6WXR') and raw==(json.dumps({'e9':1,'fields':dict(sorted(f.items()))},separators=(',',':'))+'\n').encode('ascii')
 scope=json.loads((B/'release/execution-scope.json').read_text());assert str(uuid.UUID(scope['batch']))==scope['batch'] and scope['originalScope']=='aeefe32f-816d-4c0b-aca7-16f76dbd45ff' and scope['runtimeScopeSha256']==runtime and scope['releaseSha256']==digest and scope['review']==review
 requestPath=B/'release/observer-request.json';q=json.loads(requestPath.read_text());assert q['executionBatch']==scope['batch'] and q['originalScope']==scope['originalScope'] and len(q['pins'])==1 and q['maxTextBytes']==32768 and q['scope']==runtime and q['id']=='E13J-R1-SUPPLEMENT-ONCE'
 m=json.loads((E/'jar-member-difference.json').read_text());check(m['baseline']);check(m['jar']);assert len(m['members'])==193 and m['unchangedMembers']==192 and m['changedMembers']==['com/videokit/spike/e4/E13JReadOnly.class']
 with zipfile.ZipFile(R/m['baseline']['path']) as old,zipfile.ZipFile(R/m['jar']['path']) as z:
  assert set(z.namelist())==set(old.namelist())=={r['entry'] for r in m['members']} and len(z.namelist())==193
  for r in m['members']:
   b=z.read(r['entry']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];assert r['byteIdentical']==(b==old.read(r['entry']));assert 'KBindingCheck' not in r['entry']
 def norm(t):return '\n'.join(re.sub(r'[ \t]+',' ',re.sub(r'#\d+','#CP',line.replace(digest,'ABSENT'))).strip() for line in t.splitlines())
 assert norm((E/'javap-old.stdout.txt').read_text())==norm((E/'javap-new.stdout.txt').read_text())
 for r in json.loads((E/'compile-inputs.json').read_text()):check(r)
 for name in ['compile-policy','check-final-binding','describe-final','javap-old','javap-new']:assert json.loads((E/(name+'.exit.json')).read_text())['exitCode']==0
 for name in ['outer-budget','static-policy']:assert json.loads((E/'final-static-002'/(name+'.exit.json')).read_text())['exitCode']==0
 b=json.loads((E/'final-static-002/outer-budget.stdout.txt').read_text(encoding='utf-8-sig'));assert b['status']=='PASS' and b['totalUpperBound']==sum(b['parts'].values())==8157 and b['remaining']==35 and b['parts']['executionCommandRequest']==204
 binding=json.loads((E/'final-binding-receipt.json').read_text());assert binding['functionalReview']==review and binding['mechanicalReview'] is None and binding['budgetUpperBound']==8157 and binding['remainingOuter']==35 and not binding['actualExecution']
 for key in ['release','scope','executionCommandRequest','observerRequest','jar','observer','launch','sourcePolicy']:check(binding[key])
 observer=(B/'policy/observe_e13k.ps1').read_bytes();old=(B/'reference/observe-reviewed.ps1').read_bytes();marker=b'# Same original local context';assert observer[observer.index(marker):]==old[old.index(marker):]
 text=observer.decode('utf-8-sig');assert digest in text and pin(requestPath)['sha256'] in text and 'd1e13k/artifacts/e13k-host-tools.jar' in text
 assert pin(B/'reference/D1_E13J_R1_FIXED_SOCKET_REVIEW_REPORT_V1.0.md')['sha256']==review
 previous=prior();assert previous==s['priorSeals'] and len(previous)==14
 return dict(status='PASS_E13K_STRICT_READONLY_BINDING_VERIFY_NOT_EXECUTED',writes=0,archive=s['archive'],externalSeal=pin(S),archiveEntries=len(members),immutableRows=len(rows),jarMembers=193,unchangedMembers=192,policyOnlyChangedMembers=1,compileAttempts=1,batch=scope['batch'],releaseSha256=digest,outerBytesBound=8157,outerAllocation=8192,totalAllocation=262144,priorSealGroups=14,actualExecution=False,actual5037Connections=0,SDKStarts=0,oldHandleReads=0)
def pack():
 assert not S.exists() and not Z.exists(),'NO_OVERWRITE_OR_REPACK';previous=prior();write(E/'prior-seals-readonly-verification.json',dict(status='PASS',priorSeals=previous,oldBuildOrTestsRerun=0))
 files=[p for p in B.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.checks','__pycache__','build','.gradle']) and p!=S]
 files += [R/'docs/coder'/n for n in ['D1_E13K_RELEASE_BINDING_DELIVERY_V1.0.md','D1_E13K_BINDING_CONTRACT_V1.0.md','D1_E13K_MECHANICAL_CHECK_REPORT_V1.0.md','D1_E13K_EXECUTION_PLAN_V1.0.md']]+[R/'docs/milestones'/n for n in ['D1_E13K_CODER_REQUIREMENTS_V1.0.md','D1_E13K_TESTER_REQUIREMENTS_V1.0.md']];files=sorted(set(files));rows=[pin(p) for p in files]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 write(S,dict(schema=1,candidate='D1-20261018-E13K',archive=pin(Z),immutableFiles=rows+[pin(Z)],priorSeals=previous,actualExecution=False,actual5037Connections=0))
 def snapshot():return [pin(p) for p in sorted(set(files+[Z,S]))]
 before=snapshot();results=[]
 for args in [[],['verify','--seal-sha',pin(S)['sha256']],['--help'],['pack','--help']]:
  cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py'),*args];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);results.append(dict(argv=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
 assert before==snapshot(),'VERIFY_MUTATION'
 receipt=dict(status='PASS_E13K_FINAL_READONLY_VERIFICATION_NOT_EXECUTED',archive=pin(Z),externalSeal=pin(S),archiveEntries=len(files),immutableRows=len(rows)+1,readOnlyFilesBeforeAfter=len(before),beforeAfterIdentical=True,verifications=results,priorSeals=previous,jar=json.loads((E/'jar-member-difference.json').read_text())['jar'],outerBytesBound=8157,totalBudget=262144,actualExecution=False,actual5037Connections=0,oldHandleReads=0);write(R/'docs/coder/D1_E13K_FINAL_READONLY_VERIFICATION_V1.0.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ['verifications','priorSeals']},ensure_ascii=False))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha),ensure_ascii=False))
if __name__=='__main__':main()
