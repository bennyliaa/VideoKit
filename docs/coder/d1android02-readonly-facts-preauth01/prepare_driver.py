"""Static reuse + profile preparation. Must run once before dynamic worker."""
from pathlib import Path
import json,hashlib,os,ast,uuid
B=Path(__file__).resolve().parent;OLD=B.parent/'d1android02-global-idle-contract03-selfcheck02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for rel in ('owned_capture.py','reuse/capture_policy.py','reuse/native_identity.py','reuse/evidence_io.py','reuse/owned_child.py','reuse/owned_child.ps1'):
 dst=B/'driver'/rel;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes((OLD/rel).read_bytes())
save(B/'reference/driver-lineage.json',{rel:dict(upstream=str(OLD/rel),sha256=sha(OLD/rel),derivedSha256=sha(B/'driver'/rel),algorithmChanges=False) for rel in ('owned_capture.py','reuse/capture_policy.py','reuse/native_identity.py','reuse/evidence_io.py','reuse/owned_child.py','reuse/owned_child.ps1')})
qc=B/'selfchecks/work/qualification';qc.mkdir(parents=True,exist_ok=False)
env=dict(SystemRoot='C:\\Windows',WINDIR='C:\\Windows',TEMP=str(qc),TMP=str(qc))
pins={str(p.relative_to(B)):sha(p) for folder in ('tools','selfchecks','driver') for p in (B/folder).rglob('*') if p.is_file() and 'work' not in p.parts}
pins.update({p.name:sha(p) for p in B.glob('*.py')})
for p in (B/'tools').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in (B/'driver').rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in B.glob('*.py'):compile(p.read_text(),str(p),'exec')
seal=json.loads((B/'reference/runner-source-seal.json').read_bytes())
for rel,h in seal['sources'].items():assert sha(B/rel)==h
save(B/'reference/batch-plan.json',dict(schema='PREAUTH01_OFFLINE_BATCH_V1',batch=uuid.uuid4().hex,wholeSeconds=360,stopNewSeconds=320,concurrency=1,retry=0,readBytes=1073741824,savedBytes=16777216,auxiliaryProcesses=96,plannedGraphProcessBound=12,estimateSeconds=90,ioReservation=dict(originalGateSourceCaps=3*268435456,pythonAndPSImportControlUpper=64*1048576,driverAndSourcesUpper=32*1048576,total=905969664),actualSDK=0,nativeRoute=0,tcp=0,qualificationV2='NOT_IMPLEMENTED_NO_ADAPTER',externalApproval='SYNTHETIC_OFFLINE_FIXTURE_ONLY'))
save(B/'reference/profile.json',dict(schema='PREAUTH01_EXACT_PROFILE_V1',hostCwd=str(Path.cwd()),qualificationCwd=str(qc),qualificationEnv=env,inheritedEnvSha256=hashlib.sha256(json.dumps(dict(os.environ),sort_keys=True,separators=(',',':')).encode()).hexdigest(),scriptPins=pins,sourceSealSha256=sha(B/'reference/runner-source-seal.json'),gateSourcesSha256=sha(B/'reference/gate-sources.json'),callGraph=['qualification python0/python7/PS0','semantic PS exact input/output','preStart PS exact output','new original Gate route_fixture exact OFFLINE context','new fixed fact_fixture COMPLETE','legacy original Gate route_fixture and fixed producer','new facts_entry explicit template/external-hash/policy; nested route+producer'],audit='MEMORY_OBSERVATION_ONLY; mismatch stops subsequent calls after original return',constructorGuard='FULL_ARGV/CWD/ENV/STREAMS/SOURCE_BEFORE_POPEN',maxConstructors=96))
print(json.dumps(dict(profile=sha(B/'reference/profile.json'),pins=len(pins))))
