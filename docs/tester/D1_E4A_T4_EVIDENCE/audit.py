"""Static identities and recorded binary-route evidence only. No CRT/fake/device rerun."""
from pathlib import Path
import hashlib,json,zipfile,datetime
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/binary-freeze.json';assert sha(seal)=='8eb3b4d82adaaba225eb22ee0afe90d551f9735a7518d1b34a7355927e4b2e67'
s=json.loads(seal.read_text());rows=s['immutable']
for row in rows:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
manifest=json.loads((R/s['manifest']['path']).read_text());expected={r['path']:r for r in manifest['files']}
with zipfile.ZipFile(R/s['sourceZip']['path']) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for name,row in expected.items():
  raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
for name in ['exact_process.py','command_response.py']:assert (B/'tools'/name).read_bytes()==(R/'docs/coder/d1e4at3/tools'/name).read_bytes()
assert sha(R/'docs/tester/D1_E4A_T3L_LOCALIZATION_REPORT_V1.0.md')=='7b017ed1f887b039ffa3ed55c6df5ada8257b1e75bbf9e88852ec0f557cf4150'
assert sha(R/'docs/coder/d1e4a/evidence/e4a-freeze.json')=='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
checks=json.loads((B/'evidence/local-check-results.json').read_text());assert checks['assertions']==len(checks['checks'])==41 and all(q['passed'] for q in checks['checks'])
assert len(checks['records'])==checks['actualLocalProcessCalls']==25 and all(q['ownership']=='RETURNED' and q['originalExitObserved'] and q['submittedBytes']==0 for q in checks['records'])
assert checks['crt']['text']['bytes']==26 and checks['crt']['binary']['bytes']==256 and all(q['closeReturn']==0 for q in checks['crt'].values())
assert checks['crt']['text']['sha256']==hashlib.sha256(bytes(range(26))).hexdigest() and checks['crt']['binary']['sha256']==hashlib.sha256(bytes(range(256))).hexdigest()
success=checks['cases'][0]['result'];assert success['metadataCommands']==9 and success['pushAttempts']==success['copyAttempts']==1
assert success['stageProof']['sha']==success['internalProof']['sha']=='40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880'
short=checks['cases'][1]['result'];assert short['status']=='NOT_ADMITTED' and short['pushAttempts']==1 and short['copyAttempts']==0
facts={'at':datetime.datetime.now().astimezone().isoformat(),'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'sourceZip':s['sourceZip'],'recordedAssertions':41,'recordedLocalProcessCalls':25,'recordedCrtResults':checks['crt'],'recordedCases':[{'case':q['case'],'status':q['result']['status'],'metadataCommands':q['result']['metadataCommands'],'pushAttempts':q['result']['pushAttempts'],'copyAttempts':q['result']['copyAttempts']} for q in checks['cases']],'T1PumpAndT3ResponseByteIdentical':True,'priorReportAndProductUnchanged':True,'pushAtomicNoReplace':'NOT_PROVIDED_ACCEPTED_ONLY_COOPERATIVE_SELF_256B_SCOPE','Android12DualViewAdmission':'UNKNOWN_DEVICE_NOT_RUN','installedSdkMappingAndDeviceCause':'UNKNOWN','testerCrtOrFakeRerun':False,'adbCalls':0,'deviceRuns':0,'realMediaReads':0,'gradleRuns':0,'inFlight':[]}
(E/'identity-and-recorded-binary-audit.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'recordedAssertions':41,'deviceRuns':0}))
