"""Exact immutable-manifest based Git subset; never enumerate old live trees."""
from pathlib import Path
import json,hashlib,re,subprocess,collections
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parent;GIT='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def save(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a):
 p=subprocess.run([GIT,*a],cwd=ROOT,capture_output=True);assert p.returncode==0,p.stderr.decode(errors='replace');return p.stdout
assert git('rev-parse','HEAD').decode().strip()=='09eae12e950d156e1e8fbbfa294ce9b06e6758b4'
assert not git('diff','--cached','--name-only')
sources=[('coder07',ROOT/'docs/coder/d1android02-facts-v2-qualification07/full-manifest.json','e9a275eba60347706fee8ed622350368b1fb0a87f6100c361297952f5a204e7f',567,8138358),('tester07A',ROOT/'docs/tester/D1_FACTS_V2_QUALIFICATION07_PHASE_A_EVIDENCE/manifest.json','0a9173fc3f2c654c408d1a75bb4dc239b6a8437ca1f1840f9b4ef002a0c3e48f',90,2435522),('tester07B',ROOT/'docs/tester/D1_FACTS_V2_QUALIFICATION07_INDEPENDENT_B_EVIDENCE/delivery-manifest.json','017f776849e300a942ce308230f8c76f81ae2afbe4234adc5d9748b14bd4e910',301,5547144)]
allowed={};excluded=[];sourceAudits=[]
def deny(p,bytes,h,reason,origin):excluded.append(dict(path=p,bytes=bytes,sha256=h,reason=reason,origin=origin))
def inspect(p,origin,expected=None):
 rel=p.relative_to(ROOT).as_posix();low=rel.lower();parts=p.relative_to(ROOT).parts
 if any(re.fullmatch(r'(aux|con|prn|nul|com[1-9]|lpt[1-9])(?:\..*)?',x,re.I) for x in parts):deny(rel,expected['bytes'] if expected else None,expected['sha256'] if expected else None,'WINDOWS_RESERVED_NAME_NO_OPEN',origin);return
 reason=None
 if '/sealed-code/' in low:reason='OLD06_SOURCE_COPY_NOT_CURRENT07_PRODUCT'
 elif p.suffix.lower() not in ('.py','.ps1','.json','.md','.txt','.csv','.patch'):reason='RAW_BINARY_ARCHIVE_LOCK_OR_UNAPPROVED_EXTENSION'
 elif '/__pycache__/' in low or any(x in low for x in ('/node_modules/','/third_party/','/upstream/','/deps/')):reason='THIRD_PARTY_OR_CACHE'
 elif p.name=='plan07.json':reason='AMBIENT_HOST_ENVIRONMENT_SNAPSHOT'
 elif any(x in p.name.lower() for x in ('-pipe-','-stdout','-stderr')):reason='ORIGINAL_CAPTURE_STREAM'
 elif expected and expected['bytes']>262144:reason='GENERATED_TEXT_OVER_256KIB'
 if reason:deny(rel,expected['bytes'] if expected else None,expected['sha256'] if expected else None,reason,origin);return
 b=p.read_bytes()
 if expected:assert len(b)==expected['bytes'] and sha(b)==expected['sha256'],rel
 try:s=b.decode('utf-8-sig')
 except UnicodeDecodeError:deny(rel,len(b),sha(b),'NON_UTF8_OR_BINARY',origin);return
 if '\x00' in s:deny(rel,len(b),sha(b),'NUL_BINARY',origin);return
 if len(b)>262144:deny(rel,len(b),sha(b),'GENERATED_TEXT_OVER_256KIB',origin);return
 if p.suffix=='.json':
  try:d=json.loads(s)
  except ValueError:d=None
  def payload(v):
   if type(v) is dict:return any((k.lower() in ('rawbase64','rawhex','datahex','hex','stdoutbytes','packetutf8') and type(x) is str and len(x)>512) or payload(x) for k,x in v.items())
   if type(v) is list:return any(payload(x) for x in v)
   return False
  if payload(d):deny(rel,len(b),sha(b),'ENCODED_ORIGINAL_RAW_STREAM',origin);return
 allowed[rel]=dict(path=rel,bytes=len(b),sha256=sha(b),origin=origin)
for label,m,h,count,size in sources:
 raw=m.read_bytes();assert sha(raw)==h;d=json.loads(raw);entries=d['files'];assert len(entries)==count and sum(x['bytes'] for x in entries)==size
 for e in entries:
  p=Path(e['path'])
  if not p.is_absolute():p=(m.parent if label=='coder07' else m.parent.parent)/p
  # Only known closed Q07 snapshot members; never traverse unrelated directories.
  inspect(p,label,e)
 inspect(m,label+'-full-local-manifest')
 sourceAudits.append(dict(label=label,path=m.relative_to(ROOT).as_posix(),sha256=h,count=count,bytes=size,scope='metadata excludes raw members before file open; selected text independently hash-verified; full567/90/301 content verified during accepted batches'))
# Exact root reports only, no recursive Q01-Q06 product enumeration.
extra=[
'docs/CURRENT_DESIGN_BASELINE_V1.0.md','docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md','docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md','docs/MILESTONES_V1.0.md','docs/PLAYBACK_MILESTONE_MAPPING_V1.0.md',
'docs/D1_QUALIFICATION04_PHASE_A_COORDINATOR_REVIEW_V1.0.md',
'docs/tester/D1_QUALIFICATION07_GIT_CHECKPOINT_TESTER_REQUIREMENTS_V1.0.md',
'docs/tester/D1_FACTS_V2_QUALIFICATION07_PHASE_A_REPORT_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION07_INDEPENDENT_B_REPORT_V1.0.md',
'docs/tester/D1_FACTS_V2_QUALIFICATION01_INDEPENDENT_B_REPORT_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION02_INDEPENDENT_B_REPORT_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION04_INDEPENDENT_B_REPORT_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION04_PHASE_A_REPORT_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION05_PHASE_A_REPORT_V1.0.md','docs/tester/D1_FACTS_V2_QUALIFICATION06_PHASE_A_REPORT_V1.0.md']
for folder in ('coder','tester'):
 for p in (ROOT/'docs'/folder).glob('D1_FACTS_V2_QUALIFICATION*.md'):
  if any(x in p.name for x in ('REQUIREMENTS','DISPATCH')):extra.append(p.relative_to(ROOT).as_posix())
for n in sorted(set(extra)):inspect(ROOT/n,'EXPLICIT_APPROVED_DOC_OR_HISTORY_REPORT')
# Accurately named static delivery reports are the sole old-product exceptions.
for n,h in [('docs/coder/d1android02-facts-v2-qualification05/DELIVERY.md','c66b5edc3219176680c6ae3c2b66950c276c84285d92ddb0aab5824e54d77cad'),('docs/coder/d1android02-facts-v2-qualification06/DELIVERY.md','d7773dd5c2747bd77a720de4849c302ab0ccdb47a840a820056b54aa010aab82')]:
 p=ROOT/n;b=p.read_bytes();assert sha(b)==h;inspect(p,'EXACT_HISTORICAL_REPORT_ONLY',dict(bytes=len(b),sha256=h))
inspect(Path(__file__),'GIT_CHECKPOINT_FILE_ONLY_TOOL')
secretHits=[]
patterns={'PRIVATE_KEY':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','GITHUB_TOKEN':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b','AWS_ACCESS':r'\bAKIA[0-9A-Z]{16}\b','TOKEN_ASSIGNMENT':r'(?i)(?:github_token|access_token|client_secret|password)\s*[=:]\s*[\x22\x27][A-Za-z0-9_+/=-]{16,}[\x22\x27]'}
for rel in allowed:
 text=(ROOT/rel).read_text(encoding='utf-8-sig')
 for kind,pattern in patterns.items():
  for m in re.finditer(pattern,text):secretHits.append(dict(path=rel,line=text[:m.start()].count('\n')+1,kind=kind))
assert not secretHits,secretHits
ignore=git('check-ignore','--stdin').decode() if False else ''
exclusionPolicy=['test_media/**; all media, original streams, .raw/.bin/.zip/.apk/.aar/.jar and native binaries','local.properties, credentials/private keys, third-party packages, runtime distributions and caches','all old Q01-Q06 product trees except exact named static DELIVERY reports; no activity/lock/PID/session query','all coder d1android02-real-facts-handoff01 floating outputs and future planned work, not enumerated','tester07A sealed-code copies are old06 sources and excluded','large generated text above256KiB; encoded raw capture JSON; ambient plan07 environment snapshots','only Git exclusions; local frozen artifacts and original manifests unchanged']
save('source-whitelist.json',dict(base='09eae12e950d156e1e8fbbfa294ce9b06e6758b4',sourceManifests=sourceAudits,files=sorted(allowed.values(),key=lambda x:x['path']),count=len(allowed),bytes=sum(x['bytes'] for x in allowed.values()),metadataHashCycle='this inventory/exclusions and scope notes are separately hashed in outside-cycle stage-freeze; no self-hash claim'))
save('exclusions.json',dict(policy=exclusionPolicy,files=excluded,byReason=dict(collections.Counter(x['reason'] for x in excluded)),excludedCount=len(excluded)))
save('review-checks.json',dict(secretHits=secretHits,utf8TextOnly=True,maxBytes=max(x['bytes'] for x in allowed.values()),sourceFiles=len(allowed),sourceBytes=sum(x['bytes'] for x in allowed.values()),thirdPartyRedistributed=False,licenseReview='Only owned candidate/test tools, schema and text metadata added; existing project license/NOTICE/SBOM files unchanged. Runtime/third-party/binary distribution excluded. Git cannot independently reproduce omitted historical artifacts.',selectedSourceBytesUnchanged=True,oldObjectsQueried=False))
print(json.dumps(dict(count=len(allowed),bytes=sum(x['bytes'] for x in allowed.values()),excluded=len(excluded),secretHits=0,exclusionCounts=dict(collections.Counter(x['reason'] for x in excluded)))))
