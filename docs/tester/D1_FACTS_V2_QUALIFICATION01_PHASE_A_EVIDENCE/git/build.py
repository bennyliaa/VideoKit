"""Static file/checkpoint audit only; git subprocesses are metadata operations."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re,subprocess,sys
G=Path(__file__).resolve().parent;E=G.parent;T=E.parent;ROOT=T.parent.parent;C=T.parent/'coder';N='D1_FACTS_V2_QUALIFICATION01_PHASE_A';HEAD='43e58c12106d8f57d5bd6b46a7d11ec3ba80806e';BASE='review/d1-contract03-offline-20261023-af2619b2';BRANCH='review/d1-preauth01-offline-20261023-a601'
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def put(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def git(*a,input=None):return subprocess.run(['git',*a],cwd=ROOT,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
def main():
 if len(sys.argv)>1:return verify(sys.argv[1])
 assert git('rev-parse','HEAD').decode().strip()==HEAD and git('branch','--show-current').decode().strip()==BASE and not git('diff','--cached','--name-only','-z') and git('remote','get-url','origin').decode().strip()=='https://github.com/bennyliaa/VideoKit.git'
 candidates={};audit=[]
 def add(p,origin,h=None,n=None):
  p=p.resolve();p.relative_to(ROOT);b=p.read_bytes()
  if h is not None:assert sha(b)==h and len(b)==n,str(p)
  candidates.setdefault(p,set()).add(origin)
 def packet(base,p,h,count,tag):
  raw=p.read_bytes();assert sha(raw)==h;rows=json.loads(raw)['files'];assert len(rows)==count
  for x in rows:add(Path(x['absolutePath']) if 'absolutePath' in x else base/x['path'],tag,x['sha256'],x['bytes'])
  add(p,tag+'-manifest');audit.append(dict(tag=tag,files=count,manifestSha256=h,bad=0))
 packet(C/'d1android02-readonly-facts-preauth01',C/'d1android02-readonly-facts-preauth01/reference/full-manifest.json','3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c',56,'PREAUTH-original56')
 packet(C/'d1android02-readonly-facts-preauth01-selfcheck02',C/'d1android02-readonly-facts-preauth01-selfcheck02/reference/full-manifest.json','2c8c69d8ecec03d7bc339ae8bdb2349bdb942258f0c050b183197f1aa960fe61',108,'PREAUTH-developer108')
 for prefix,h,count in [('D1_PREAUTH01_INDEPENDENT_B','992c684578af2da658b7f1f3e179b7e5d6b79c0f8b36891c5788118e6ea37562',57),('D1_PREAUTH01_DRIVER_ENV02','fd3b676a69da58aa52d1c86ae3073e8b627bf5e3559f46242a976aeb0b230cbc',184)]:
  packet(T,T/(prefix+'_MANIFEST_V1.0.json'),h,count,prefix)
  for tail in ['_REPORT_V1.0.md','_FREEZE_RECEIPT_V1.0.json','_COORDINATOR_SEND_RECEIPT_V1.0.json','_TESTER_REQUIREMENTS_V1.0.md']:add(T/(prefix+tail),prefix+'-root')
 put(E/'static-source-audit.json',dict(utc=datetime.now(timezone.utc).isoformat(),packets=audit,newV2SourceReadOrTested=False,newTestPopenGateSDK=0,matrixRows=160,matrixStatus='PLANNED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED'))
 report=T/(N+'_REPORT_V1.0.md');phase=[]
 for p in [report,*[p for p in E.glob('*') if p.is_file()]]:
  b=p.read_bytes();phase.append(dict(absolutePath=str(p),bytes=len(b),sha256=sha(b)));add(p,'PHASE_A_STATIC_NOT_RUN')
 manifest=T/(N+'_MANIFEST_V1.0.json');put(manifest,dict(schema='FACTS_V2_PHASE_A_STATIC_MANIFEST_V1',files=phase,status='STATIC_PREPARATION_COMPLETE_V2_NOT_RUN',excluded=['self manifest','freeze receipt','Git inventory and after-commit delivery']))
 put(T/(N+'_FREEZE_RECEIPT_V1.0.json'),dict(reportSha256=sha(report.read_bytes()),manifestSha256=sha(manifest.read_bytes()),files=len(phase),bytes=sum(x['bytes'] for x in phase),bad=0,plannedCases=160,executedV2Cases=0,newTestPopenGateSDK=0,D1='NOT_PASSED',M0='NOT_STARTED'))
 add(manifest,'PHASE_A_manifest');add(T/(N+'_FREEZE_RECEIPT_V1.0.json'),'PHASE_A_freeze')
 for rel in ['docs/CURRENT_DESIGN_BASELINE_V1.0.md','docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md','docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md','docs/D1_PREAUTH01_JSON_CONTRACT_CLARIFICATION_V1.0.md','docs/coder/D1_READONLY_FACTS_PREAUTH01_CODER_REQUIREMENTS_V1.0.md','docs/coder/D1_PREAUTH01_SELFCHECK02_CODER_REQUIREMENTS_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION01_PHASE_A_CHECKPOINT_TESTER_REQUIREMENTS_V1.0.md']:add(ROOT/rel,'authorized-PREAUTH-or-static-coordination')
 for p in [G/'build.py',G/'README.md']:add(p,'own-Git-audit')
 rows=[];excluded=[];secrets=0
 for p,origins in sorted(candidates.items()):
  b=p.read_bytes();rel=p.relative_to(ROOT).as_posix();reason=None
  if re.search(r'(?:^|/)(?:aux|con|prn|nul|com[1-9]|lpt[1-9])(?:\.[^/]*)?(?:/|$)',rel,re.I):reason='WINDOWS_RESERVED_PATH'
  elif 'd1android02-facts-v2-qualification01' in rel:reason='FLOATING_V2_EXCLUDED'
  elif p.suffix.lower() not in ['.py','.ps1','.json','.md','.txt','.patch','.sha256'] or any(x in p.parts for x in ['upstream','deps','node_modules','__pycache__','test_media']):reason='BINARY_DISTRIBUTION_RUNTIME_RAW_OR_CACHE'
  elif len(b)>1048576 or b'\0' in b:reason='LARGE_OR_BINARY'
  elif p.name=='local.properties' or p.name.startswith('.env'):reason='LOCAL_CREDENTIAL_CONTAINER'
  elif re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{25,}\b|\bgithub_pat_[A-Za-z0-9_]{25,}\b|\bAKIA[A-Z0-9]{16}\b',b):reason='SECRET_EXCLUDED';secrets+=1
  else:
   try:b.decode('utf-8-sig')
   except UnicodeDecodeError:reason='NON_UTF8'
   def raw(d):
    if isinstance(d,str):return len(d)>65536 or len(d)>4096 and re.fullmatch('[a-fA-F0-9]+',d) is not None
    if isinstance(d,list):return any(raw(v) for v in d)
    if isinstance(d,dict):return any(raw(v) for v in d.values())
    return False
   if not reason and p.suffix.lower()=='.json' and raw(json.loads(b)):reason='RAW_EMBEDDED_CAPTURE_LOCAL_ONLY'
  row=dict(path=rel,bytes=len(b),sha256=sha(b),gitBlobSha1=blob(b),origins=sorted(origins))
  if reason:row['reason']=reason;excluded.append(row)
  else:rows.append(row)
 assert secrets==0
 assert not git('check-attr','-z','--all','--stdin',input=b'\0'.join(x['path'].encode() for x in rows)+b'\0')
 put(G/'whitelist.json',dict(files=rows,licenseScope='VideoKit-owned exact frozen source/tests/reports/metadata; upstream and third-party distributions excluded; no new redistribution rights',controlFilesSeparate=True))
 put(G/'excluded.json',dict(files=excluded,rootsNeverSelected=['docs/coder/d1android02-facts-v2-qualification01/**','new V2 coder work order (not checked-in, only PLANNED phase reference)','all unrelated files/test_media/zip/rawbinary/media/cache/runtime/third-party distribution/local.properties/credentials'],originalManifestsUnchanged=True,remoteFullyReproducesHistory=False))
 put(G/'review-checks.json',dict(baseHead=HEAD,baseBranch=BASE,headBranch=BRANCH,indexInitiallyEmpty=True,remoteBaseVerified=HEAD,origin='https://github.com/bennyliaa/VideoKit.git',secretHits=0,attributeFilters=0,coreAutocrlf=False,files=len(rows),excluded=len(excluded),excludedReasons=dict(collections.Counter(x['reason'] for x in excluded)),phase='160_PLANNED_NOT_RUN',PREAUTH='9_OF_9_LIMITED_OFFLINE_ACCEPTED',oldFailuresRetained=True,SDKDeviceD1='NOT_PASSED',M0='NOT_STARTED'))
 for name in ['whitelist.json','excluded.json','review-checks.json']:
  p=G/name;b=p.read_bytes();assert len(b)<=1048576;rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b),gitBlobSha1=blob(b)))
 plan=dict(baseHead=HEAD,baseBranch=BASE,headBranch=BRANCH,files=rows);put(G/'stage-plan.json',plan)
 with (G/'pathspec.nul').open('xb') as f:f.write(b'\0'.join((':(literal)'+x['path']).encode() for x in rows)+b'\0')
 print(json.dumps(dict(files=len(rows),bytes=sum(x['bytes'] for x in rows),excluded=len(excluded),stagePlanSha256=sha((G/'stage-plan.json').read_bytes()),phaseReportSha256=sha(report.read_bytes()),phaseManifestSha256=sha(manifest.read_bytes()))))
def verify(mode):
 p=load(G/'stage-plan.json');assert git('branch','--show-current').decode().strip()==BRANCH
 if mode=='stage':
  assert git('rev-parse','HEAD').decode().strip()==HEAD;table={}
  for r in git('ls-files','--stage','-z').split(b'\0'):
   if r:a,path=r.split(b'\t',1);table[path.decode()]=a.decode().split()[1]
  changed={x.decode() for x in git('diff','--cached','--name-only','-z').split(b'\0') if x};assert changed<={x['path'] for x in p['files']}
 else:
  assert git('rev-parse','HEAD^').decode().strip()==HEAD;table={}
  for r in git('ls-tree','-rz','--full-tree','HEAD').split(b'\0'):
   if r:a,path=r.split(b'\t',1);table[path.decode()]=a.decode().split()[2]
 for x in p['files']:
  b=(ROOT/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'] and table[x['path']]==x['gitBlobSha1'],x['path']
 d=dict(mode=mode,allSelectedExact=True,files=len(p['files']),head=git('rev-parse','HEAD').decode().strip(),stagePlanSha256=sha((G/'stage-plan.json').read_bytes()))
 put(G/(mode+'-review.json'),d);print(json.dumps(d))
if __name__=='__main__':main()
