from pathlib import Path
import json,hashlib,zipfile,datetime,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
assert len(sys.argv)==3 and sys.argv[1]=='--output','NEW_ABSOLUTE_OUTPUT_REQUIRED'
root=R/'docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE';raw=Path(sys.argv[2]);assert raw.is_absolute(),'ABSOLUTE_ONLY';D=raw.resolve()
assert root.resolve()==root and D.is_relative_to(root) and D!=root and not D.exists(),'EXACT_NEW_REVIEW_CHILD_ONLY'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=E/'fixture-tool02-freeze.json';f=json.loads(seal.read_text());assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in f['files'])
jar=B/'artifacts/videokit-fixture-tool02.jar';audit=json.loads((E/'jar-audit02.json').read_text());assert sha(jar)==audit['sha256']
origins=json.loads((E/'class-origin02.json').read_text());assert len(origins)==990
with zipfile.ZipFile(jar) as z:
 assert z.testzip() is None and {i.filename for i in z.infolist() if not i.is_dir()}==set(audit['jarFileNames'])
 for x in origins:
  assert sha(B/x['actualCompilerOutput'])==x['sha256']==sha(B/x['packageCopy']) and sha(B/x['sourcePath'])==x['sourceSha256']
  if not x['testOnly']:assert hashlib.sha256(z.read(x['jarEntry'])).hexdigest()==x['sha256']
old=0
for x in json.loads((E/'prior-frozen02.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sha256'];v=json.loads(p.read_text());assert all(sha(R/y['path'])==y['sha256'] for y in v['files']);old+=len(v['files'])
assert old==8725
v=json.loads((E/'prior-independent02.json').read_text());p=R/v['manifestPath'];assert sha(p)==v['sha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/y['path'])==y['sha256'] for y in m['evidenceFiles'])
c=json.loads((E/'nonmedia-001/summary.json').read_text());assert c['totalExecutedGroups']==58 and c['allOriginalProcessesReturned']
receipt={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sealSha256':sha(seal),'frozenFilesUnchanged':len(f['files']),'oldFrozenFilesUnchanged':old,'toolJarSha256':sha(jar),'actualCompilerClassesBytesMatched':990,'productionClasses':985,'testClassesExcluded':5,'recordedCoderNonmediaGroups':58,'recordedCoderOriginalReturns':2,'newRuntimeOrCompilerCallsInThisMaterialAudit':0,'generationMainJobEncoderMuxerOrMediaRun':0,'oldOwnerQueryOrIntervention':0,'independentP2Closure':'NOT_IMPLIED','D1':'NOT_PASSED','M0':'NOT_STARTED'}
D.mkdir(parents=True,exist_ok=False);(D/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False,indent=2))
