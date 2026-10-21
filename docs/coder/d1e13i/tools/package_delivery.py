"""Default verify/help strictly read-only; explicit pack alone creates one immutable E13I bundle."""
from pathlib import Path
import argparse,hashlib,json,zipfile,subprocess,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';S=E/'e13i-freeze.json';Z=R/'docs/coder/D1-20261018-E13I-source.zip'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(r):assert pin(R/r['path'])=={k:r[k] for k in ['path','bytes','sha256']},r['path']
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prior():
 h=R/'docs/coder/d1e13h/evidence/e13h-freeze.json';assert pin(h)['sha256']=='befdcfcc5c04722cb138f845a27fe6d434d63fd204c211b39028914cdce2fc9e';old=json.loads(h.read_text());groups=old['priorSeals']+[dict(seal=pin(h),immutableRowsVerified=len(old['immutableFiles']))]
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
 m=json.loads((E/'host-jar-manifest.json').read_text());check(m['jar']);assert len(m['classes'])==193 and m['unchangedFClassCount']==183 and m['newProductionClassCount']==10
 base=json.loads((E/'base-jar-source-manifest.json').read_text());check(base['jar']);check(base['copiedJar'])
 with zipfile.ZipFile(R/m['jar']['path']) as z,zipfile.ZipFile(R/base['copiedJar']['path']) as old:
  assert len(z.namelist())==193 and set(z.namelist())=={r['entry'] for r in m['classes']}
  for r in m['classes']:
   check(r['source']);b=z.read(r['entry']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];assert not any(v in r['entry'] for v in ['ICheck','IFixtures','IAdditionalCheck'])
   if r['origin']=='UNCHANGED_REVIEWED_E13F':assert b==old.read(r['entry'])
   else:assert b==(E/'actual-tested-production-class-bytes'/r['entry']).read_bytes()
 for r in json.loads((E/'host-001/inputs.json').read_text()):check(r)
 result=json.loads((E/'host-001/results.json').read_text());assert result['status']=='PASS_FINITE_FIXED_SOCKET_OFFLINE' and len(result['modes'])==31 and result['parentCustodyOutstanding']==0
 for name in ['compile',*result['modes'],'describe']:
  record=json.loads((E/'host-001'/(name+'.exit.json')).read_text());assert record['exitCode']==0 and record['naturalReturn'] and record['parentOriginalWaitReturned'] and record['parentRecordingFilesCloseReturned'] and record['qualificationPreserved']
 assert json.loads((E/'host-001/public-reject.exit.json').read_text())['exitCode']==1
 for name in ['test-probe-compile','additional-gates','observer-parse']:assert json.loads((E/'supplement-002'/(name+'.exit.json')).read_text())['exitCode']==0
 for name in ['correct-unissued','wrong-role']:assert json.loads((E/'supplement-002'/(name+'.exit.json')).read_text())['exitCode']==1
 p=json.loads((E/'supplement-002/parent-custody.exit.json').read_text());assert p['exitCode']==0 and p['naturalReturn'] and not p['qualificationPreserved'] and p['parentRecordingFilesCloseReturned']
 binding=json.loads((E/'supplement-002/parent-custody-source-binding.json').read_text());assert hashlib.sha256((B/'tools/check_host.py').read_text().encode()).hexdigest()==binding['sha256']
 for r in json.loads((E/'protocol-source-manifest.json').read_text())['files']:check(r)
 for r in json.loads((E/'protocol-excerpt-manifest.json').read_text())['excerpts']:check(r['source']);check(r['excerpt'])
 binding=json.loads((E/'script-binding.json').read_text());check(binding['script']);check(binding['old']);marker=b'# Same original local context';old=(R/binding['old']['path']).read_bytes();new=(R/binding['script']['path']).read_bytes();assert old[old.index(marker):]==new[new.index(marker):]
 plan=json.loads((B/'release-plan.json').read_text());b=plan['budget'];assert b['allocated']==b['total']==262144 and b['unallocated']==0 and b['queries']==2 and b['versionQueries']==0;assert b['previousHostAndConsole']+b['originalExecReservation']+b['outerJavaSummary']+b['observerFactsConsole']+b['batchIntentMetadata']+2*(b['queryWireCapEach']+b['queryMetadataEach'])==262144
 assert all(plan[k] is None for k in ['actualScope','actualRelease','actualOnce','sourceReview']) and 'APPROVED_REQUEST_SHA="ABSENT"' in (B/'tools/E13IReadOnly.java').read_text()
 assert pin(B/'reference/D1_E13H_READONLY_ENTRY_REVIEW_REPORT_V1.0.md')['sha256']=='d74bb01bf02361fd8785bf1f215a793937ad756fb69f02eb7dfe4931256a953c'
 previous=prior();assert previous==s['priorSeals'] and len(previous)==11
 return dict(status='PASS_E13I_STRICT_READONLY_VERIFY_NO_DISPATCH',writes=0,archive=s['archive'],externalSeal=pin(S),archiveEntries=len(members),immutableRows=len(rows),jarClasses=193,unchangedFClassComparisons=183,newTestedClassComparisons=10,protocolSourceFiles=10,primaryModes=31,productionCompilations=1,extraTestOnlyProbeCompilations=1,priorSealGroups=11,actual5037Connections=0,SDKStarts=0,oldHandleReads=0,actualScope=None,D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'NO_OVERWRITE_OR_REPACK';previous=prior();write(E/'prior-seals-readonly-verification.json',dict(status='PASS',priorSeals=previous,oldBuildOrTestsRerun=0))
 files=[p for p in B.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.checks','__pycache__','build','.gradle']) and p!=S]
 files += [R/'docs/coder'/n for n in ['D1_E13I_FIXED_SOCKET_DELIVERY_V1.0.md','D1_E13I_IMPLEMENTATION_CONTRACT_V1.0.md','D1_E13I_SELF_CHECK_REPORT_V1.0.md','D1_E13I_E13G_SUPPLEMENT_PLAN_V1.0.md']]
 files += [R/'docs/milestones'/n for n in ['D1_E13I_CODER_REQUIREMENTS_V1.0.md','D1_E13I_TESTER_REQUIREMENTS_V1.0.md']];files=sorted(set(files));rows=[pin(p) for p in files]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 write(S,dict(schema=1,candidate='D1-20261018-E13I',archive=pin(Z),immutableFiles=rows+[pin(Z)],priorSeals=previous,actualScope=None,SDKStarts=0,actual5037Connections=0))
 def snap():return [pin(p) for p in sorted(set(files+[Z,S]))]
 before=snap();results=[]
 for args in [[],['verify','--seal-sha',pin(S)['sha256']],['--help'],['pack','--help']]:
  cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py'),*args];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);results.append(dict(argv=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
 assert before==snap(),'READONLY_VERIFY_MUTATION'
 receipt=dict(status='PASS_E13I_FINAL_READONLY_VERIFICATION_NO_DISPATCH',archive=pin(Z),externalSeal=pin(S),archiveEntries=len(files),immutableRows=len(rows)+1,readOnlyFilesBeforeAfter=len(before),beforeAfterIdentical=True,verifications=results,priorSeals=previous,hostJar=json.loads((E/'host-jar-manifest.json').read_text())['jar'],actual5037Connections=0,SDKStarts=0,oldHandleReads=0,actualScope=None,D1='NOT_PASSED',M0='NOT_STARTED');write(R/'docs/coder/D1_E13I_FINAL_READONLY_VERIFICATION_V1.0.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ['verifications','priorSeals']},ensure_ascii=False))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha),ensure_ascii=False))
if __name__=='__main__':main()
