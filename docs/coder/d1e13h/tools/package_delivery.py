"""Default verify/help read only. Explicit pack seals one new E13H offline preparation bundle."""
from pathlib import Path
import argparse,hashlib,json,zipfile,subprocess,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';S=E/'e13h-freeze.json';Z=R/'docs/coder/D1-20261018-E13H-source.zip'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(r):assert pin(R/r['path'])=={k:r[k] for k in ['path','bytes','sha256']},r['path']
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prior():
 old=json.loads((R/'docs/coder/d1e13f/evidence/e13f-freeze.json').read_text());out=old['priorSeals']+[dict(seal=pin(R/'docs/coder/d1e13f/evidence/e13f-freeze.json'),immutableRowsVerified=len(old['immutableFiles']))]
 assert out[-1]['seal']['sha256']=='7b72f1bade91286b7d99fbba5459777261e905f4317e0daa969042148b5bf38f'
 for group in out:
  check(group['seal'])
  for row in json.loads((R/group['seal']['path']).read_text(encoding='utf-8'))['immutableFiles']:check(row)
 return out
def verify(expected=None):
 assert S.exists(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_SHA'
 seal=json.loads(S.read_text());rows=seal['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for n,r in members.items():b=z.read(n);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 manifest=json.loads((E/'host-jar-manifest.json').read_text());check(manifest['jar']);assert len(manifest['classes'])==188 and manifest['baseClassCount']==183 and manifest['newClassCount']==5
 base=json.loads((E/'host-001/base-inputs.json').read_text());check(base['jar']);check(base['copiedJar'])
 with zipfile.ZipFile(R/manifest['jar']['path']) as z,zipfile.ZipFile(R/base['copiedJar']['path']) as old:
  assert len(z.namelist())==188 and set(z.namelist())=={x['entry'] for x in manifest['classes']}
  for row in manifest['classes']:
   check(row['source']);b=z.read(row['entry']);assert hashlib.sha256(b).hexdigest()==row['sha256'] and len(b)==row['bytes'];assert 'HCheck' not in row['entry']
   if row['origin']=='BYTE_IDENTICAL_REVIEWED_E13F':assert b==old.read(row['entry'])
   else:assert b==(E/'actual-tested-class-bytes'/row['entry']).read_bytes()
 for row in json.loads((E/'host-001/inputs.json').read_text()):check(row)
 for mode in ['SUCCESS','TIMEOUT','POLICY','WRITE_FAILURE']:assert json.loads((E/'host-001'/(mode+'.exit.json')).read_text())['exitCode']==0
 for mode in ['VERSION_OK','VERSION_BAD','VERSION_TIMEOUT','describe','observer-parse']:assert json.loads((E/'final-002'/(mode+'.exit.json')).read_text())['exitCode']==0
 for mode in ['public-reject','correct-role-disabled','wrong-exe','wrong-serial-argv-role']:assert json.loads((E/'final-002'/(mode+'.exit.json')).read_text())['exitCode']==1
 assert 'G_PRODUCTION_REJECTED_BEFORE_OWNER_OR_NETWORK' in (E/'final-002/public-reject.stderr.txt').read_text()
 assert 'G_PRODUCTION_REJECTED_SERVER_REPLACEMENT_RACE' in (E/'final-002/correct-role-disabled.stderr.txt').read_text()
 binding=json.loads((E/'script-binding.json').read_text());check(binding['script']);check(binding['reviewedOriginal']);marker='# Same original local context';old=(R/binding['reviewedOriginal']['path']).read_text(encoding='utf-8-sig');new=(R/binding['script']['path']).read_text();assert old[old.index(marker):]==new[new.index(marker):]
 plan=json.loads((B/'release-plan.json').read_text());assert plan['status']=='PREPARE_ONLY_DIRECT_ADB_DISABLED' and plan['budget']['allocatedBytes']==246784 and plan['budget']['totalBytes']==262144 and plan['actualScope'] is None and plan['actualOnce'] is None
 assert 'DIRECT_ADB_NO_RESTART_PROVEN=false' in (B/'tools/E13GReadOnly.java').read_text()
 assert pin(B/'reference/D1_E13G_CURRENT_STATE_AND_DISPOSITION_PROPOSAL_V1.0.md')['sha256']=='02d60005562af95b4257befb623ff00911f956615ffbaa66ee955397809000fb'
 previous=prior();assert previous==seal['priorSeals']
 return dict(status='PASS_E13H_STRICT_READONLY_VERIFY_PREPARE_ONLY',writes=0,archive=seal['archive'],externalSeal=pin(S),archiveEntries=len(members),immutableRows=len(rows),jarClasses=188,unchangedE13FClassComparisons=183,newTestedClassComparisons=5,priorSealGroups=len(previous),hostCompilations=1,SDKStarts=0,actual5037Connections=0,originalSessionReads=0,productionEnabled=False,D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'NO_REPACK_OR_OVERWRITE'
 previous=prior();write(E/'prior-seals-readonly-verification.json',dict(status='PASS',priorSeals=previous,oldBuildOrTestsRerun=0))
 files=[p for p in B.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.checks','__pycache__','.gradle','build']) and p!=S]
 docs=['D1_E13H_READONLY_ENTRY_DELIVERY_V1.0.md','D1_E13H_IMPLEMENTATION_CONTRACT_V1.0.md','D1_E13H_SELF_CHECK_REPORT_V1.0.md','D1_E13H_E13G_SUPPLEMENT_PLAN_V1.0.md']
 files += [R/'docs/coder'/n for n in docs]+[R/'docs/milestones'/n for n in ['D1_E13H_CODER_REQUIREMENTS_V1.0.md','D1_E13H_TESTER_REQUIREMENTS_V1.0.md']]
 files=sorted(set(files));rows=[pin(p) for p in files]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 write(S,dict(schema=1,candidate='D1-20261018-E13H',archive=pin(Z),immutableFiles=rows+[pin(Z)],priorSeals=previous,productionEnabled=False,actualScope=None,deviceCalls=0))
 def snap():return [pin(p) for p in sorted(set(files+[Z,S]))]
 before=snap();results=[]
 for args in [[],['verify','--seal-sha',pin(S)['sha256']],['--help'],['pack','--help']]:
  cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py'),*args];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);results.append(dict(argv=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
 after=snap();assert before==after,'VERIFY_MUTATION'
 receipt=dict(status='PASS_E13H_FINAL_READONLY_VERIFICATION_PREPARE_ONLY',archive=pin(Z),externalSeal=pin(S),archiveEntries=len(files),immutableRows=len(rows)+1,readOnlyFilesBeforeAfter=len(before),beforeAfterIdentical=True,verifications=results,priorSeals=previous,hostJar=json.loads((E/'host-jar-manifest.json').read_text())['jar'],productionEnabled=False,actual5037Connections=0,SDKStarts=0,originalSessionReads=0,D1='NOT_PASSED',M0='NOT_STARTED');write(R/'docs/coder/D1_E13H_FINAL_READONLY_VERIFICATION_V1.0.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ['verifications','priorSeals']},ensure_ascii=False))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha),ensure_ascii=False))
if __name__=='__main__':main()
