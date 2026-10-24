"""Facts V2 -> requires-review candidate -> externally reviewed qualification V2.
No reviewer synthesis, permission issuance, device query, or new capture engine.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,re,hashlib,threading,uuid,os
from outer_capture import Capture
from fact_collector import facts,SDK_SHA
from fact_preauth import encode,same,utc
from facts_contract import dec,enc,exact as contract_exact,decode_entry,FACT_ENTRY_BYTES,EVIDENCE_BYTES,REVIEW_BYTES,QUALIFICATION_WIRE_BYTES
from capture_origin import require as original_capture
from immutable_evidence import create,read as read_evidence
_SOURCE_READS=[]
_BUNDLES={}
def source_read(path):
 raw=Path(path).read_bytes();_SOURCE_READS.append(dict(path=str(path),bytes=len(raw)))
 if len(_SOURCE_READS)>8192 or sum(x['bytes'] for x in _SOURCE_READS)>536870912:raise ValueError('V2_HOST_SOURCE_READ_BUDGET')
 return raw
B=Path(__file__).resolve().parents[1]
COORD='01a107c3-2bf9-7fa0-94a0-234258ca6774'
TARGET={'scope','planId','runId','sourceSealSha256','planSha256','mode','evidenceRoot'}
REVIEW={'schema','sourceThreadId','sourceTurnId','mode','approvedForQualification','candidateSha256','bundleSha256','target','notBeforeUtc','expiresUtc','home','homeEvidenceSha256','services'}
SERVICE={'packages','process','user','uid','kind','state','category','firmware','evidenceSha256','factScope','validFromUtc','validToUtc','range'}
def sha(b):return hashlib.sha256(b).hexdigest()
def fail(c):raise ValueError(c)
def exact(d,keys,c):
 if type(d) is not dict or set(d)!=set(keys):fail(c)
def integer(v,lo,hi):return type(v) is int and lo<=v<=hi
def digest(v):return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None and v!='0'*64
def now(v=None):return datetime.now(timezone.utc) if v is None else utc(v)
def current_pins():
 raw=source_read(B/'reference/runner-source-seal.json');s=json.loads(raw)['sources']
 return dict(sourceSealSha256=sha(raw),planSha256=s['reference/exact-seven-role-plan.json'])
def target(t):
 exact(t,TARGET,'V2_TARGET_SCHEMA');pins=current_pins()
 if any(not digest(t[k]) for k in ('scope','sourceSealSha256','planSha256')) or t['sourceSealSha256']!=pins['sourceSealSha256'] or t['planSha256']!=pins['planSha256']:fail('V2_TARGET_SOURCE')
 try:valid=type(t['planId']) is str and str(uuid.UUID(t['planId']))==t['planId']
 except ValueError:valid=False
 if not valid or type(t['runId']) is not str or re.fullmatch('D1MA02-[A-Z0-9_-]{1,32}',t['runId']) is None or t['mode'] not in ('LIVE','OFFLINE_FIXTURE'):fail('V2_TARGET_ID_MODE')
 from entry_gates import fixture_root_allowed
 root=t['evidenceRoot']
 if type(root) is not str or not Path(root).is_absolute() or str(Path(root).resolve())!=root or Path(root).name!='outputs':fail('V2_TARGET_EVIDENCE_ROOT')
 if t['mode']=='OFFLINE_FIXTURE':
  if not fixture_root_allowed(root):fail('V2_TARGET_EVIDENCE_ROOT')
 elif not Path(root).is_relative_to(Path('D:/CodexProjects/VideoKit/docs/tester/D1_ANDROID02_CAPTURE_EXECUTION')):fail('V2_TARGET_EVIDENCE_ROOT')
 return json.loads(encode(t))
class FactsBundle:
 def __init__(self,capture,preauth_bytes,policy_bytes):
  try:self._construct(capture,preauth_bytes,policy_bytes)
  except ValueError:raise
  except (KeyError,TypeError,AttributeError,OverflowError):fail('V2_ORIGINAL_FIELD_TYPE')
 def _construct(self,capture,preauth_bytes,policy_bytes):
  if type(capture) is not Capture:fail('V2_OUTER_ORIGINAL_REQUIRED')
  if any(v['actual'] is capture for v in _BUNDLES.values()):fail('V2_CAPTURE_BUNDLE_ONCE')
  original=original_capture(capture)
  self.actual=capture;self.preauth=preauth_bytes;self.policy=policy_bytes;self.outer=original['stdoutBytes']
  identity=json.loads(original['identity']);argv=list(original['argv'])
  d=decode_entry(self.outer,preauth_bytes,policy_bytes,argv,identity,source_read)
  self.receipt=d['receipt'];self.binding=d['binding'];self.raw=d['raw'];self.parsed=d['parsed'];self.gateReceipt=d['gate'];self.initialProof=d['proof']
  self.outer_return=dict(schema='GLOBAL_IDLE_FACT_OBSERVED_OUTER_RETURN_V2',ownerPid=identity['pid'],creationFileTime=identity['creationFileTime'],image=identity['image'],creatorArgv=argv,hostPid=os.getpid(),hostThread=threading.get_ident(),captureSourceSha256=sha(source_read(B/'tools/outer_capture.py')),originSourceSha256=sha(source_read(B/'tools/capture_origin.py')),lifecycle='ORIGINAL_CONSTRUCTOR_START_READ_WAIT_CLOSE_JOURNAL_RETURN',stdoutSha256=sha(self.outer),waitReturned=True,stdoutEOF=True,stderrEOF=True,originalPipesClosed=True,originalHandleClosed=True,controllerReturned=True,unknown=False,exitCode=0)
  p=d['preauth'];r=self.receipt
  self.evidence=dict(schema='GLOBAL_IDLE_FACT_EVIDENCE_BUNDLE_V2',factScope=p['scope'],factPlanId=p['planId'],factRunId=p['runId'],nonce=p['nonce'],rawSha256=sha(self.raw),rawBytes=len(self.raw),receiptSha256=sha(enc(r)),externalPreauthSha256=sha(preauth_bytes),runtimeBindingSha256=sha(enc(self.binding)),outerReturnSha256=sha(enc(self.outer_return)),collectorSha256=r['sourceSha256'],factPlanSha256=r['planSha256'],sourceSealSha256=p['sourceSealSha256'],mode=p['mode'],factEvidenceRoot=p['evidenceRoot'],gateReceiptSha256=self.binding['gateReceiptSha256'],initialProofSha256=self.binding['initialProofSha256'])
  self.hash=sha(enc(self.evidence))
  self.packetRef=create(self.outer,str(Path(p['evidenceRoot'])/'v2-original-return'),'facts-entry-'+p['scope']+'.json')
  _BUNDLES[self]=dict(actual=capture,seal=self._seal())
 def _seal(self):
  return sha(enc(dict(receipt=self.receipt,binding=self.binding,parsed=self.parsed,outer=self.outer_return,evidence=self.evidence,hash=self.hash,packetRef=self.packetRef,gate=self.gateReceipt,proof=self.initialProof,raw=sha(self.raw),packet=sha(self.outer),preauth=sha(self.preauth),policy=sha(self.policy))))
 def require_original(self):
  try:
   r=_BUNDLES.get(self)
   if r is None or self.actual is not r['actual'] or self._seal()!=r['seal']:fail('V2_BUNDLE_ORIGINAL_PROVENANCE')
   origin=original_capture(self.actual)
   if origin['stdoutBytes']!=self.outer:fail('V2_BUNDLE_ORIGINAL_BYTES')
  except ValueError:raise
  except (KeyError,TypeError,AttributeError,OverflowError):fail('V2_BUNDLE_ORIGINAL_PROVENANCE')
 def fresh(self,stamp=None):
  self.require_original();n=now(stamp);start=utc(self.receipt['collectedAtUtc'])
  if not 0<=(n-start).total_seconds()<300:fail('V2_FACT_STALE_FUTURE')
  return n,start
def candidate(bundle,t,stamp=None):
 if type(bundle) is not FactsBundle:fail('V2_OBSERVED_BUNDLE_REQUIRED')
 n,start=bundle.fresh(stamp);t=target(t)
 if t['mode']!=bundle.receipt['mode'] or t['scope']==bundle.receipt['scope']:fail('V2_TARGET_FACT_SCOPE_MODE')
 f=bundle.parsed;home=dict(package=f['homeRolePackage'],component=f['homeComponent'],process=f['homeRolePackage'],user=f['user'],uid=f['homeUid'],systemFlag=True)
 return dict(schema='GLOBAL_IDLE_QUALIFICATION_CANDIDATE_V2',status='REQUIRES_REVIEW',approved=False,bundleSha256=bundle.hash,target=t,mode=t['mode'],collectedAtUtc=bundle.receipt['collectedAtUtc'],maximumExpiresUtc=(start+timedelta(seconds=300)).isoformat(),home=home,services=[],servicePolicy='NO_AUTOMATIC_EXEMPTIONS')
def _qualify(bundle,t,review_bytes,approved_review_sha256,evidence,stamp=None):
 c=candidate(bundle,t,stamp);n,start=bundle.fresh(stamp)
 if not digest(approved_review_sha256) or type(review_bytes) is not bytes or sha(review_bytes)!=approved_review_sha256:fail('V2_EXTERNAL_REVIEW_HASH')
 rev=dec(review_bytes,REVIEW_BYTES,'V2_REVIEW');exact(rev,REVIEW,'V2_REVIEW_SCHEMA')
 if rev['schema']!='GLOBAL_IDLE_FACT_REVIEW_V2' or rev['approvedForQualification'] is not True or rev['sourceThreadId']!=COORD or not re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',rev['sourceTurnId'] or ''):fail('V2_REVIEW_SOURCE_APPROVAL')
 if not same(rev['target'],t) or rev['mode']!=t['mode'] or rev['bundleSha256']!=bundle.hash or rev['candidateSha256']!=sha(encode(c)):fail('V2_REVIEW_BATCH_TARGET')
 lo=utc(rev['notBeforeUtc']);hi=utc(rev['expiresUtc'])
 if not start<=lo<=n<hi<=start+timedelta(seconds=300):fail('V2_REVIEW_WINDOW')
 if not same(rev['home'],c['home']):fail('V2_HOME_REVIEW_IDENTITY')
 if type(evidence) is not dict:fail('V2_POLICY_EVIDENCE_MAP')
 def proof(h,expected):
  if not digest(h) or h not in evidence or type(evidence[h]) is not bytes or sha(evidence[h])!=h:fail('V2_NARROW_EVIDENCE_HASH')
  if not same(dec(evidence[h],EVIDENCE_BYTES,'V2_POLICY_EVIDENCE'),expected):fail('V2_NARROW_EVIDENCE_CONTENT')
 proof(rev['homeEvidenceSha256'],dict(schema='GLOBAL_IDLE_HOME_REVIEW_EVIDENCE_V1',mode=t['mode'],factScope=bundle.receipt['scope'],rawSha256=sha(bundle.raw),firmware=bundle.parsed['fingerprint'],home=c['home'],statement='EXACT_OBSERVED_HOME_IDENTITY'))
 if type(rev['services']) is not list or len(rev['services'])>68:fail('V2_SERVICE_BOUND')
 seen=set()
 for s in rev['services']:
  exact(s,SERVICE,'V2_SERVICE_SCHEMA')
  if type(s['packages']) is not list or len(s['packages'])!=1 or type(s['process']) is not str or not re.fullmatch('[A-Za-z_.][A-Za-z0-9_.]*(?::[A-Za-z0-9_.]+)*',s['process']) or not integer(s['user'],0,0) or not integer(s['uid'],0,99999) or s['kind'] not in ('APP','PERS') or not integer(s['state'],0,6) or s['state'] in (2,3) or s['category']!='NONCONTENDING_SYSTEM_SERVICE' or s['firmware']!=bundle.parsed['fingerprint'] or s['factScope']!=bundle.receipt['scope'] or s['range']!='EXACT_SNAPSHOT' or s['validFromUtc']!=bundle.receipt['collectedAtUtc'] or s['validToUtc']!=rev['expiresUtc'] or (s['process'],s['uid']) in seen:fail('V2_SERVICE_NARROW_POLICY')
  seen.add((s['process'],s['uid']))
  if sum(p['package']==s['packages'][0] and p['uid']==s['uid'] and p['systemFlag'] is True for p in bundle.parsed['systemPackages'])!=1:fail('V2_SERVICE_SYSTEM_FACT')
  proof(s['evidenceSha256'],dict(schema='GLOBAL_IDLE_SERVICE_REVIEW_EVIDENCE_V1',mode=t['mode'],rawSha256=sha(bundle.raw),**{k:v for k,v in s.items() if k!='evidenceSha256'}))
 q=dict(schema='GLOBAL_IDLE_QUALIFICATION_V2',mode=t['mode'],fixtureOnly=t['mode']=='OFFLINE_FIXTURE',targetScope=t['scope'],targetRunId=t['runId'],targetPlanId=t['planId'],targetSourceSealSha256=t['sourceSealSha256'],targetPlanSha256=t['planSha256'],factScope=bundle.receipt['scope'],authorizationKind='GLOBAL_IDLE_FACT_PREAUTH_V1',externalPreauthSha256=bundle.evidence['externalPreauthSha256'],runtimeBindingSha256=bundle.evidence['runtimeBindingSha256'],bundleSha256=bundle.hash,adapterSourceSha256=sha(source_read(Path(__file__))),reviewSha256=approved_review_sha256,reviewSourceThreadId=rev['sourceThreadId'],reviewSourceTurnId=rev['sourceTurnId'],approved=True,factCaptureReceiptSha256=bundle.evidence['receiptSha256'],factOuterReturnSha256=bundle.evidence['outerReturnSha256'],collectorSourceSha256=bundle.receipt['sourceSha256'],factPlanSha256=bundle.receipt['planSha256'],rawSha256=sha(bundle.raw),rawBytes=len(bundle.raw),routeProofSha256=bundle.receipt['routeProofSha256'],sdkSha256=SDK_SHA,collectedAtUtc=bundle.receipt['collectedAtUtc'],expiresAtUtc=rev['expiresUtc'],originalReturn={k:bundle.outer_return[k] for k in ('waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed','controllerReturned','unknown','exitCode')},grammar='API31_APP_PERS_V1',serial='HA1Q6WXR',model=bundle.parsed['model'],api=bundle.parsed['api'],fingerprint=bundle.parsed['fingerprint'],user=bundle.parsed['user'],home=rev['home'],services=rev['services'],systemPackages=bundle.parsed['systemPackages'],reviewEvidenceSha256=approved_review_sha256)
 # Only one reviewed policy is stored; no repeated full services in the wire.
 used={rev['homeEvidenceSha256']}|{s['evidenceSha256'] for s in rev['services']}
 body=dict(schema='GLOBAL_IDLE_QUALIFICATION_EVIDENCE_V2',reviewUtf8=review_bytes.decode('utf-8'),candidateUtf8=enc(c).decode('utf-8'),bundleUtf8=enc(bundle.evidence).decode('utf-8'),outerReturnUtf8=enc(bundle.outer_return).decode('utf-8'),preauthUtf8=bundle.preauth.decode('utf-8'),policyUtf8=bundle.policy.decode('utf-8'),factsPacketRef=bundle.packetRef,policyEvidence={k:evidence[k].decode('utf-8') for k in sorted(used)})
 raw=enc(body)
 if len(raw)>EVIDENCE_BYTES:fail('V2_EVIDENCE_REPRESENTATION_BOUND')
 ref=create(raw,str(Path(t['evidenceRoot'])/'v2-authority'),'qualification-evidence-'+t['scope']+'.json')
 wire=dict(schema='GLOBAL_IDLE_QUALIFICATION_V2',representation='PINNED_EVIDENCE_REFERENCE_V1',mode=q['mode'],fixtureOnly=q['fixtureOnly'],targetScope=q['targetScope'],targetRunId=q['targetRunId'],targetPlanId=q['targetPlanId'],targetSourceSealSha256=q['targetSourceSealSha256'],targetPlanSha256=q['targetPlanSha256'],reviewEvidenceSha256=approved_review_sha256,authorizationKind=q['authorizationKind'],adapterSourceSha256=q['adapterSourceSha256'],bundleSha256=q['bundleSha256'],evidenceRoot=t['evidenceRoot'],evidenceRef=ref)
 if len(enc(wire))>QUALIFICATION_WIRE_BYTES:fail('V2_QUALIFICATION_WIRE_BOUND')
 return wire
def qualify(bundle,t,review_bytes,approved_review_sha256,evidence,stamp=None):
 try:return _qualify(bundle,t,review_bytes,approved_review_sha256,evidence,stamp)
 except ValueError:raise
 except (KeyError,TypeError,AttributeError,OverflowError):fail('V2_REVIEW_FIELD_TYPE')
