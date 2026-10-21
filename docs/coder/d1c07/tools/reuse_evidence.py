"""Reuse proven unchanged local gates with exact C06 origins, not new runtime PASS."""
from pathlib import Path
import json,hashlib,shutil,sys
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c06';base=root/'docs/coder/d1c07';e=base/'evidence';rows=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['contract-probe.log','recovery-probe.log','validation-probe.log','control-probe.log','failure-probe.log','capture-probe.log','transfer-selfcheck.json','transfer-selfcheck.log','advisory-review.log','agp-task-source-excerpts.json','tool-vulnerability-review.json','TOOL_VULNERABILITY_REVIEW.md']
for p in (old/'evidence').rglob('*'):
 if p.is_file() and ('advisories' in p.parts or p.name in names or p.suffix=='.snapshot'):
  q=e/p.relative_to(old/'evidence');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows.append({'origin':p.relative_to(root).as_posix(),'copy':q.relative_to(root).as_posix(),'sha256':sha(p)})
checks={}
for directory,names in {'src':['OutputValidationRules','FencedTask','HostFixtures','CodecProbeState','FrameWindow','FrameCaptureRules','CaptureInputKind','RecoverySelfCheck','ValidationSelfCheck','C06ControlSelfCheck','C06FailureSelfCheck','C06CaptureSelfCheck','AsyncReadBridge','LeaseRegistry'],'android':['AndroidOutputValidator','AuthorizedSink','FdOutputMuxer','TombstoneWitness','VideoFrameSink','VideoCaptureOutputValidator','NativeFault','ExitEvidence']}.items():
 for name in names:
  p=next(old.rglob(name+'.java'));newName=name.replace('C06','C07');q=next(base.rglob(newName+'.java'))
  checks[name]=p.read_text(encoding='utf-8').replace('C06','C07').replace('c06','c07')==q.read_text(encoding='utf-8')
oldTest=next((old/'device').rglob('C06DeviceTests.java')).read_text(encoding='utf-8').replace('C06','C07').replace('c06','c07');newTest=next((base/'device').rglob('C07DeviceTests.java')).read_text(encoding='utf-8')
checks['host_formal_T01_T02_and_broker_SIGSEGV_HANG']=oldTest.split('@Test public void videoFrameCaptureMp4Control')[0]==newTest.split('@Test public void videoFrameCaptureMp4Control')[0]
p=next((old/'device').rglob('C06IsolatedDeviceTests.java'));q=next((base/'device').rglob('C07IsolatedDeviceTests.java'));checks['all_companion_and_ordinary_strict_source']=p.read_text(encoding='utf-8').replace('C06','C07').replace('c06','c07')==q.read_text(encoding='utf-8')
assert all(checks.values()),checks
result={'candidateId':'D1-20261005-C07','files':rows,'namespace_normalized_identity':checks,'rerun':False,'reuse_assertions':141,'scope':'C06 22 local capture assertions plus prior119 reused with original log IDs; not C07 device proof'}
(e/'c06-evidence-reuse.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(e/'gate-preservation.json').write_text(json.dumps({'status':'PASS_STATIC_ONLY','checks':checks,'formal_dual_track':'UNCHANGED','ordinary_history':'UNKNOWN=FAIL; method source retained, not scheduled for same-condition C07 rerun','device':'NOT_RUN'},indent=2),encoding='utf-8')
p=base/'tools/integrity.py';s=p.read_text(encoding='utf-8');s=s.replace("for folder,candidate in", "assert sha(root/'docs/coder/d1c06/evidence/freeze-summary.json')=='1fc7ef1b294c8e2dd11d3b547385bcec2875540bbc1428f939bfdbd198ae6f0d'\nfor folder,candidate in").replace("('d1c05','C05')]:","('d1c05','C05'),('d1c06','C06')]:").replace("('C03','C04','C05')", "('C03','C04','C05','C06')");p.write_text(s,encoding='utf-8')
p=base/'tools/freeze.py';s=p.read_text(encoding='utf-8').replace('C01/C02/C03/C04/C05','C01/C02/C03/C04/C05/C06').replace('docs/coder/D1_C07_DIAGNOSIS_AND_EXIT_REVIEW_V1.0.md','docs/coder/D1_SINGLE_APP_ISOLATION_OPTIONS_V1.0.md')
s=s.replace('C07 broker native SIGSEGV and independent hang, task-matched codec cause/FD release and actual AVI requested-time frame remain NOT_RUN; phone regressions pending; singleApp/Kit and model/decoder licensing blocked','C07 format guard real fixture/device regression NOT_RUN; ordinary historical UNKNOWN=FAIL retained without same-condition rerun; phone regressions, CPU route selection/admission and model rights remain blocked')
p.write_text(s,encoding='utf-8')
print('PASS unchanged gate identities',len(checks),'reused local assertions141')
