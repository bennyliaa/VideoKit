"""Read-only source/evidence analysis. Default verify writes nothing; explicit collect seals documents only."""
from pathlib import Path
import argparse,hashlib,json,zipfile,sys,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':sha(b)}
def external(p):b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':sha(b)}
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify(expected):
 p=E/'e13d-freeze.json'
 if not p.exists():return {'status':'NOT_FROZEN','writes':0},2
 if expected:assert pin(p)['sha256']==expected
 seal=json.loads(p.read_text(encoding='utf-8'));rows=seal['immutableFiles']
 assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for n,row in members.items():raw=z.read(n);assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
 inputs=json.loads((E/'input-verification.json').read_text())
 for group in inputs['frozenManifests']:
  check(group['manifest'])
  for row in json.loads((R/group['manifest']['path']).read_text(encoding='utf-8'))[group['rowKey']]:check(row)
 for row in inputs['reports']:check(row)
 for row in json.loads((E/'source-excerpts.json').read_text())['sources']:check(row['source'])
 return {'status':'PASS_E13D_OFFLINE_ANALYSIS_READONLY_VERIFY','writes':0,'archive':seal['archive'],'externalSeal':pin(p),'archiveEntries':len(members),'immutableRows':len(rows),'sourceFiles':len(json.loads((E/'source-excerpts.json').read_text())['sources']),'deviceCalls':0,'builds':0,'testRuns':0,'implementationChanges':0,'caseRootCause':'NOT_UNIQUELY_DETERMINED','D1':'NOT_PASSED','M0':'NOT_STARTED'},0
def collect():
 archive=R/'docs/coder/D1-20261018-E13D-offline-analysis.zip';sealpath=E/'e13d-freeze.json';assert not archive.exists() and not sealpath.exists()
 E.mkdir(parents=True,exist_ok=True)
 execution=R/'docs/tester/D1_E13C_TABLET_EXECUTION/aeefe32f-816d-4c0b-aca7-16f76dbd45ff'
 reports=[R/'docs/tester/D1_E13C_TABLET_EXECUTION_REPORT_V1.0.md',R/'docs/tester/D1_E13C_TABLET_EXECUTION_REPORT_V1.1.md']
 assert pin(reports[1])['sha256']=='77a21b4beeb77e11ce065af97e0548bdcebb86f6f0c3d0be2e7061ab950e2008'
 manifests=[]
 for path,key,expected in [
  (execution/'pending-snapshot-manifest.json','rows','c919618f135fe9f7a2b8d06e7a46c65dd024896bf88bf17d1c433b33545553d5'),
  (execution/'record-repair-manifest.json','rows',None),
  (R/'docs/coder/d1e13a/evidence/e13a-freeze.json','immutableFiles','24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6'),
  (R/'docs/coder/d1e13b/evidence/e13b-freeze.json','immutableFiles','e74a7cc615c4b1db78717e48f170e0248bf7445de059db7eacc2aaa4018c482e'),
  (R/'docs/coder/d1e13c/evidence/e13c-freeze.json','immutableFiles','14358fdb7e7900de669e76965c4ecce5b008eb8daea216b9abaa7f7891e45762')]:
  if expected:assert pin(path)['sha256']==expected
  rows=json.loads(path.read_text(encoding='utf-8'))[key]
  for row in rows:check(row)
  manifests.append({'manifest':pin(path),'rowKey':key,'rowsVerified':len(rows)})
 write(E/'input-verification.json',{'status':'PASS_FROZEN_INPUT_BYTES','reports':[pin(p) for p in reports],'frozenManifests':manifests,'liveLedgerRead':False,'mainCaseSessionRead':False,'currentDeviceStateRead':False,'note':'Only explicitly frozen manifests and delivered reports; no search for later live raw or outputs.'})
 A=R/'docs/coder/d1e13a'
 sources=[]
 for path,ranges in [
  ('app/src/androidTest/java/com/videokit/spike/e4/E13DeviceTests.java',[(9,27)]),
  ('app/src/androidTest/java/com/videokit/spike/e4/E13Instrumentation.java',[(1,15)]),
  ('android/com/videokit/spike/e4/E13PermissionProbe.java',[(9,52)]),
  ('fixture/src/main/java/com/videokit/e13/sender/SenderService.java',[(9,35)]),
  ('binding/com/videokit/spike/e4/E13BindingOwner.java',[(9,49)]),
  ('android/com/videokit/spike/e4/E4CodecService.java',[(40,70),(99,106)]),
  ('android/com/videokit/spike/e4/E4CodecWire.java',[(35,43)]),
  ('tools/E13HostCase.java',[(10,32)]),
  ('tools/E9PcSupervisor.java',[(17,18),(59,112),(156,176)]),
  ('src/com/videokit/spike/e4/E9CurrentObservation.java',[(11,40)]),
  ('android/com/videokit/spike/e4/E9AndroidFiles.java',[(18,65)]),
  ('android/com/videokit/spike/e4/E11ActivationLifetime.java',[(1,6)]),
  ('android/com/videokit/spike/e4/E4Session.java',[(19,54),(83,100)]),
  ('android/com/videokit/spike/c14/AndroidLease.java',[(1,18)]),
  ('src/com/videokit/spike/e4/E13SourceGroup.java',[(11,30),(84,94)]),
  ('app/src/debug/AndroidManifest.xml',[(1,9)]),
  ('fixture/src/main/AndroidManifest.xml',[(1,8)]),
  ('app/gradle.lockfile',[(17,24)])]:
  p=A/path;lines=p.read_text(encoding='utf-8-sig').splitlines();sources.append({'source':pin(p),'excerpts':[{'firstLine':a,'lastLine':min(b,len(lines)),'text':'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines))))} for a,b in ranges]})
 write(E/'source-excerpts.json',{'scope':'Frozen E13A source, E13C JAR retains E13HostCase/E9PcSupervisor exact members. No code execution.','sources':sources})
 cache=Path('C:/Users/benny/.gradle/caches/modules-2/files-2.1/androidx.test');deps=[]
 for module,version,digest,entry,ranges in [
  ('runner','1.7.0','98be1207f313bdf344a95ac60c576d578e36bc17','androidx/test/runner/AndroidJUnitRunner.java',[(445,477),(599,638)]),
  ('monitor','1.8.0','c901f94f9f176d3a922d88e1a24a3a16ac085ece','androidx/test/runner/MonitoringInstrumentation.java',[(349,379),(391,453),(717,745)])]:
  p=cache/module/version/digest/(module+'-'+version+'-sources.jar')
  with zipfile.ZipFile(p) as z:raw=z.read(entry)
  lines=raw.decode().splitlines();deps.append({'cachedArchive':external(p),'entry':entry,'entryBytes':len(raw),'entrySha256':sha(raw),'excerpts':[{'firstLine':a,'lastLine':b,'text':'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,b))} for a,b in ranges]})
 write(E/'cached-dependency-source-excerpts.json',{'networkRequests':0,'downloads':0,'versionAuthority':pin(A/'app/gradle.lockfile'),'scope':'Matching declared locked dependency source only; not vendor API31 thread evidence or a new runtime test','dependencies':deps})
 ps=execution/'pending-observation/01-processes-stdout.txt';lines=ps.read_text(encoding='utf-8').splitlines()
 matches=[{'line':i+1,'text':s} for i,s in enumerate(lines) if 'videokit' in s or any((' '+x+' ') in s for x in ['14763','14765','14779'])]
 write(E/'observation-boundaries.json',{'psRaw':pin(ps),'matchingLines':matches,'processNamesInThisSnapshot':['com.videokit.app'],'fixtureOrCodecProcessNameObserved':False,'absenceIsNotNeverStarted':True,'mainCase':'LAST_RECORDED_PENDING_NO_CURRENT_RECHECK','diagnostic':'LOST_DIAGNOSTIC_OWNER_UNKNOWN_SEPARATE','terminalRawAvailableInDeliveredReport':False,'hypothesesNotConfirmed':['pre-test main idle','before observation IO','positive binding or HELLO','fixture call/bind/unbind','one-shot finish refusal','PC reader/authority wait'],'provedStaticWindows':['D13-S01 no finish resumption wiring','D13-S02 sticky remote unknown without original query','D13-S03 local timers do not bound synchronous operations','D13-S04 late raw not forwarded after await deadline'],'newDiagnostics':'PROPOSAL_ONLY_NOT_AUTHORIZED_OR_EXECUTED','implementationChanges':0,'builds':0,'testRuns':0,'deviceCalls':0})
 files=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=sealpath]
 files += [R/'docs/coder/D1_E13D_OFFLINE_ROOT_CAUSE_AND_RECOVERY_V1.0.md',R/'docs/milestones/D1_E13D_CODER_REQUIREMENTS_V1.0.md',R/'docs/milestones/D1_E13D_TESTER_REQUIREMENTS_V1.0.md'];files=sorted(set(files));rows=[pin(p) for p in files]
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 write(sealpath,{'schema':1,'scope':'OFFLINE_ROOT_CAUSE_PROPOSALS_ONLY','archive':pin(archive),'immutableFiles':rows+[pin(archive)],'implementationChanges':0,'builds':0,'testRuns':0,'deviceCalls':0})
 before=[pin(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]+[pin(archive)];checks=[]
 for args in [[],['verify','--seal-sha',pin(sealpath)['sha256']],['--help']]:
  cmd=[sys.executable,'-X','utf8','-B',str(B/'tools/analysis_bundle.py'),*args];r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=60);checks.append({'argv':cmd,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,r.stderr
 after=[pin(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]+[pin(archive)];assert before==after
 result={'status':'PASS_E13D_OFFLINE_ANALYSIS_FINAL_READONLY_VERIFICATION','archive':pin(archive),'externalSeal':pin(sealpath),'archiveEntries':len(files),'immutableRows':len(rows)+1,'readOnlyFilesBeforeAfter':len(before),'verifications':checks,'caseRootCause':'NOT_UNIQUELY_DETERMINED','implementationChanges':0,'builds':0,'testRuns':0,'deviceCalls':0}
 write(R/'docs/coder/D1_E13D_FINAL_READONLY_VERIFICATION_V1.0.json',result);print(json.dumps({k:v for k,v in result.items() if k!='verifications'}))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','collect'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='collect':
  if a.seal_sha:p.error('--seal-sha is verification-only')
  collect();return
 result,code=verify(a.seal_sha);print(json.dumps(result));raise SystemExit(code)
if __name__=='__main__':main()
