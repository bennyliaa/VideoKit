"""Default verify/help only read. Explicit pack creates one new J archive/seal, never rebuilds or executes."""
from pathlib import Path
import argparse,hashlib,json,zipfile,subprocess,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';S=E/'e13j-r1-freeze.json';Z=R/'docs/coder/D1-20261018-E13J-R1-source.zip'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(r):assert pin(R/r['path'])=={k:r[k] for k in ['path','bytes','sha256']},r['path']
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prior():
 p=R/'docs/coder/d1e13j/evidence/e13j-freeze.json';assert pin(p)['sha256']=='fb3966af1514094eecc937ff34562a7dc3b311586279d7526f1eda98cc00a6d0';s=json.loads(p.read_text());groups=s['priorSeals']+[dict(seal=pin(p),immutableRowsVerified=len(s['immutableFiles']))]
 for g in groups:
  check(g['seal'])
  for row in json.loads((R/g['seal']['path']).read_text(encoding='utf-8'))['immutableFiles']:check(row)
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
 m=json.loads((E/'host-jar-manifest.json').read_text());check(m['jar']);assert len(m['classes'])==193 and m['unchangedFClassCount']==183 and m['newProductionClassCount']==10 and m['productionCompileAttempts']==1
 base=json.loads((E/'base-jar-source-manifest.json').read_text());check(base['jar']);check(base['copiedJar'])
 with zipfile.ZipFile(R/m['jar']['path']) as z,zipfile.ZipFile(R/base['copiedJar']['path']) as old:
  assert len(z.namelist())==193 and set(z.namelist())=={r['entry'] for r in m['classes']}
  for r in m['classes']:
   check(r['source']);b=z.read(r['entry']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];assert not any(c in r['entry'] for c in ['ICheck','IFixtures','JCheck'])
   if r['origin']=='UNCHANGED_REVIEWED_E13F':assert b==old.read(r['entry'])
   else:assert b==(E/'actual-tested-production-class-bytes'/r['entry']).read_bytes()
 for r in json.loads((E/'host-001/inputs.json').read_text()):check(r)
 for mode in ['compile','OK','EXIT_NO_EOF','WRITE_FAIL','CHAIN_OK','CLOSE_PENDING','TAIL_PENDING','BUDGET_BOUNDARY','BUDGET_TX','PRODUCTION_AUDIT','AUDIT_AFTER_RAW_FAILURE','describe']:
  row=json.loads((E/'host-001'/(mode+'.exit.json')).read_text());assert row['exitCode']==0 and row['naturalReturn'] and row['parentOriginalWaitReturned'] and row['parentRecordingFilesCloseReturned'] and row['qualificationPreserved']
 assert json.loads((E/'host-001/public-reject.exit.json').read_text())['exitCode']==1
 assert json.loads((E/'host-001/results.json').read_text())['modes']==10
 parent=json.loads((E/'parent-faults-002/results.json').read_text());assert len(parent['groups'])==3 and pin(B/'tools/check_host.py')['sha256']==parent['sourceSha256']
 for row in parent['groups']:assert row['originalProcessSame'] and row['naturalWaitReturned'] and row['originalFilesCloseReturned'] and row['diagnosticFailures'] and not row['qualification'] and not row['kill']
 for mode in ['PENDING_WRITE','CONSOLE','BOTH']:
  row=json.loads((E/'parent-faults-002'/mode/'original.exit.json').read_text());assert row['exitCode']==0 and row['parentOriginalWaitReturned'] and row['parentRecordingFilesCloseReturned'] and not row['qualificationPreserved']
 assert 'afterLimitReadCalls=0' in (E/'host-001/BUDGET_BOUNDARY.stdout.txt').read_text()
 for n in [1,2]:
  root=E/'host-001/PRODUCTION_AUDIT'/('query-'+str(n));assert not (root/'final-owner-facts.txt').exists();facts=(root/'facts.txt').read_text();assert len((root/'facts.txt').read_bytes())<=1024 and len((root/'intent.txt').read_bytes())<=1024 and 'phase=T' in facts and 'qualification=SNAPSHOT_NOT_FINAL' in facts and 'auditOwnClose=UNPROVEN' in facts
 for r in json.loads((E/'protocol-source-manifest.json').read_text())['files']:check(r)
 for r in json.loads((E/'protocol-excerpt-manifest.json').read_text())['excerpts']:check(r['source']);check(r['excerpt'])
 b=json.loads((E/'script-binding.json').read_text());check(b['script']);check(b['old']);marker=b'# Same original local context';old=(R/b['old']['path']).read_bytes();new=(R/b['script']['path']).read_bytes();assert old[old.index(marker):]==new[new.index(marker):]
 assert json.loads((E/'script-003/parse.exit.json').read_text())['exitCode']==0 and json.loads((E/'script-003/unissued.exit.json').read_text())['exitCode']==1
 p=json.loads((B/'release-plan.json').read_text());assert all(p[k] is None for k in ['actualScope','actualRelease','actualOnce','sourceReview']) and p['budget']['allocated']==262144 and p['budget']['total']==262144
 assert 'APPROVED_REQUEST_SHA="ABSENT"' in (B/'tools/E13JReadOnly.java').read_text()
 assert pin(B/'reference/D1_E13I_FIXED_SOCKET_REVIEW_REPORT_V1.0.md')['sha256']=='250083aed28e914bd5d7eb67394fe3bdd69b87f48ec4f6a1f2fe75ed7fa330e7'
 previous=prior();assert previous==s['priorSeals'] and len(previous)==13
 return dict(status='PASS_E13J_R1_STRICT_READONLY_VERIFY_NO_DISPATCH',writes=0,archive=s['archive'],externalSeal=pin(S),archiveEntries=len(members),immutableRows=len(rows),jarClasses=193,unchangedFClassComparisons=183,newTestedClassComparisons=10,focusedModes=10,parentDiagnosticFaultGroups=3,revisionProductionCompilations=1,totalJProductionCompilations=2,priorSealGroups=13,actual5037Connections=0,SDKStarts=0,oldHandleReads=0,D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'NO_REPACK_OR_OVERWRITE';previous=prior();write(E/'prior-seals-readonly-verification.json',dict(status='PASS',priorSeals=previous,oldBuildOrTestsRerun=0))
 files=[p for p in B.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.checks','__pycache__','build','.gradle']) and p!=S]
 files += [R/'docs/coder'/n for n in ['D1_E13J_R1_FIXED_SOCKET_DELIVERY_V1.0.md','D1_E13J_R1_IMPLEMENTATION_CONTRACT_V1.0.md','D1_E13J_R1_SELF_CHECK_REPORT_V1.0.md','D1_E13J_R1_E13G_SUPPLEMENT_PLAN_V1.0.md']]+[R/'docs/milestones'/n for n in ['D1_E13J_R1_CODER_REQUIREMENTS_V1.0.md','D1_E13J_R1_TESTER_REQUIREMENTS_V1.0.md']];files=sorted(set(files));rows=[pin(p) for p in files]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 write(S,dict(schema=1,candidate='D1-20261018-E13J-R1',archive=pin(Z),immutableFiles=rows+[pin(Z)],priorSeals=previous,actualScope=None,actual5037Connections=0,SDKStarts=0))
 def snap():return [pin(p) for p in sorted(set(files+[Z,S]))]
 before=snap();results=[]
 for args in [[],['verify','--seal-sha',pin(S)['sha256']],['--help'],['pack','--help']]:
  cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py'),*args];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);results.append(dict(argv=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
 assert before==snap(),'READONLY_MUTATION'
 receipt=dict(status='PASS_E13J_R1_FINAL_READONLY_VERIFICATION_NO_DISPATCH',archive=pin(Z),externalSeal=pin(S),archiveEntries=len(files),immutableRows=len(rows)+1,readOnlyFilesBeforeAfter=len(before),beforeAfterIdentical=True,verifications=results,priorSeals=previous,hostJar=json.loads((E/'host-jar-manifest.json').read_text())['jar'],actual5037Connections=0,SDKStarts=0,oldHandleReads=0,actualScope=None,D1='NOT_PASSED',M0='NOT_STARTED');write(R/'docs/coder/D1_E13J_R1_FINAL_READONLY_VERIFICATION_V1.0.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ['verifications','priorSeals']},ensure_ascii=False))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha),ensure_ascii=False))
if __name__=='__main__':main()
