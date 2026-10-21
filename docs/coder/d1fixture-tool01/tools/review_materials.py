from pathlib import Path
import json,hashlib,zipfile,sys,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2]
assert len(sys.argv)==3 and sys.argv[1]=='--output','USAGE_--output_NEW_ABSOLUTE_REVIEW_CHILD'
root=R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE';raw=Path(sys.argv[2]);assert raw.is_absolute(),'ABSOLUTE_PATH_REQUIRED'
D=raw.resolve();assert root.resolve()==root and D.is_relative_to(root) and D!=root,'EXACT_NEW_REVIEW_ROOT_ONLY';assert not D.exists(),'EXISTING_OUTPUT_REJECTED'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/fixture-tool01-freeze.json';frozen=json.loads(seal.read_text())
assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in frozen['files'])
jar=B/'artifacts/videokit-fixture-tool01.jar';audit=json.loads((B/'evidence/jar-audit.json').read_text());assert sha(jar)==audit['sha256']
origins=json.loads((B/'evidence/jar-class-origin.json').read_text());assert len(origins)==982
with zipfile.ZipFile(jar) as z:
 assert z.testzip() is None and {i.filename for i in z.infolist() if not i.is_dir()}==set(audit['files'])
 for x in origins:
  p=B/x['actualCompilerOutputPath'];assert sha(p)==x['sha256'] and z.read(x['jarEntry'])==p.read_bytes() and sha(B/x['sourcePath'])==x['sourceSha256']
old=0
for x in json.loads((B/'evidence/prior-frozen-preservation.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sha256'];v=json.loads(p.read_text())
 assert all(sha(R/y['path'])==y['sha256'] for y in v['files']);old+=len(v['files'])
assert old==6972
for x in json.loads((B/'evidence/prior-independent-preservation.json').read_text()):
 p=R/x['path'];assert sha(p)==x['sha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/y['path'])==y['sha256'] for y in m['evidenceFiles'])
result={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate':'D1_FIXTURE_TOOL01_BUILD','sealSha256':sha(seal),'frozenFilesUnchanged':len(frozen['files']),'toolJarSha256':sha(jar),'actualCompilerClassBytesMatched':982,'oldFrozenFilesUnchanged':old,'check':'PYTHON_READ_ONLY_MATERIAL_AUDIT_NOT_FUNCTIONAL_OR_INDEPENDENT_VERDICT','newCompilerJarOrJavaCalls':0,'runtimeMainOrEncoderInitialization':0,'oldOwnerPollAttachIntervention':0,'newMediaOrDeviceOperations':0,'generationAuthorized':False,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
D.mkdir(parents=True,exist_ok=False);(D/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
