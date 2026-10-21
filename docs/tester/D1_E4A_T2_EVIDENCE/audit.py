"""Read frozen identities and existing results only. No runner imports or test execution."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=B/'evidence/remote-freeze.json';assert sha(p)=='ce571e95cd294a46b2f852e2d07c7f91126d2b388eb6b27ddcc589e91010b09a'
s=json.loads(p.read_text());rows=s['immutable']
for row in rows:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
manifest=json.loads((R/s['manifest']['path']).read_text());expected={row['path']:row for row in manifest['files']}
with zipfile.ZipFile(R/s['sourceZip']['path']) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for n,row in expected.items():
  raw=z.read(n);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
assert sha(B/'tools/exact_process.py')==sha(R/'docs/coder/d1e4at1/tools/exact_process.py')=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
assert sha(R/'docs/tester/D1_E4A_T1P_PRELOAD_REPORT_V1.0.md')=='be7af9832fd8ab178dcab21efbc10fbde091507b4c84389c928e9954cc73511a'
assert sha(R/'docs/coder/d1e4a/evidence/e4a-freeze.json')=='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
checks=json.loads((B/'evidence/local-check-results.json').read_text());own=json.loads((R/checks['ownedResults']['path']).read_text());root=(R/checks['ownedResults']['path']).parent
assert own['assertions']==43 and own['callRecords']==len(own['records'])==32 and own['retainedLocalOwners']==0
assert all(q['ownership']=='RETURNED' and q['originalExitObserved'] for q in own['records'])
old=json.loads((root/'original-argv/trace-00.json').read_text());fixed=json.loads((root/'fixed-legacy-argv/trace-00.json').read_text());assert old['remoteShellExit']==127 and fixed['remoteShellExit']==0
assert not old['installedAdbExecuted'] and not fixed['installedAdbExecuted']
assert (B/'payload256.bin').read_bytes()==bytes(range(256))
facts={'at':datetime.datetime.now().astimezone().isoformat(),'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'sourceZip':s['sourceZip'],'existingAssertions':43,'existingDirectClientCalls':32,'diagnostics':[{'case':q['case'],'status':q['result']['status'],'metadataCommands':q['result']['metadataCommands'],'producerAttempts':q['result']['producerAttempts'],'priorRemoteOwnership':q['result']['priorRemoteOwnership']} for q in own['diagnostics']],'sourceModelRemote127':'LOCAL_MODEL_ONLY_NOT_DEVICE_OBSERVED','installedSdkCommitMapping':'UNKNOWN','old81407RootCause':'UNKNOWN','T1PumpByteIdentical':True,'priorReportAndProductUnchanged':True,'fakeRerun':False,'adbCalls':0,'realMediaReads':0,'deviceRuns':0,'gradleRuns':0,'inFlight':[]}
(E/'identity-and-recorded-model-audit.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'recordedAssertions':43,'recordedCalls':32}))
