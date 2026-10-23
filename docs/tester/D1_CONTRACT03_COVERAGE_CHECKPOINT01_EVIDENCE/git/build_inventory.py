"""File-only whitelist + read-only Git review; no index/branch mutation."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re,subprocess
G=Path(__file__).resolve().parent;R=G.parent;T=R.parent;ROOT=T.parent.parent;C=T.parent/'coder'
HEAD='1f14c5b92c8174fa0dff6a1819283edc544fa4b4'
def sha(b):return hashlib.sha256(b).hexdigest()
def gitblob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def put(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def git(*args,input=None):
 p=subprocess.run(['git',*args],cwd=ROOT,input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True);return p.stdout
def main():
 freeze=load(T/'D1_CONTRACT03_COVERAGE_CHECKPOINT01_FREEZE_RECEIPT_V1.0.json');assert freeze['allOwnStartedOriginalsReturned'] and not freeze['newResourceUnknown']
 assert git('rev-parse','HEAD').decode().strip()==HEAD
 assert git('branch','--show-current').decode().strip()=='main'
 assert not git('diff','--cached','--name-only','-z')
 assert git('remote','get-url','origin').decode().strip()=='https://github.com/bennyliaa/VideoKit.git'
 candidates={}
 def add(p,origin,h=None,n=None):
  p=Path(p).resolve();p.relative_to(ROOT);assert p.is_file(),str(p)
  if h is not None:
   b=p.read_bytes();assert sha(b)==h and len(b)==n,str(p)
  candidates.setdefault(p,set()).add(origin)
 def packet(base,p,origin):
  d=load(p);add(p,origin+'-original-manifest')
  for x in d['files']:add(Path(x['absolutePath']) if 'absolutePath' in x else base/x['path'],origin,x['sha256'],x['bytes'])
 packet(C/'d1android02-global-idle-contract03-fix',C/'d1android02-global-idle-contract03-fix/reference/freeze-manifest.json','CONTRACT03-original98')
 packet(C/'d1android02-global-idle-contract03-selfcheck02',C/'d1android02-global-idle-contract03-selfcheck02/reference/material-manifest.json','SELFCHECK02-frozen484')
 for kind in ['SEMANTICS_A','INDEPENDENT_B']:
  prefix='D1_GLOBAL_IDLE_CONTRACT03_'+kind
  packet(T,T/(prefix+'_MANIFEST_V1.0.json'),prefix)
  for tail in ['_REPORT_V1.0.md','_FREEZE_RECEIPT_V1.0.json','_COORDINATOR_SEND_RECEIPT_V1.0.json','_TESTER_REQUIREMENTS_V1.0.md']:
   add(T/(prefix+tail),prefix+'-root-record')
 prefix='D1_CONTRACT03_COVERAGE_CHECKPOINT01'
 packet(T,T/(prefix+'_MANIFEST_V1.0.json'),prefix)
 for tail in ['_REPORT_V1.0.md','_FREEZE_RECEIPT_V1.0.json','_TESTER_REQUIREMENTS_V1.0.md']:add(T/(prefix+tail),prefix+'-root-record')
 for rel in ['AGENTS.md','docs/CURRENT_DESIGN_BASELINE_V1.0.md','docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md','docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md','docs/coder/D1_GLOBAL_IDLE_CONTRACT03_FIX_CODER_REQUIREMENTS_V1.0.md','docs/coder/D1_GLOBAL_IDLE_CONTRACT03_FIX_BLOCKED_DELIVERY_V1.0.md','docs/coder/D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_CODER_REQUIREMENTS_V1.0.md','docs/coder/D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_REPORT_V1.0.md','docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_TESTER_REQUIREMENTS_V1.0.md','docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVISION02_INDEPENDENT_B_REPORT_V1.0.md']:
  add(ROOT/rel,'authorized-root-record-or-minimal-failure-trace')
 for name in ['README.md','build_inventory.py','verify_stage.py']:add(G/name,'checkpoint-own-git-review-tool')
 excluded=[];rows=[];maxsize=0;secretHits=0
 patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'\bgh[pousr]_[A-Za-z0-9]{25,}\b',rb'\bgithub_pat_[A-Za-z0-9_]{25,}\b',rb'\bAKIA[A-Z0-9]{16}\b',rb'(?i)Authorization\s*:\s*Bearer\s+[A-Za-z0-9._-]{24,}']
 def rawpayload(d):
  if isinstance(d,str):return len(d)>65536 or len(d)>4096 and re.fullmatch('[0-9a-fA-F]+',d) is not None
  if isinstance(d,list):return any(rawpayload(v) for v in d)
  if isinstance(d,dict):return any(rawpayload(v) for v in d.values())
  return False
 for p,origins in sorted(candidates.items()):
  rel=p.relative_to(ROOT).as_posix();parts=[s.lower() for s in p.relative_to(ROOT).parts];reason=None;b=p.read_bytes();h=sha(b)
  if any(s in parts for s in ['upstream','deps','node_modules','__pycache__','test_media','artifacts','platform-fixtures','instrumentation-assets']):reason='THIRD_PARTY_DISTRIBUTION_OR_RUNTIME_RAW_BINARY_CACHE_OR_MEDIA_ROOT'
  elif any('preauth01' in s for s in parts):reason='NEW_PREAUTH_FLOATING_OR_PLANNED_WORK_OUTSIDE_CHECKPOINT'
  elif p.suffix.lower() not in {'.py','.ps1','.json','.md','.txt','.patch','.sha256'}:reason='NON_WHITELIST_TEXT_TYPE_RAW_BINARY_ARCHIVE_OR_CAPTURE'
  elif p.name.lower()=='local.properties' or p.name.lower().startswith('.env'):reason='LOCAL_CONFIGURATION_OR_CREDENTIAL_CONTAINER'
  elif len(b)>1048576:reason='OVER_ONE_MIB_PER_TEXT_FILE'
  elif b'\0' in b:reason='BINARY_CONTENT'
  elif any(re.search(pattern,b) for pattern in patterns):reason='SECRET_PATTERN_EXCLUDED_WITHOUT_PRINTING_VALUE';secretHits+=1
  else:
   try:b.decode('utf-8-sig')
   except UnicodeDecodeError:reason='NON_UTF8_BINARY_OR_UNQUALIFIED_TEXT'
   if not reason and p.suffix.lower()=='.json':
    try:
     if rawpayload(json.loads(b)):reason='RAW_CAPTURE_OR_LARGE_EMBEDDED_PAYLOAD_RETAINED_LOCAL_ONLY'
    except (UnicodeDecodeError,json.JSONDecodeError):reason='UNQUALIFIED_JSON_TEXT'
  row=dict(path=rel,bytes=len(b),sha256=h,origins=sorted(origins))
  if reason:row['reason']=reason;excluded.append(row);continue
  row.update(gitBlobSha1=gitblob(b),licenseReview='VideoKit-owned source/test/report/metadata from exact frozen manifests; upstream raw/distributions excluded; no new redistribution rights claimed')
  rows.append(row);maxsize=max(maxsize,len(b))
 assert rows and secretHits==0,('REVIEW_SECRET_HITS',secretHits)
 attrs=git('check-attr','-z','--all','--stdin',input=b'\0'.join(x['path'].encode() for x in rows)+b'\0')
 assert not attrs,('UNREVIEWED_GIT_ATTRIBUTE',len(attrs))
 bad=[x for x in rows if 'd1android02-readonly-facts-preauth01' in x['path'].lower()];assert not bad
 put(G/'whitelist.json',dict(schema='CONTRACT03_GIT_DATA_WHITELIST_V1',baseHead=HEAD,files=rows,controlFilesSeparate=['whitelist.json','excluded.json','review-checks.json'],selfHashPolicy='Final exact all-file stage plan including control hashes is local-only to avoid self-reference.'))
 put(G/'excluded.json',dict(schema='CONTRACT03_GIT_EXCLUSIONS_V1',inspectedExcludedFiles=excluded,excludedRootsOutsideCandidateSet=['test_media/**','all unrelated or old dependency chain not explicitly selected','docs/coder/d1android02-readonly-facts-preauth01/**','new PREAUTH work orders and new floating implementation','third-party runtimes/distribution packages','all zip/media/raw binaries/build caches/local.properties/credentials'],originalCompleteManifestsUnchanged=True,remoteIndependentBinaryReproductionClaim=False))
 checks=dict(schema='CONTRACT03_GIT_PRESTAGE_REVIEW_V1',utc=datetime.now(timezone.utc).isoformat(),baseHead=HEAD,initialBranch='main',indexInitiallyEmpty=True,origin='https://github.com/bennyliaa/VideoKit.git',remoteMainVerifiedEqualToHead=True,remoteReadToolChunk='6e4d53',testReportSha256=freeze['reportSha256'],testManifestSha256=freeze['manifestSha256'],frozenTestFiles=freeze['files'],dataFiles=len(rows),dataBytes=sum(x['bytes'] for x in rows),maxFileBytes=maxsize,inspectedExcludedFiles=len(excluded),excludedByReason=dict(collections.Counter(x['reason'] for x in excluded)),secretPatternHits=secretHits,secretValuesPrinted=False,attributeFiltersObserved=0,coreAutocrlf='false',originalBytesPreserved=True,licenseScope='Owned frozen files and citation/hash metadata only; upstream/distribution excluded; existing project license policy unchanged',newPreauthSelected=0,productStatus='WIP_NOT_ACCEPTED',A='400_LIMITED_PASS_ACCEPTED',B='10_PASS_GROUPS_9_OF_11_EXACT_FAULT_TARGETS_ORIGINAL_FAIL_RETAINED',coverage='FAIL_TEST_DRIVER_PRE_PERMIT_TARGET_NOT_COVERED',devicesAndSDK='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',noMainMergeForcePushOrRelease=True)
 put(G/'review-checks.json',checks)
 final=[*rows]
 for name in ['whitelist.json','excluded.json','review-checks.json']:
  p=G/name;b=p.read_bytes();final.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b),gitBlobSha1=gitblob(b),origins=['checkpoint-control-file']))
 final.sort(key=lambda x:x['path'])
 stage=dict(schema='CONTRACT03_EXACT_LOCAL_STAGE_PLAN_V1',baseHead=HEAD,branch='review/d1-contract03-offline-20261023-af2619b2',files=final,excludedFromItself=True,contentBoundary='No floating source, no binary dependency reproduction; preserve original FAIL/NOT_RUN/UNKNOWN.')
 put(G/'stage-plan.json',stage)
 with (G/'pathspec.nul').open('xb') as f:f.write(b'\0'.join((':(literal)'+x['path']).encode() for x in final)+b'\0')
 print(json.dumps(dict(files=len(final),bytes=sum(x['bytes'] for x in final),excluded=len(excluded),excludedByReason=checks['excludedByReason'],maxBytes=maxsize,secretHits=secretHits,stagePlanSha256=sha((G/'stage-plan.json').read_bytes()))))
if __name__=='__main__':main()
