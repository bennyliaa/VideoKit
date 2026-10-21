"""One-time offline derivation from the frozen E13F; never touches device/custody roots."""
from pathlib import Path
import hashlib,json,shutil,difflib
B=Path(__file__).resolve().parents[1]; R=B.parents[2]; F=R/'docs/coder/d1e13f'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=sha(b))
def write(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record(fields):return ('{"e9":1,"fields":'+json.dumps(dict(sorted(fields.items())),separators=(',',':'))+'}\n').encode('ascii')
assert not (B/'evidence/prepared.json').exists(),'already prepared'
seal=F/'evidence/e13f-freeze.json'; old=json.loads(seal.read_text(encoding='utf-8'))
for row in old['immutableFiles']:
 assert pin(R/row['path'])==row,row['path']
assert pin(R/old['archive']['path'])==old['archive']
write(B/'evidence/prior-freeze-verification.json',dict(seal=pin(seal),archive=old['archive'],rows=len(old['immutableFiles']),allRowsUnchanged=True))
sources=sorted({row['source']['path'] for row in json.loads((F/'evidence/host-jar-manifest.json').read_text())['classes']})
derived=[]
for rel in sources:
 p=R/rel;q=B/p.relative_to(F);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);derived.append(dict(original=pin(p),current=q.relative_to(R).as_posix()))
observer=B/'tools/observe_original.ps1';shutil.copyfile(F/'tools/observe_original.ps1',observer)
refs=[
 'docs/tester/D1_AK_CONSOLIDATED_CLOSEOUT_REPORT_V1.0.md',
 'docs/tester/D1_UNRESOLVED_TASKS_CONSOLIDATED_DISPOSITION_V1.0.md',
 'docs/tester/D1_TABLET_CLOSEOUT_CONT_REPORT_V1.0.md',
 'docs/tester/D1_E13F_LIFECYCLE_REVIEW_REPORT_V1.0.md',
 'docs/milestones/D1_RESUME_AFTER_TABLET_CLOSEOUT_CODER_REQUIREMENTS_V1.0.md',
 'docs/milestones/D1_RESUME_AFTER_TABLET_CLOSEOUT_TESTER_REQUIREMENTS_V1.0.md']
assert pin(R/refs[2])['sha256']=='5d85e965029c8f923ad4bdffa4e5471bfa8d5e4e6c033b23de27fae40f61e354'
referenceRows=[]
for rel in refs:
 p=R/rel;q=B/'reference'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);referenceRows.append(dict(original=pin(p),snapshot=pin(q)))
for folder,key in [('D1_AK_CLOSEOUT_EVIDENCE','files'),('D1_TABLET_CLOSEOUT_CONT_EVIDENCE','items')]:
 source=R/'docs/tester'/folder;index=source/'evidence-index.json';data=json.loads(index.read_text(encoding='utf-8'))
 for row in data[key]:
  p=source/row['path'];raw=p.read_bytes();assert len(raw)==row['bytes'] and sha(raw)==row['sha256'],p
  q=B/'reference'/folder/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
 q=B/'reference'/folder/'evidence-index.json';shutil.copyfile(index,q)
write(B/'evidence/input-references.json',referenceRows)
write(B/'disposition/authorization.json',dict(kind='CAPTURED_COORDINATOR_DELEGATION',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',receivedDate='2026-10-20',scope='RESUME_AFTER_TABLET_CLOSEOUT_OFFLINE_ONLY',humanAuthorization='User requested continued development; standing human authorization permits coordinator project communication.',coordinatorInstruction='正式启动 RESUME_AFTER_TABLET_CLOSEOUT 开发批次；实现真实A/K+平板证据聚合、B/H行政UNKNOWN及新策略绑定；一次必要host构建、零Android构建；无设备/SDK/占用查询或产品测试。',deviceExecutionAuthorizedByThisRecord=False,reviewScope='Administrative disposition acceptance only; not independent review of this new source.'))
write(B/'disposition/administrative-review.json',dict(kind='CAPTURED_COORDINATOR_ADMINISTRATIVE_ACCEPTANCE',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',tabletReport=pin(B/'reference/D1_TABLET_CLOSEOUT_CONT_REPORT_V1.0.md'),accepted='OBSERVED_ALREADY_STOPPED is sufficient to end outstanding tablet supplementary force-stop requirement; do not repeat force-stop.',forceStopCalls=0,otherProjectForeground='com.lendmanager.app',freshM1RequiredBeforeDevice=True,originalAckReconstructed=False,independentSourceReview='PENDING'))
write(B/'disposition/case-evidence.json',dict(kind='ADMINISTRATIVE_TERMINATION_AND_OBSERVATION',A=dict(outcome='TERMINATED_WITHOUT_RETURN',originalJavaReturn=False,outerPowerShellNaturalExit=True,originalAdbAck='UNPROVEN'),K=dict(outcome='TERMINATED_WITHOUT_RETURN',originalJavaReturn=False,socketReaderAck='UNPROVEN'),tablet=dict(outcome='OBSERVED_ALREADY_STOPPED',stopped=True,relatedProcessObserved=False,activeInstrumentationObserved=False,forceStopCalls=0,stopAttribution='UNKNOWN_NOT_THIS_BATCH',otherProjectForeground='com.lendmanager.app'),reports=[pin(B/'reference'/Path(rel).name) for rel in [refs[0],refs[2]]],oldInternalAckReconstructed=False,oldLedgerRewritten=False,unknownRefunded=False))
write(B/'disposition/diagnostic-disposition.json',dict(kind='SEPARATE_ADMINISTRATIVE_UNKNOWN',B=dict(outcome='ADMINISTRATIVELY_QUARANTINED_UNKNOWN',originalReturn=False,actions=0),H=dict(outcome='ADMINISTRATIVELY_QUARANTINED_UNKNOWN',originalReturn=False,actions=0),K=dict(originalProtocolAck='UNPROVEN',budgetUnknown=True,allocated=189440,limit=262144,wireBytes=70656),basis=[pin(B/'reference'/Path(refs[1]).name),pin(B/'reference/D1_AK_CLOSEOUT_EVIDENCE/closeout-disposition-ledger.json')],unknownRefunded=False))
fields=dict(kind='e13ReviewedOriginalDisposition',originalScope='aeefe32f-816d-4c0b-aca7-16f76dbd45ff',serial='HA1Q6WXR',packages='com.videokit.app,com.videokit.app.test,com.videokit.e13.sender',outcome='TERMINATED_WITHOUT_RETURN',originalJavaReturn='false',caseEvidence=pin(B/'disposition/case-evidence.json')['sha256'],diagnosticDisposition=pin(B/'disposition/diagnostic-disposition.json')['sha256'],review=pin(B/'disposition/administrative-review.json')['sha256'],authorization=pin(B/'disposition/authorization.json')['sha256'])
disposition=B/'disposition/reviewed-original-disposition.json';disposition.write_bytes(record(fields));digest=pin(disposition)['sha256']
p=B/'tools/E13GuardLocation.java';t=p.read_text();assert t.count('DISPOSITION_SHA="ABSENT"')==1;t=t.replace('DISPOSITION_SHA="ABSENT"',f'DISPOSITION_SHA="{digest}"').replace('future disposition pin.','administrative disposition pin.');p.write_text(t,encoding='utf-8')
p=B/'tools/E13HostActivationSession.java';t=p.read_text();t=t.replace('Offline v17->v18 lifecycle candidate. Fixed custody disposition pin is ABSENT: no dispatch.','Reviewed-source v17->v19 deployment; single-method scope, fresh device authorization still required.')
t=t.replace('String.join(",",new TreeSet<>(E13Selection.METHODS))','"ordinarySenderCannotBindCodec"').replace('process51/text2097152','process43/text3145728')
p.write_text(t,encoding='utf-8')
p=B/'tools/E13HostCase.java';t=p.read_text().replace('if(!E13Selection.METHODS.contains(method))','if(!method.equals(s.get("methods")))')
p.write_text(t,encoding='utf-8')
p=B/'tools/E13PendingGuard.java';t=p.read_text();old='Path marker=root.resolve(old+".original-returned");'
assert t.count(old)==1
t=t.replace(old,'if(!method.equals("DEPLOY")){E9Record prior=E9Record.parse(Files.readAllBytes(claim),4096);if(prior.get("scope").equals(scope)&&prior.get("method").equals(method))throw new IOException("E13_CASE_ALREADY_ENTERED_NO_CHILD");}'+old)
p.write_text(t,encoding='utf-8')
write(B/'evidence/source-derivation.json',derived)
for row in derived:
 p=R/row['original']['path'];q=R/row['current']
 if p.read_bytes()!=q.read_bytes():
  out=B/'evidence/diffs'/q.relative_to(B);out=out.with_suffix(out.suffix+'.diff');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(''.join(difflib.unified_diff(p.read_text().splitlines(True),q.read_text().splitlines(True),fromfile=p.relative_to(R).as_posix(),tofile=q.relative_to(R).as_posix())),encoding='utf-8')
write(B/'evidence/prepared.json',dict(candidate='D1-20261020-RESUME01',productionSourceFiles=len(sources),sourceFilesChanged=4,disposition=pin(disposition),deviceCalls=0,originalCustodyRootAccesses=0,androidBuilds=0))
print(json.dumps(dict(status='PREPARED',sourceFiles=len(sources),disposition=pin(disposition))))
